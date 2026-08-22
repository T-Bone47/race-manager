"""
Jolpica F1 adapter.

Normalizes the Jolpica F1 API (Ergast-compatible; see
https://github.com/jolpica/jolpica-f1) into this project's internal
canonical schema, per MASTER_ARCHITECTURE.md section 29.

Scope note: this is a Phase 0/1 starter. It covers exactly one endpoint
(race results) end to end, to prove the adapter pattern before more
sources or endpoints get added -- consistent with section 4's "do not
keep adding sources unless a specific missing capability is
demonstrated". Season/driver/circuit/lap adapters follow the same
shape and get added as real Phase 1 needs show up.

Usage terms: this project calls the jolpica-f1 API subject to its
Terms of Use (https://github.com/jolpica/jolpica-f1/blob/main/TERMS.md).
Review those terms before this data ships in any public build.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"
DEFAULT_TIMEOUT_SECONDS = 10


@dataclass
class CanonicalRaceResult:
    """One driver's canonical result for a single race.

    Field names are ours, not Jolpica's/Ergast's -- nothing outside
    DataPipeline/sources should ever see the source's own field names
    (MASTER_ARCHITECTURE.md section 29).
    """

    driver_id: str
    constructor_id: str
    position: Optional[int]
    points: float
    grid: int
    laps: int
    status: str
    time_millis: Optional[int]


@dataclass
class CanonicalRace:
    """A single race, normalized into our internal schema."""

    season: int
    round: int
    race_name: str
    race_date: str
    results: list = field(default_factory=list)


class JolpicaAdapter:
    """Adapter for the Jolpica F1 (Ergast-compatible) API.

    All adapters -- Jolpica, and FastF1/OpenF1/F1DB/Kaggle as they get
    added -- must output canonical types like the ones above. The
    canonical schema is the only thing the rest of the pipeline (and
    eventually the C# simulation) should ever depend on.
    """

    def __init__(self, base_url: str = BASE_URL, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_race_results(self, season: int, round_: int) -> CanonicalRace:
        """Fetch and normalize the results of a single race."""
        url = f"{self.base_url}/{season}/{round_}/results.json"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return self._normalize_race_results(response.json())

    @staticmethod
    def _normalize_race_results(payload: dict) -> CanonicalRace:
        races = payload["MRData"]["RaceTable"]["Races"]
        if not races:
            raise ValueError("Jolpica returned no races for that season/round")
        race = races[0]

        results = []
        for entry in race.get("Results", []):
            time_block = entry.get("Time") or {}
            millis = time_block.get("millis")
            results.append(
                CanonicalRaceResult(
                    driver_id=entry["Driver"]["driverId"],
                    constructor_id=entry["Constructor"]["constructorId"],
                    position=int(entry["position"]) if entry.get("position") else None,
                    points=float(entry.get("points", 0)),
                    grid=int(entry.get("grid", 0)),
                    laps=int(entry.get("laps", 0)),
                    status=entry.get("status", "Unknown"),
                    time_millis=int(millis) if millis else None,
                )
            )

        return CanonicalRace(
            season=int(race["season"]),
            round=int(race["round"]),
            race_name=race.get("raceName", ""),
            race_date=race.get("date", ""),
            results=results,
        )


if __name__ == "__main__":
    # Manual live-connectivity check -- deliberately NOT part of the
    # automated test suite. The sandbox this was scaffolded in blocks
    # outbound calls to api.jolpi.ca by network policy; your machine
    # and GitHub Actions should not have that restriction. Run this
    # file directly to confirm live connectivity:
    #     python -m DataPipeline.sources.jolpica_adapter
    adapter = JolpicaAdapter()
    race = adapter.get_race_results(2024, 1)
    print(f"{race.race_name} ({race.season} round {race.round}): {len(race.results)} results")
    for r in race.results[:3]:
        print(f"  P{r.position} {r.driver_id} ({r.constructor_id}) - {r.points} pts")
