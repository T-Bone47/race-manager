# Race Manager

A data-driven motorsport team-management and race-strategy simulator built with Unity 6 and C#, calibrated using historical motorsport datasets. Not a driving game — you're the Team Principal, not the driver.

The authoritative spec for this project is [`Documentation/MASTER_ARCHITECTURE.md`](Documentation/MASTER_ARCHITECTURE.md). Read it before touching anything below.

## Status: Phase 1 — Data Pipeline (in progress)

- [x] Phase 0: repository structure, `Documentation/MASTER_ARCHITECTURE.md` seeded
- [x] Phase 0: `RaceManager.Simulation` — a Unity-independent C# class library, headlessly testable, proving MASTER_ARCHITECTURE.md section 7.2's "testable without opening a Unity scene" principle
- [x] Phase 0: CI workflow running both test suites on push
- [x] Phase 1: canonical schema (`DataPipeline/schema/canonical.py`, `Documentation/DATA_SCHEMA.md`) — 10 entities, pydantic-validated
- [x] Phase 1: Jolpica adapter covers drivers, constructors, circuits, season schedule + sessions, race results, laps, pit stops — all offline-tested (27 tests passing)
- [ ] Phase 1: tyres / weather — schema defined, unpopulated until a FastF1/OpenF1 adapter exists
- [ ] Actual Unity 6 project (must be created locally — see `UnityProject/README.md`)
- [ ] Phase 2 real simulation core (the C# code here today is a determinism scaffold, not the pace/tyre/strategy model)

## Layout

```
race-manager/
├── Documentation/            architecture & design docs
├── DataPipeline/             Python: external data → canonical schema
│   ├── schema/               canonical.py — the 10 Phase 1 entity types
│   ├── sources/               per-source adapters (jolpica_adapter.py)
│   └── tests/
├── RaceManager.Simulation/            C# class library: deterministic sim core (Unity-independent)
├── RaceManager.Simulation.Tests/      NUnit tests for the above
├── UnityProject/              placeholder — create the actual Unity 6 project here
├── Tools/                     misc dev tooling, added as needed
├── scripts/                   misc automation scripts, added as needed
└── .github/workflows/         CI
```

## Running things locally

### Data pipeline (Python)

```bash
cd DataPipeline
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd ..
pytest
```

### Simulation core (C#)

```bash
dotnet test RaceManager.sln
```

### Unity

See [`UnityProject/README.md`](UnityProject/README.md) — this has to be created locally, in the Unity Editor, on your machine.

## Contributing to this repo (solo or not)

Per `MASTER_ARCHITECTURE.md` section 3: feature branches, meaningful commits, PR-style review even solo. Per section 38–39: small, testable increments — no giant one-shot changes, and every feature gets an architecture check, a scope check, and tests before it's called done.
