"""
Jolpica F1 adapter.

Normalizes the Jolpica F1 API (Ergast-compatible; see
https://github.com/jolpica/jolpica-f1) into the canonical schema defined
in DataPipeline/schema/canonical.py, per MASTER_ARCHITECTURE.md section 29.

Scope (Phase 1, per the approved plan): drivers, constructors, circuits,
season schedule + session metadata, race results, laps, pit stops.
Deliberately NOT covered: qualifying results, sprint results, standings --
Jolpica supports these but they weren't asked for yet, so they're not
fetched (avoiding scope creep past what was approved). Tyres and weather
have no Jolpica data at all; those canonical types exist but stay
unpopulated until a FastF1/OpenF1 adapter is added.

Usage terms: this project calls the jolpica-f1 API subject to its Terms
of Use (https://github.com/jolpica/jolpica-f1/blob/main/TERMS.md).
Review those terms before this data ships in any public build.
"""

from __future__ import annotations

from typing import Any, Iterator, List, Tuple

import requests

from DataPipeline.schema.canonical import (
    CanonicalCircuit,
    CanonicalConstructor,
    CanonicalDriver,
    CanonicalLap,
    CanonicalPitStop,
    CanonicalRace,
    CanonicalRaceResult,
    CanonicalSession,
    SessionType,
    build_race_id,
)

BASE_URL = "https://api.jolpi.ca/ergast/f1"
DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_PAGE_SIZE = 100  # Jolpica's documented per-request max

# Ergast/Jolpica race-schedule keys that carry a nested {date, time} block
# for a sub-session, mapped to our SessionType. Ergast has used both
# "SprintQualifying" and "SprintShootout" for the same session across
# different seasons/formats, so both map to the same canonical type.
_SESSION_KEY_MAP = {
    "FirstPractice": SessionType.FP1,
    "SecondPractice": SessionType.FP2,
    "ThirdPractice": SessionType.FP3,
    "SprintQualifying": SessionType.SPRINT_QUALIFYING,
    "SprintShootout": SessionType.SPRINT_QUALIFYING,
    "Sprint": SessionType.SPRINT,
    "Qualifying": SessionType.QUALIFYING,
}


def _parse_time_to_millis(time_str: str) -> int:
    """Parses Ergast/Jolpica lap-time / pit-stop-duration strings.

    Handles both 'M:SS.mmm' (e.g. lap times, '1:35.123') and plain
    'SS.mmm' (e.g. most pit stop durations, '2.345').
    """
    if ":" in time_str:
        minutes_str, rest = time_str.split(":", 1)
        minutes = int(minutes_str)
    else:
        minutes = 0
        rest = time_str
    seconds = float(rest)
    return int(minutes * 60_000 + round(seconds * 1000))


