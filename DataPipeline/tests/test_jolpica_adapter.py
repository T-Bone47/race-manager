"""
Smoke test for JolpicaAdapter.

Runs fully offline: mocks the HTTP call so it passes in any
environment -- including sandboxes with restricted network egress --
and never depends on Jolpica's API actually being reachable or up.
"""

from unittest.mock import MagicMock, patch

from DataPipeline.sources.jolpica_adapter import CanonicalRace, JolpicaAdapter

SAMPLE_ERGAST_PAYLOAD = {
    "MRData": {
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
        }
    }
}


def _mock_response(payload):
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def test_get_race_results_normalizes_to_canonical_shape():
    adapter = JolpicaAdapter()

    with patch("DataPipeline.sources.jolpica_adapter.requests.get") as mock_get:
        mock_get.return_value = _mock_response(SAMPLE_ERGAST_PAYLOAD)
        race = adapter.get_race_results(2024, 1)

    assert isinstance(race, CanonicalRace)
    assert race.season == 2024
    assert race.round == 1
    assert race.race_name == "Bahrain Grand Prix"
    assert len(race.results) == 2

    winner = race.results[0]
    assert winner.driver_id == "max_verstappen"
    assert winner.constructor_id == "red_bull"
    assert winner.position == 1
    assert winner.points == 25.0
    assert winner.time_millis == 5058286

    runner_up = race.results[1]
    assert runner_up.driver_id == "sergio_perez"
    assert runner_up.position == 2


def test_get_race_results_requests_the_correct_url():
    adapter = JolpicaAdapter()

    with patch("DataPipeline.sources.jolpica_adapter.requests.get") as mock_get:
        mock_get.return_value = _mock_response(SAMPLE_ERGAST_PAYLOAD)
        adapter.get_race_results(2024, 1)

    called_url = mock_get.call_args[0][0]
    assert called_url == "https://api.jolpi.ca/ergast/f1/2024/1/results.json"


def test_no_races_returned_raises():
    adapter = JolpicaAdapter()
    empty_payload = {"MRData": {"RaceTable": {"Races": []}}}

    with patch("DataPipeline.sources.jolpica_adapter.requests.get") as mock_get:
        mock_get.return_value = _mock_response(empty_payload)
        try:
            adapter.get_race_results(2024, 99)
            assert False, "expected ValueError for an empty Races list"
        except ValueError:
            pass
