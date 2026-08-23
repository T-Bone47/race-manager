"""
Tests for JolpicaAdapter.

All fully offline: every HTTP call is mocked, so these pass in any
environment -- including sandboxes with restricted network egress -- and
never depend on Jolpica's API actually being reachable or up.
"""

from unittest.mock import MagicMock, patch

import pytest

from DataPipeline.sources.jolpica_adapter import JolpicaAdapter, _parse_time_to_millis


def _mock_response(payload):
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def _patched_get(*payloads):
    return patch(
        "DataPipeline.sources.jolpica_adapter.requests.get",
        side_effect=[_mock_response(p) for p in payloads],
    )


# ---- time parsing -----------------------------------------------------

def test_parse_time_to_millis_minutes_seconds():
    assert _parse_time_to_millis("1:35.123") == 95123


def test_parse_time_to_millis_seconds_only():
    assert _parse_time_to_millis("23.145") == 23145


# ---- drivers -----------------------------------------------------------

DRIVERS_PAYLOAD = {
    "MRData": {
        "total": "2",
        "DriverTable": {
            "Drivers": [
                {
                    "driverId": "max_verstappen",
                    "permanentNumber": "33",
                    "code": "VER",
                    "givenName": "Max",
                    "familyName": "Verstappen",
                    "dateOfBirth": "1997-09-30",
                    "nationality": "Dutch",
                },
                {
                    # deliberately missing code/permanentNumber, like many
                    # historical drivers in Jolpica's older seasons
                    "driverId": "farina",
                    "givenName": "Nino",
                    "familyName": "Farina",
                    "nationality": "Italian",
                },
            ]
        },
    }
}


def test_get_drivers_normalizes_to_canonical_shape():
    adapter = JolpicaAdapter()
    with _patched_get(DRIVERS_PAYLOAD):
        drivers = adapter.get_drivers(2024)

    assert len(drivers) == 2
    assert drivers[0].driver_id == "max_verstappen"
    assert drivers[0].code == "VER"
    assert drivers[0].permanent_number == 33

    # missing optional fields become None, not KeyErrors
    assert drivers[1].code is None
    assert drivers[1].permanent_number is None
    assert drivers[1].family_name == "Farina"


def test_get_drivers_requests_the_correct_url():
    adapter = JolpicaAdapter()
    with _patched_get(DRIVERS_PAYLOAD) as mock_get:
        adapter.get_drivers(2024)
    called_url = mock_get.call_args[0][0]
    assert called_url == "https://api.jolpi.ca/ergast/f1/2024/drivers.json"


# ---- constructors -------------------------------------------------------

def test_get_constructors_normalizes_to_canonical_shape():
    payload = {
        "MRData": {
            "total": "2",
            "ConstructorTable": {
                "Constructors": [
                    {"constructorId": "red_bull", "name": "Red Bull", "nationality": "Austrian"},
                    {"constructorId": "mercedes", "name": "Mercedes", "nationality": "German"},
                ]
            },
        }
    }
    adapter = JolpicaAdapter()
    with _patched_get(payload):
        constructors = adapter.get_constructors(2024)

    assert len(constructors) == 2
    assert constructors[0].constructor_id == "red_bull"
    assert constructors[0].name == "Red Bull"


# ---- circuits -----------------------------------------------------------

def test_get_circuits_normalizes_to_canonical_shape():
    payload = {
        "MRData": {
            "total": "1",
            "CircuitTable": {
                "Circuits": [
                    {
                        "circuitId": "bahrain",
                        "circuitName": "Bahrain International Circuit",
                        "Location": {
                            "lat": "26.0325",
                            "long": "50.5106",
                            "locality": "Sakhir",
                            "country": "Bahrain",
                        },
                    }
                ]
            },
        }
    }
    adapter = JolpicaAdapter()
    with _patched_get(payload):
        circuits = adapter.get_circuits(2024)

    assert len(circuits) == 1
    circuit = circuits[0]
    assert circuit.circuit_id == "bahrain"
    assert circuit.country == "Bahrain"
    assert circuit.latitude == pytest.approx(26.0325)
    assert circuit.longitude == pytest.approx(50.5106)


# ---- season schedule + sessions -----------------------------------------

SCHEDULE_PAYLOAD = {
    "MRData": {
        "total": "1",
        "RaceTable": {
            "Races": [
                {
                    "season": "2024",
                    "round": "1",
                    "raceName": "Bahrain Grand Prix",
                    "Circuit": {"circuitId": "bahrain"},
                    "date": "2024-03-02",
                    "time": "15:00:00Z",
                    "FirstPractice": {"date": "2024-02-29", "time": "11:30:00Z"},
                    "SecondPractice": {"date": "2024-02-29", "time": "15:00:00Z"},
                    "ThirdPractice": {"date": "2024-03-01", "time": "11:30:00Z"},
                    "Qualifying": {"date": "2024-03-01", "time": "15:00:00Z"},
                }
            ]
        },
    }
}


def test_get_season_schedule_normalizes_races_and_sessions():
    adapter = JolpicaAdapter()
    with _patched_get(SCHEDULE_PAYLOAD):
        races, sessions = adapter.get_season_schedule(2024)

    assert len(races) == 1
    race = races[0]
    assert race.race_id == "2024_1"
    assert race.season == 2024
    assert race.round == 1
    assert race.circuit_id == "bahrain"

    # RACE + FP1 + FP2 + FP3 + Q = 5 sessions; no Sprint block in this fixture
    session_types = {s.session_type.value for s in sessions}
    assert session_types == {"RACE", "FP1", "FP2", "FP3", "Q"}
    assert all(s.race_id == "2024_1" for s in sessions)


