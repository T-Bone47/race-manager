"""
Canonical F1 data schema — Phase 1.

This is the raw historical canonical layer: the "CANONICAL F1 DATASET" box
in MASTER_ARCHITECTURE.md section 6. It is deliberately NOT the same thing
as section 10's in-game driver ratings (Pace=88, Qualifying=91, ...) or
section 12's circuit characteristics (TyreStress, OvertakingDifficulty,
...) — those are later, derived outputs of the Model Calibration Layer
(section 30), built FROM this data, not equivalent to it. Building those
is out of scope here.

Every adapter (Jolpica now; FastF1/OpenF1/F1DB later, per section 4 and
the explicit "don't add sources until the schema is stable" sequencing)
must output these types and nothing else. Source-specific field names
must never leak past DataPipeline/sources/ (section 29).

Validation: pydantic, not plain dataclasses. Real runtime type-checking
and range constraints, so a malformed adapter payload fails loudly at
the schema boundary instead of quietly propagating bad data downstream.
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def build_race_id(season: int, round_: int) -> str:
    """The join key used across every entity below that belongs to one race."""
    return f"{season}_{round_}"


class SessionType(str, Enum):
    FP1 = "FP1"
    FP2 = "FP2"
    FP3 = "FP3"
    SPRINT_QUALIFYING = "SQ"
    SPRINT = "SPRINT"
    QUALIFYING = "Q"
    RACE = "RACE"


class TyreCompound(str, Enum):
    """Section 13's initial compound list."""

    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    INTERMEDIATE = "INTERMEDIATE"
    WET = "WET"


class CanonicalDriver(BaseModel):
    driver_id: str
    code: Optional[str] = None
    permanent_number: Optional[int] = None
    given_name: str
    family_name: str
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None


class CanonicalConstructor(BaseModel):
    """A team, in section 3/8's terminology."""

    constructor_id: str
    name: str
    nationality: Optional[str] = None


class CanonicalCircuit(BaseModel):
    """Raw circuit reference data only -- not section 12's calibrated
    gameplay circuit model (TyreStress, OvertakingDifficulty, etc.),
    which is a later, derived product built on top of this."""

    circuit_id: str
    name: str
    locality: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CanonicalRace(BaseModel):
    """A single scheduled race weekend."""

    race_id: str
    season: int = Field(ge=1950)
    round: int = Field(gt=0)
    name: str
    circuit_id: str
    date: date


class CanonicalSession(BaseModel):
    """Session metadata: one race has several of these (FP1-3, qualifying,
    sprint sessions where applicable, and the race itself)."""

    race_id: str
    session_type: SessionType
    session_date: Optional[date] = None
    time_utc: Optional[str] = None


class CanonicalRaceResult(BaseModel):
    race_id: str
    driver_id: str
    constructor_id: str
    position: Optional[int] = Field(default=None, gt=0)
    points: float = Field(ge=0)
    grid: int = Field(ge=0)  # 0 == pit lane start, per Ergast/Jolpica convention
    laps_completed: int = Field(ge=0)
    status: str
    time_millis: Optional[int] = Field(default=None, gt=0)
    fastest_lap_rank: Optional[int] = Field(default=None, gt=0)
    fastest_lap_time_millis: Optional[int] = Field(default=None, gt=0)


class CanonicalLap(BaseModel):
    """One driver's timing for one lap."""

    race_id: str
    driver_id: str
    lap_number: int = Field(gt=0)
    position: int = Field(gt=0)
    time_millis: int = Field(gt=0)


class CanonicalPitStop(BaseModel):
    race_id: str
    driver_id: str
    stop_number: int = Field(gt=0)
    lap_number: int = Field(gt=0)
    time_of_day: Optional[str] = None
    duration_millis: Optional[int] = Field(default=None, gt=0)


class CanonicalTyreStint(BaseModel):
    """Shape only. No adapter populates this yet -- Jolpica has no tyre
    data. Populated once a FastF1/OpenF1 adapter is added; the shape may
    still need revision at that point once real payloads get inspected."""

    race_id: str
    driver_id: str
    stint_number: int = Field(gt=0)
    compound: TyreCompound
    lap_start: int = Field(gt=0)
    lap_end: Optional[int] = Field(default=None, gt=0)
    tyre_age_at_start: int = Field(ge=0)


class CanonicalWeatherObservation(BaseModel):
    """Shape only. No adapter populates this yet -- same reason as
    CanonicalTyreStint above."""

    race_id: str
    session_type: SessionType
    timestamp_utc: Optional[str] = None
    air_temp_c: Optional[float] = None
    track_temp_c: Optional[float] = None
    humidity_pct: Optional[float] = Field(default=None, ge=0, le=100)
    rainfall: Optional[bool] = None
    wind_speed_kph: Optional[float] = Field(default=None, ge=0)