class JolpicaAdapter:
    """Adapter for the Jolpica F1 (Ergast-compatible) API.

    All adapters -- Jolpica, and FastF1/OpenF1/F1DB as they get added --
    must output the canonical types from DataPipeline.schema.canonical.
    The canonical schema is the only thing the rest of the pipeline (and
    eventually the C# simulation) should ever depend on.
    """

    def __init__(self, base_url: str = BASE_URL, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _fetch_all_pages(self, url: str, page_size: int = DEFAULT_PAGE_SIZE) -> Iterator[dict]:
        """Yields raw MRData payloads across every page of a limit/offset
        paginated Jolpica endpoint. Works unmodified for small endpoints
        too (drivers/constructors/circuits) -- the loop just runs once."""
        offset = 0
        while True:
            response = requests.get(
                url, params={"limit": page_size, "offset": offset}, timeout=self.timeout
            )
            response.raise_for_status()
            payload = response.json()
            yield payload

            total = int(payload["MRData"].get("total", 0))
            offset += page_size
            if offset >= total:
                break

    # ---- reference data -------------------------------------------------

    def get_drivers(self, season: int) -> List[CanonicalDriver]:
        url = f"{self.base_url}/{season}/drivers.json"
        drivers: List[CanonicalDriver] = []
        for payload in self._fetch_all_pages(url):
            for entry in payload["MRData"]["DriverTable"]["Drivers"]:
                drivers.append(
                    CanonicalDriver(
                        driver_id=entry["driverId"],
                        code=entry.get("code"),
                        permanent_number=(
                            int(entry["permanentNumber"]) if entry.get("permanentNumber") else None
                        ),
                        given_name=entry["givenName"],
                        family_name=entry["familyName"],
                        date_of_birth=entry.get("dateOfBirth"),
                        nationality=entry.get("nationality"),
                    )
                )
        return drivers

    def get_constructors(self, season: int) -> List[CanonicalConstructor]:
        url = f"{self.base_url}/{season}/constructors.json"
        constructors: List[CanonicalConstructor] = []
        for payload in self._fetch_all_pages(url):
            for entry in payload["MRData"]["ConstructorTable"]["Constructors"]:
                constructors.append(
                    CanonicalConstructor(
                        constructor_id=entry["constructorId"],
                        name=entry["name"],
                        nationality=entry.get("nationality"),
                    )
                )
        return constructors

    def get_circuits(self, season: int) -> List[CanonicalCircuit]:
        url = f"{self.base_url}/{season}/circuits.json"
        circuits: List[CanonicalCircuit] = []
        for payload in self._fetch_all_pages(url):
            for entry in payload["MRData"]["CircuitTable"]["Circuits"]:
                location = entry.get("Location", {})
                circuits.append(
                    CanonicalCircuit(
                        circuit_id=entry["circuitId"],
                        name=entry["circuitName"],
                        locality=location.get("locality"),
                        country=location.get("country"),
                        latitude=float(location["lat"]) if location.get("lat") else None,
                        longitude=float(location["long"]) if location.get("long") else None,
                    )
                )
        return circuits

    # ---- races + sessions -------------------------------------------------

    def get_season_schedule(self, season: int) -> Tuple[List[CanonicalRace], List[CanonicalSession]]:
        """Returns (races, sessions) for a season. Session sub-objects
        present in the source payload vary by race format (sprint
        weekends carry extra keys) -- only the ones actually present get
        turned into CanonicalSession rows."""
        url = f"{self.base_url}/{season}/races.json"
        races: List[CanonicalRace] = []
        sessions: List[CanonicalSession] = []
        for payload in self._fetch_all_pages(url):
            for entry in payload["MRData"]["RaceTable"]["Races"]:
                race_season = int(entry["season"])
                race_round = int(entry["round"])
                race_id = build_race_id(race_season, race_round)

                races.append(
                    CanonicalRace(
                        race_id=race_id,
                        season=race_season,
                        round=race_round,
                        name=entry["raceName"],
                        circuit_id=entry["Circuit"]["circuitId"],
                        date=entry["date"],
                    )
                )

                sessions.append(
                    CanonicalSession(
                        race_id=race_id,
                        session_type=SessionType.RACE,
                        session_date=entry.get("date"),
                        time_utc=entry.get("time"),
                    )
                )
                for source_key, session_type in _SESSION_KEY_MAP.items():
                    block = entry.get(source_key)
                    if block:
                        sessions.append(
                            CanonicalSession(
                                race_id=race_id,
                                session_type=session_type,
                                session_date=block.get("date"),
                                time_utc=block.get("time"),
                            )
                        )
        return races, sessions

    # ---- per-race data -------------------------------------------------

    def get_race_results(self, season: int, round_: int) -> List[CanonicalRaceResult]:
        """Fetch and normalize the results of a single race.

        Returns results only (joined to a race via race_id) -- race
        metadata itself comes from get_season_schedule, so it isn't
        duplicated here.
        """
        race_id = build_race_id(season, round_)
        url = f"{self.base_url}/{season}/{round_}/results.json"
        results: List[CanonicalRaceResult] = []
        for payload in self._fetch_all_pages(url):
            races = payload["MRData"]["RaceTable"]["Races"]
            if not races:
                raise ValueError("Jolpica returned no races for that season/round")
            for entry in races[0].get("Results", []):
                time_block = entry.get("Time") or {}
                millis = time_block.get("millis")
                fastest_lap = entry.get("FastestLap") or {}
                fastest_lap_time = (fastest_lap.get("Time") or {}).get("time")
                results.append(
                    CanonicalRaceResult(
                        race_id=race_id,
                        driver_id=entry["Driver"]["driverId"],
                        constructor_id=entry["Constructor"]["constructorId"],
                        position=int(entry["position"]) if entry.get("position") else None,
                        points=float(entry.get("points", 0)),
                        grid=int(entry.get("grid", 0)),
                        laps_completed=int(entry.get("laps", 0)),
                        status=entry.get("status", "Unknown"),
                        time_millis=int(millis) if millis else None,
                        fastest_lap_rank=(
                            int(fastest_lap["rank"]) if fastest_lap.get("rank") else None
                        ),
                        fastest_lap_time_millis=(
                            _parse_time_to_millis(fastest_lap_time) if fastest_lap_time else None
                        ),
                    )
                )
        return results

    def get_laps(self, season: int, round_: int) -> List[CanonicalLap]:
        """Fetch every lap time for every driver in a race. Paginates --
        a full race is ~20 drivers x ~60-70 laps, well past the API's
        100-row page size."""
        race_id = build_race_id(season, round_)
        url = f"{self.base_url}/{season}/{round_}/laps.json"
        laps: List[CanonicalLap] = []
        for payload in self._fetch_all_pages(url):
            races = payload["MRData"]["RaceTable"]["Races"]
            if not races:
                continue
            for lap_entry in races[0].get("Laps", []):
                lap_number = int(lap_entry["number"])
                for timing in lap_entry.get("Timings", []):
                    laps.append(
                        CanonicalLap(
                            race_id=race_id,
                            driver_id=timing["driverId"],
                            lap_number=lap_number,
                            position=int(timing["position"]),
                            time_millis=_parse_time_to_millis(timing["time"]),
                        )
                    )
        return laps

    def get_pit_stops(self, season: int, round_: int) -> List[CanonicalPitStop]:
        race_id = build_race_id(season, round_)
        url = f"{self.base_url}/{season}/{round_}/pitstops.json"
        stops: List[CanonicalPitStop] = []
        for payload in self._fetch_all_pages(url):
            races = payload["MRData"]["RaceTable"]["Races"]
            if not races:
                continue
            for entry in races[0].get("PitStops", []):
                duration_str = entry.get("duration")
                stops.append(
                    CanonicalPitStop(
                        race_id=race_id,
                        driver_id=entry["driverId"],
                        stop_number=int(entry["stop"]),
                        lap_number=int(entry["lap"]),
                        time_of_day=entry.get("time"),
                        duration_millis=(
                            _parse_time_to_millis(duration_str) if duration_str else None
                        ),
                    )
                )
        return stops


if __name__ == "__main__":
    # Manual live-connectivity check -- deliberately NOT part of the
    # automated test suite. The sandbox this was built in blocks
    # outbound calls to api.jolpi.ca by network policy; your machine
    # and GitHub Actions should not have that restriction. Run this
    # file directly to confirm live connectivity:
    #     python -m DataPipeline.sources.jolpica_adapter
    adapter = JolpicaAdapter()
    results = adapter.get_race_results(2024, 1)
    print(f"2024 round 1: {len(results)} results")
    for r in results[:3]:
        print(f"  P{r.position} {r.driver_id} ({r.constructor_id}) - {r.points} pts")