def test_get_season_schedule_omits_sessions_not_present_in_source():
    # A weekend with no practice sessions listed (e.g. a truncated fixture)
    # must not fabricate FP1/FP2/FP3 rows that don't exist in the source.
    payload = {
        "MRData": {
            "total": "1",
            "RaceTable": {
                "Races": [
                    {
                        "season": "2024",
                        "round": "5",
                        "raceName": "Chinese Grand Prix",
                        "Circuit": {"circuitId": "shanghai"},
                        "date": "2024-04-21",
                    }
                ]
            },
        }
    }
    adapter = JolpicaAdapter()
    with _patched_get(payload):
        _, sessions = adapter.get_season_schedule(2024)

    assert {s.session_type.value for s in sessions} == {"RACE"}


# ---- race results ---------------------------------------------------------

RESULTS_PAYLOAD = {
    "MRData": {
        "total": "2",
        "RaceTable": {
            "Races": [
                {
                    "season": "2024",
                    "round": "1",
                    "raceName": "Bahrain Grand Prix",
                    "date": "2024-03-02",
                    "Results": [
                        {
                            "position": "1",
                            "points": "25",
                            "grid": "1",
                            "laps": "57",
                            "status": "Finished",
                            "Driver": {"driverId": "max_verstappen"},
                            "Constructor": {"constructorId": "red_bull"},
                            "Time": {"millis": "5058286", "time": "1:31:44.742"},
                            "FastestLap": {"rank": "1", "Time": {"time": "1:32.608"}},
                        },
                        {
                            "position": "2",
                            "points": "18",
                            "grid": "5",
                            "laps": "57",
                            "status": "Finished",
                            "Driver": {"driverId": "sergio_perez"},
                            "Constructor": {"constructorId": "red_bull"},
                            "Time": {"millis": "5081378"},
                        },
                    ],
                }
            ]
        },
    }
}


def test_get_race_results_normalizes_to_canonical_shape():
    adapter = JolpicaAdapter()
    with _patched_get(RESULTS_PAYLOAD):
        results = adapter.get_race_results(2024, 1)

    assert len(results) == 2
    winner = results[0]
    assert winner.race_id == "2024_1"
    assert winner.driver_id == "max_verstappen"
    assert winner.position == 1
    assert winner.points == 25.0
    assert winner.time_millis == 5058286
    assert winner.fastest_lap_rank == 1
    assert winner.fastest_lap_time_millis == 92608  # 1:32.608

    runner_up = results[1]
    assert runner_up.driver_id == "sergio_perez"
    assert runner_up.fastest_lap_rank is None


def test_get_race_results_requests_the_correct_url():
    adapter = JolpicaAdapter()
    with _patched_get(RESULTS_PAYLOAD) as mock_get:
        adapter.get_race_results(2024, 1)
    called_url = mock_get.call_args[0][0]
    assert called_url == "https://api.jolpi.ca/ergast/f1/2024/1/results.json"


def test_get_race_results_no_races_raises():
    empty_payload = {"MRData": {"total": "0", "RaceTable": {"Races": []}}}
    adapter = JolpicaAdapter()
    with _patched_get(empty_payload):
        with pytest.raises(ValueError):
            adapter.get_race_results(2024, 99)


# ---- laps (pagination) ---------------------------------------------------

def test_get_laps_paginates_across_multiple_pages():
    # total (150) deliberately exceeds one page (100) so the adapter is
    # forced to make a second request and aggregate both.
    page1 = {
        "MRData": {
            "total": "150",
            "RaceTable": {
                "Races": [
                    {
                        "season": "2024",
                        "round": "1",
                        "Laps": [
                            {
                                "number": "1",
                                "Timings": [
                                    {"driverId": "max_verstappen", "position": "1", "time": "1:35.123"}
                                ],
                            }
                        ],
                    }
                ]
            },
        }
    }
    page2 = {
        "MRData": {
            "total": "150",
            "RaceTable": {
                "Races": [
                    {
                        "season": "2024",
                        "round": "1",
                        "Laps": [
                            {
                                "number": "2",
                                "Timings": [
                                    {"driverId": "max_verstappen", "position": "1", "time": "1:34.456"}
                                ],
                            }
                        ],
                    }
                ]
            },
        }
    }
    adapter = JolpicaAdapter()
    with _patched_get(page1, page2) as mock_get:
        laps = adapter.get_laps(2024, 1)

    assert mock_get.call_count == 2
    assert len(laps) == 2
    assert laps[0].lap_number == 1
    assert laps[0].time_millis == 95123
    assert laps[1].lap_number == 2
    assert laps[1].race_id == "2024_1"


# ---- pit stops -------------------------------------------------------------

def test_get_pit_stops_normalizes_to_canonical_shape():
    payload = {
        "MRData": {
            "total": "2",
            "RaceTable": {
                "Races": [
                    {
                        "season": "2024",
                        "round": "1",
                        "PitStops": [
                            {
                                "driverId": "max_verstappen",
                                "lap": "12",
                                "stop": "1",
                                "time": "14:23:15",
                                "duration": "2.345",
                            },
                            {
                                "driverId": "sergio_perez",
                                "lap": "15",
                                "stop": "1",
                                "time": "14:30:02",
                                "duration": "23.145",
                            },
                        ],
                    }
                ]
            },
        }
    }
    adapter = JolpicaAdapter()
    with _patched_get(payload):
        stops = adapter.get_pit_stops(2024, 1)

    assert len(stops) == 2
    first = stops[0]
    assert first.race_id == "2024_1"
    assert first.driver_id == "max_verstappen"
    assert first.duration_millis == 2345
    assert stops[1].duration_millis == 23145
