# Data Schema

Canonical F1 dataset schema — Phase 1. Source of truth for field definitions is `DataPipeline/schema/canonical.py`; this document explains the *why* behind it and how it maps to sources.

## Layer, not the same as gameplay data

This schema is the "CANONICAL F1 DATASET" box in `MASTER_ARCHITECTURE.md` section 6 — the raw, normalized historical record. It is **not**:

- section 10's in-game driver ratings (`Pace`, `Qualifying`, `Racecraft`, ...) — those are calibrated, derived outputs of the Model Calibration Layer (section 30), built *from* this data
- section 12's circuit characteristics (`TyreStress`, `OvertakingDifficulty`, ...) — same reason

Building those calibrated models is out of scope for Phase 1.

## Validation

Every type is a `pydantic.BaseModel`, not a plain dataclass. Malformed adapter output should fail loudly at construction time (a `pydantic.ValidationError`), not propagate silently downstream. See `DataPipeline/tests/test_canonical_schema.py` for the constraints actually enforced.

## ID scheme

`driver_id` / `constructor_id` / `circuit_id` are the source's own slugs (e.g. `"max_verstappen"`, `"red_bull"`, `"albert_park"`) — not synthetic sequential IDs like section 29's `driver_001` example. That example belongs to the later, calibrated Game Dataset stage. At this raw-history layer, with exactly one source, a surrogate key would solve a problem that doesn't exist yet. Revisit if/when a second source's IDs collide or diverge from Jolpica's.

`race_id` is a derived join key: `f"{season}_{round}"` (see `build_race_id`), used by every entity below that belongs to one race.

## Entities

| Entity | Fields | Populated by |
|---|---|---|
| `CanonicalDriver` | `driver_id, code, permanent_number, given_name, family_name, date_of_birth, nationality` | Jolpica |
| `CanonicalConstructor` | `constructor_id, name, nationality` | Jolpica |
| `CanonicalCircuit` | `circuit_id, name, locality, country, latitude, longitude` | Jolpica |
| `CanonicalRace` | `race_id, season, round, name, circuit_id, date` | Jolpica |
| `CanonicalSession` | `race_id, session_type, session_date, time_utc` | Jolpica |
| `CanonicalRaceResult` | `race_id, driver_id, constructor_id, position, points, grid, laps_completed, status, time_millis, fastest_lap_rank, fastest_lap_time_millis` | Jolpica |
| `CanonicalLap` | `race_id, driver_id, lap_number, position, time_millis` | Jolpica |
| `CanonicalPitStop` | `race_id, driver_id, stop_number, lap_number, time_of_day, duration_millis` | Jolpica |
| `CanonicalTyreStint` | `race_id, driver_id, stint_number, compound, lap_start, lap_end, tyre_age_at_start` | **Shape only** — no source yet |
| `CanonicalWeatherObservation` | `race_id, session_type, timestamp_utc, air_temp_c, track_temp_c, humidity_pct, rainfall, wind_speed_kph` | **Shape only** — no source yet |

`CanonicalTyreStint` and `CanonicalWeatherObservation` exist because the schema needed to be designed for the domain, not for what one source happens to provide (section 29). Jolpica (Ergast-compatible) has no tyre or weather data at all. These stay unpopulated until a FastF1/OpenF1 adapter is added — deliberately deferred per the "don't add sources until the schema is stable" rule, not forgotten.

`SessionType`: `FP1, FP2, FP3, SQ (sprint qualifying), SPRINT, Q, RACE`. Which of these exist for a given race varies by weekend format (sprint weekends carry extra sessions) — `get_season_schedule` only emits the ones actually present in the source, it doesn't fabricate a fixed set.

`TyreCompound`: `SOFT, MEDIUM, HARD, INTERMEDIATE, WET` (section 13's initial compound list).

## Source-to-schema mapping (Jolpica)

| Canonical entity | Jolpica endpoint | Adapter method | Notes |
|---|---|---|---|
| `CanonicalDriver` | `/ergast/f1/{season}/drivers.json` | `get_drivers(season)` | |
| `CanonicalConstructor` | `/ergast/f1/{season}/constructors.json` | `get_constructors(season)` | |
| `CanonicalCircuit` | `/ergast/f1/{season}/circuits.json` | `get_circuits(season)` | |
| `CanonicalRace` + `CanonicalSession` | `/ergast/f1/{season}/races.json` | `get_season_schedule(season)` | Returns `(races, sessions)` |
| `CanonicalRaceResult` | `/ergast/f1/{season}/{round}/results.json` | `get_race_results(season, round)` | Returns results only; race metadata comes from `get_season_schedule`, not duplicated here |
| `CanonicalLap` | `/ergast/f1/{season}/{round}/laps.json` | `get_laps(season, round)` | Paginated — a race can have ~1,400 lap-timing rows against a 100-row page cap |
| `CanonicalPitStop` | `/ergast/f1/{season}/{round}/pitstops.json` | `get_pit_stops(season, round)` | Paginated defensively |
| `CanonicalTyreStint` | — | not implemented | No Jolpica tyre data |
| `CanonicalWeatherObservation` | — | not implemented | No Jolpica weather data |

Deliberately not fetched yet, even though Jolpica supports it: qualifying results, sprint results, standings. Wasn't asked for in Phase 1's scope — add when a real need shows up, not speculatively.

## Known gaps / open items

- Schema shape for tyres/weather is provisional; expect revision once a real FastF1/OpenF1 payload gets inspected.
- No bulk-backfill throttling strategy yet (fetching many seasons × many races' worth of laps will need real rate-limit handling eventually) — not solved now, would be premature before there's a concrete backfill task.
