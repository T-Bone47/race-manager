"""
Schema validation tests for the canonical types themselves (as opposed to
test_jolpica_adapter.py, which tests the adapter's source -> canonical
mapping). These confirm the pydantic constraints actually reject bad data
rather than silently accepting it.
"""

import pytest
from pydantic import ValidationError

from DataPipeline.schema.canonical import (
    CanonicalDriver,
    CanonicalLap,
    CanonicalPitStop,
    CanonicalRace,
    CanonicalRaceResult,
    CanonicalSession,
    CanonicalWeatherObservation,
    SessionType,
    TyreCompound,
    build_race_id,
)


def test_build_race_id_format():
    assert build_race_id(2024, 1) == "2024_1"
    assert build_race_id(1950, 7) == "1950_7"


# ---- valid construction --------------------------------------------------

def test_canonical_driver_valid_construction():
    driver = CanonicalDriver(
        driver_id="max_verstappen",
        code="VER",
        permanent_number=33,
        given_name="Max",
        family_name="Verstappen",
        nationality="Dutch",
    )
    assert driver.driver_id == "max_verstappen"


def test_canonical_driver_allows_missing_optional_fields():
    # Only the required fields; every Optional field should default to None
    driver = CanonicalDriver(driver_id="farina", given_name="Nino", family_name="Farina")
    assert driver.code is None
    assert driver.permanent_number is None
    assert driver.date_of_birth is None


# ---- required-field rejection ---------------------------------------------

def test_canonical_driver_missing_required_field_rejected():
    with pytest.raises(ValidationError):
        CanonicalDriver(driver_id="max_verstappen", given_name="Max")  # missing family_name


# ---- numeric constraint rejection ------------------------------------------

def test_lap_number_must_be_positive():
    with pytest.raises(ValidationError):
        CanonicalLap(race_id="2024_1", driver_id="x", lap_number=0, position=1, time_millis=90000)


def test_lap_time_must_be_positive():
    with pytest.raises(ValidationError):
        CanonicalLap(race_id="2024_1", driver_id="x", lap_number=1, position=1, time_millis=-5)


def test_race_result_points_cannot_be_negative():
    with pytest.raises(ValidationError):
        CanonicalRaceResult(
            race_id="2024_1",
            driver_id="x",
            constructor_id="y",
            points=-5,
            grid=1,
            laps_completed=57,
            status="Finished",
        )


def test_race_result_grid_zero_is_allowed():
    # grid == 0 is a valid Ergast/Jolpica convention for a pit-lane start,
    # not an error -- only negative values should be rejected.
    result = CanonicalRaceResult(
        race_id="2024_1",
        driver_id="x",
        constructor_id="y",
        points=0,
        grid=0,
        laps_completed=57,
        status="Finished",
    )
    assert result.grid == 0


def test_pit_stop_duration_must_be_positive():
    with pytest.raises(ValidationError):
        CanonicalPitStop(
            race_id="2024_1", driver_id="x", stop_number=1, lap_number=12, duration_millis=-100
        )


def test_race_season_before_1950_rejected():
    with pytest.raises(ValidationError):
        CanonicalRace(
            race_id="1900_1", season=1900, round=1, name="Not Real GP", circuit_id="x", date="1900-01-01"
        )


def test_weather_humidity_out_of_range_rejected():
    with pytest.raises(ValidationError):
        CanonicalWeatherObservation(
            race_id="2024_1", session_type=SessionType.RACE, humidity_pct=150
        )


# ---- enum rejection ---------------------------------------------------------

def test_invalid_session_type_rejected():
    with pytest.raises(ValidationError):
        CanonicalSession(race_id="2024_1", session_type="FP4")  # not a real session


def test_invalid_tyre_compound_rejected():
    with pytest.raises(ValidationError):
        from DataPipeline.schema.canonical import CanonicalTyreStint

        CanonicalTyreStint(
            race_id="2024_1",
            driver_id="x",
            stint_number=1,
            compound="SUPERSOFT",  # not one of section 13's five compounds
            lap_start=1,
            tyre_age_at_start=0,
        )


def test_valid_tyre_compound_accepted():
    from DataPipeline.schema.canonical import CanonicalTyreStint

    stint = CanonicalTyreStint(
        race_id="2024_1",
        driver_id="x",
        stint_number=1,
        compound=TyreCompound.MEDIUM,
        lap_start=1,
        tyre_age_at_start=0,
    )
    assert stint.compound == TyreCompound.MEDIUM
