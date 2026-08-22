# Race Manager

A data-driven motorsport team-management and race-strategy simulator built with Unity 6 and C#, calibrated using historical motorsport datasets. Not a driving game — you're the Team Principal, not the driver.

The authoritative spec for this project is [`Documentation/MASTER_ARCHITECTURE.md`](Documentation/MASTER_ARCHITECTURE.md). Read it before touching anything below.

## Status: Phase 0 — Project Setup

This repo currently contains the Phase 0 scaffold only:

- [x] Repository structure
- [x] `Documentation/MASTER_ARCHITECTURE.md` seeded
- [x] `DataPipeline/` Python scaffold with one working (mocked) adapter test
- [x] `RaceManager.Simulation` — a Unity-independent C# class library, headlessly testable, proving MASTER_ARCHITECTURE.md section 7.2's "testable without opening a Unity scene" principle
- [x] CI workflow running both test suites on push
- [ ] Actual Unity 6 project (must be created locally — see `UnityProject/README.md`)
- [ ] Phase 1 real data pipeline (currently one adapter, one endpoint, as a proof of pattern only)
- [ ] Phase 2 real simulation core (the C# code here today is a determinism scaffold, not the pace/tyre/strategy model)

## Layout

```
race-manager/
├── Documentation/            architecture & design docs
├── DataPipeline/             Python: external data → canonical schema
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
