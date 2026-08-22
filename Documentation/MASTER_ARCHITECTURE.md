# F1 Manager Simulator — Master Architecture & Claude Development Specification

## 0. Purpose of This Document

This document is the single source of truth for the project.

Claude must read and follow this architecture before creating or modifying code. Do not redesign the architecture casually, replace core technologies, or generate a large amount of code without first checking this specification.

The project is a **management/simulation game inspired by Formula 1 team management**, not a driving game.

The player is the Team Principal. The main experience is:

**Manage → Decide → Simulate → Analyze → Develop → Repeat**

The game uses minimal but polished 3D race visualization. It does not require AAA graphics, realistic driving physics, or a full racing-game control system.

---

# 1. Product Vision

## Working Name

**Race Manager**  
(Project name can be changed later.)

## Core Promise

> Build and manage a motorsport team, make strategic decisions, develop the car, manage drivers and staff, survive race weekends, and compete for championships.

## Primary Design Pillars

1. **Decision Making**
   - The player should constantly make meaningful management and strategy decisions.

2. **Data-Driven Simulation**
   - Historical motorsport data is used to calibrate the simulator.

3. **Readable Race Experience**
   - The player should understand what is happening during a race without needing advanced graphics.

4. **Management Depth Over Graphics**
   - Management systems, strategy, economics, R&D and AI are more important than visual complexity.

5. **Replayability**
   - Different team choices, driver development, strategies, weather and AI decisions should create different seasons.

6. **Portfolio Quality**
   - The architecture should demonstrate C#, software architecture, algorithms, data engineering, simulation, AI systems, testing and Unity development.

---

# 2. Explicit Non-Goals

Do NOT turn this into:

- a driving simulator
- an arcade racing game
- a photorealistic AAA game
- a multiplayer game in V1
- a full vehicle physics simulator
- an enormous open-world game
- a clone of an existing commercial F1 Manager title

Avoid unnecessary feature creep.

Use the scope-guardian plugin whenever a proposed feature could expand the project substantially.

---

# 3. Recommended Technology Stack

## Game Engine

**Unity 6**

Reason:
- excellent UI workflow
- strong C# support
- good 2D/3D hybrid development
- suitable for lightweight simulation visualization
- easier fit than Unreal for a management-heavy game

## Programming

**C#**

Use C# for:
- simulation engine
- gameplay systems
- AI decision logic
- management systems
- Unity integration
- save/load

## Data Engineering

**Python**

Use Python for:
- external F1 data ingestion
- cleaning
- normalization
- feature engineering
- statistical analysis
- calibration
- generating game-ready datasets

## Database

Start with:
- JSON for static configuration and early development

Move to:
- SQLite or another embedded database if the dataset/save complexity requires it

Do not introduce a cloud database unless there is a demonstrated need.

## Source Control

**Git + GitHub**

Use:
- feature branches
- meaningful commits
- issues for planned work
- pull-request style review even when solo

## AI Assistant

**Claude**

Two separate roles:

### Development Copilot
Claude helps with:
- architecture
- C# coding
- Unity scripts
- debugging
- test generation
- refactoring
- documentation

### Optional In-Game AI Layer
Claude may power:
- race engineer explanations
- strategic explanation
- team reports
- natural-language assistant

Claude must NOT be responsible for deterministic race physics or numerical simulation outcomes.

The numerical simulation remains C# and deterministic.

---

# 4. External F1 Data Sources

The initial source set is intentionally sufficient. Do not keep adding sources unless a specific missing capability is demonstrated.

### Primary/Reference Sources

1. **Jolpica F1**
   https://github.com/jolpica/jolpica-f1

   Use for structured historical F1 data such as seasons, races, drivers, constructors, results, laps and pit stops.

2. **FastF1**
   https://github.com/theOehrly/Fast-F1

   Use for rich timing, telemetry, weather, session and analysis data.

3. **OpenF1**
   https://openf1.org/

   Use for structured session/lap/timing/weather information where appropriate.

4. **F1DB**
   https://github.com/f1db/f1db

   Use as a broad historical/reference database.

5. **Kaggle**
   https://www.kaggle.com/discussions/general/333090

   Use for experimentation, exploratory data analysis and supplemental datasets.

6. **Awesome F1**
   https://github.com/subinium/awesome-f1

   Treat primarily as a discovery/reference catalogue. Do not automatically add every linked source to the production pipeline.

---

# 5. Critical Data Architecture Rule

Unity must NOT directly depend on six external data sources.

Use:

External Sources
→ Python Data Pipeline
→ Canonical/Internal Dataset
→ C# Simulation Engine
→ Unity

The simulation must use our own normalized model.

The game should not care whether a particular value originally came from Jolpica, FastF1, OpenF1, F1DB or another source.

---

# 6. Complete System Architecture

```text
                         ┌──────────────────────────┐
                         │       EXTERNAL DATA       │
                         └────────────┬─────────────┘
                                      │
       ┌───────────────┬──────────────┼──────────────┬─────────────┐
       ↓               ↓              ↓              ↓             ↓
   Jolpica          FastF1         OpenF1          F1DB        Kaggle
       │               │              │              │             │
       └───────────────┴──────────────┼──────────────┴─────────────┘
                                      ↓
                         ┌──────────────────────────┐
                         │     PYTHON DATA LAYER    │
                         ├──────────────────────────┤
                         │ ingestion                │
                         │ validation               │
                         │ cleaning                 │
                         │ normalization            │
                         │ feature engineering      │
                         │ calibration              │
                         └────────────┬─────────────┘
                                      ↓
                         ┌──────────────────────────┐
                         │   CANONICAL F1 DATASET   │
                         ├──────────────────────────┤
                         │ drivers                  │
                         │ teams                    │
                         │ circuits                 │
                         │ races                    │
                         │ laps                     │
                         │ tyres                    │
                         │ weather                  │
                         │ pit stops                │
                         │ timing                   │
                         │ telemetry                │
                         └────────────┬─────────────┘
                                      ↓
                         ┌──────────────────────────┐
                         │ MODEL CALIBRATION LAYER  │
                         ├──────────────────────────┤
                         │ pace model               │
                         │ tyre degradation         │
                         │ pit-loss model           │
                         │ reliability model        │
                         │ overtaking model         │
                         │ weather impact            │
                         │ circuit characteristics  │
                         └────────────┬─────────────┘
                                      ↓
                         ┌──────────────────────────┐
                         │      GAME DATASET        │
                         └────────────┬─────────────┘
                                      ↓
                         ┌──────────────────────────┐
                         │      C# CORE ENGINE      │
                         ├──────────────────────────┤
                         │ race simulation           │
                         │ management systems        │
                         │ AI teams                  │
                         │ strategy engine            │
                         │ championship              │
                         └────────────┬─────────────┘
                                      ↓
                         ┌──────────────────────────┐
                         │         UNITY            │
                         ├──────────────────────────┤
                         │ UI                       │
                         │ dashboards               │
                         │ management screens       │
                         │ 3D race viewer           │
                         │ camera/visualization     │
                         │ audio                    │
                         └──────────────────────────┘

Optional:
Simulation State → Claude API → Race Engineer / Explanation Layer
```

---

# 7. Layer Responsibilities

## 7.1 Python Data Layer

Python is the research/data-engineering layer.

Responsibilities:
- API ingestion
- data extraction
- source validation
- schema normalization
- missing-data handling
- outlier inspection
- aggregation
- statistics
- model calibration
- exporting game-ready data

Python must NOT become the real-time game engine.

## 7.2 C# Simulation Engine

This is the heart of the game.

Responsibilities:
- drivers
- cars
- teams
- tyres
- fuel
- weather
- strategy
- race control events
- AI teams
- development
- finance
- staff
- championship

The simulation must be independent from the Unity UI as much as practical.

The same race simulation should be testable from automated tests without opening a Unity scene.

## 7.3 Unity Client

Unity is the presentation and interaction layer.

Responsibilities:
- menus
- dashboards
- cards
- charts
- buttons
- camera
- minimal 3D circuit
- cars moving around the circuit
- notifications
- animations
- audio

Do not put core simulation formulas inside UI MonoBehaviours.

---

# 8. Recommended Project Structure

```text
RaceManager/
│
├── UnityProject/
│   ├── Assets/
│   │   ├── Art/
│   │   ├── Audio/
│   │   ├── Materials/
│   │   ├── Prefabs/
│   │   ├── Scenes/
│   │   │   ├── Boot/
│   │   │   ├── MainMenu/
│   │   │   ├── Dashboard/
│   │   │   ├── RaceWeekend/
│   │   │   └── RaceViewer/
│   │   ├── UI/
│   │   ├── ScriptableObjects/
│   │   ├── Simulation/
│   │   ├── Gameplay/
│   │   ├── AI/
│   │   ├── Services/
│   │   ├── SaveSystem/
│   │   └── Tests/
│   │
│   └── ProjectSettings/
│
├── DataPipeline/
│   ├── sources/
│   ├── ingestion/
│   ├── cleaning/
│   ├── normalization/
│   ├── features/
│   ├── calibration/
│   ├── validation/
│   ├── exports/
│   ├── notebooks/
│   ├── tests/
│   └── requirements.txt
│
├── Documentation/
│   ├── MASTER_ARCHITECTURE.md
│   ├── GAME_DESIGN.md
│   ├── TECHNICAL_SPEC.md
│   ├── DATA_SCHEMA.md
│   ├── SIMULATION_MODEL.md
│   ├── AI_SPEC.md
│   ├── UI_SPEC.md
│   └── CHANGELOG.md
│
├── Tools/
│
├── Tests/
│
├── scripts/
│
├── .github/
│   └── workflows/
│
└── README.md
```

---

# 9. Domain Model

Core entities:

```text
Game
Season
Team
Driver
StaffMember
Car
CarComponent
Circuit
RaceWeekend
Session
Race
Lap
TyreSet
WeatherState
Strategy
PitStop
Incident
Sponsor
Contract
Facility
ResearchProject
RegulationSet
Championship
SaveGame
```

---

# 10. Driver Model

Driver attributes should not be a single overall rating.

Example attributes:

```text
Pace
Qualifying
Racecraft
Consistency
TyreManagement
WetSkill
Aggression
Feedback
Fitness
Experience
Adaptability
```

Psychological/team attributes:

```text
Morale
Confidence
TeamTrust
Pressure
```

Drivers should have development potential.

Example:

```text
Driver:
Pace = 88
Qualifying = 91
Racecraft = 84
TyreManagement = 87
WetSkill = 90
Consistency = 82
Feedback = 94
Potential = 95
```

---

# 11. Car Model

Separate car capability into components.

```text
Aerodynamics
Chassis
PowerUnit
EnergyRecovery
Cooling
Braking
Suspension
Weight
Reliability
TyrePerformance
```

Do not simulate full engineering physics.

Use calibrated performance coefficients.

---

# 12. Circuit Model

Each circuit should have attributes rather than only a mesh.

```text
Length
CornerCount
HighSpeedRatio
LowSpeedRatio
OvertakingDifficulty
TrackEvolution
TyreStress
BrakeStress
PowerSensitivity
AeroSensitivity
PitLaneLoss
SafetyCarLikelihood
WeatherVolatility
```

A circuit can also have metadata used by the visual track system.

---

# 13. Tyre Model

Initial compounds:

```text
Soft
Medium
Hard
Intermediate
Wet
```

Core variables:

```text
TyreAge
Grip
Temperature
Degradation
Warmup
TrackCondition
CompoundPerformance
```

A simplified model may use:

```text
LapTime =
BasePace
+ TyrePenalty
+ FuelPenalty
+ TrafficPenalty
+ WeatherPenalty
+ DamagePenalty
+ DriverVariation
+ RandomNoise
```

Tyre degradation should be calibrated from real data rather than invented blindly.

---

# 14. Fuel Model

Track:

```text
FuelLoad
FuelConsumptionPerLap
FuelPenalty
FuelSavingMode
FuelMargin
```

Fuel affects pace.

---

# 15. Weather Model

Variables:

```text
AirTemperature
TrackTemperature
RainProbability
RainIntensity
TrackWetness
Humidity
WindSpeed
WindDirection
Visibility
```

Derived states:

```text
Dry
LightRain
Intermediate
HeavyRain
Wet
DryingTrack
```

Weather should evolve over the race rather than remain constant.

---

# 16. Race Simulation Engine

The race engine should be discrete/event-based, not frame-based physics.

Suggested model:

```text
Race
 ↓
Initialize drivers
 ↓
Initialize cars
 ↓
Initialize tyres
 ↓
Initialize weather
 ↓
For each lap:
    Update weather
    Update tyre condition
    Update fuel
    Update ERS
    Calculate pace
    Resolve traffic
    Resolve overtaking
    Resolve incidents
    Resolve strategy decisions
    Resolve pit stops
    Resolve safety car/VSC/red flag events
    Update positions
    Record telemetry
 ↓
Finish race
 ↓
Calculate results
 ↓
Award championship points
 ↓
Update contracts/morale/finance
```

The simulation should support a deterministic random seed.

This allows:
- reproducible bugs
- replayable tests
- debugging
- simulation comparisons

---

# 17. Strategy Engine

The player should be able to choose:

- starting tyre
- pit strategy
- aggressive/standard/conserve pace
- ERS mode
- fuel management
- pit timing
- response to Safety Car/VSC
- weather decisions

The strategy engine should evaluate:

```text
CurrentTrackPosition
GapAhead
GapBehind
TyreAge
TyreDegradation
PitLaneLoss
WeatherForecast
SafetyCarProbability
Traffic
RemainingLaps
DriverCondition
CarReliability
```

Use expected-value style decision logic.

Do not make strategy purely random.

---

# 18. AI Team System

Every AI team should have a strategy profile.

Example:

```text
RiskTolerance
Aggression
PitBias
TyreConservation
WeatherGamble
OvertakeBias
SafetyCarReaction
DevelopmentPriority
```

AI team decisions may initially use rule-based utility scoring.

Example:

```text
StrategyScore =
ExpectedPositionGain
- PitLoss
+ TyreAdvantage
+ SafetyCarOpportunity
+ WeatherOpportunity
- RiskPenalty
```

Later versions may introduce ML.

Do not start with ML unless the rule-based system is already working.

---

# 19. Race Events

Implement an event framework.

Examples:

```text
SafetyCar
VirtualSafetyCar
RedFlag
Collision
Puncture
EngineIssue
BrakeIssue
Overheating
FrontWingDamage
SlowPitStop
WeatherChange
TrackEvolution
DriverError
Debris
```

Events should have:
- probability
- triggers
- severity
- duration
- consequences
- AI reaction

---

# 20. Management Systems

## Drivers

- scouting
- contracts
- salaries
- development
- morale
- performance

## Staff

Departments:

```text
Race Engineering
Aerodynamics
Reliability
Pit Crew
Driver Development
Data/Strategy
```

## R&D

Upgrade tree:

```text
Aerodynamics
Chassis
Power
Reliability
Tyre Management
Operations
```

Each upgrade needs:
- cost
- development time
- performance effect
- reliability effect
- prerequisites

## Finance

Track:

```text
Budget
Driver Salaries
Staff Salaries
Engine Costs
Operations
Development Costs
Sponsor Income
Prize Money
Facility Costs
```

## Sponsors

Sponsors may have:
- contract length
- income
- objectives
- bonuses
- penalties

## Facilities

Examples:

```text
Factory
Wind Tunnel
Simulator
Driver Academy
Strategy Room
Pit Equipment
Data Center
```

---

# 21. Career Mode

Core loop:

```text
Season
 ↓
Pre-season
 ↓
Race Weekend
 ↓
Race
 ↓
Development
 ↓
Next Race
 ↓
Final Championship
 ↓
Contract/Regulation Off-season
 ↓
Next Season
```

Include:
- standings
- driver contracts
- team performance
- regulations
- R&D progression
- finances
- reputation

---

# 22. Minimal 3D Race Viewer

The race viewer should be visually attractive but technically modest.

Use:
- simple 3D track
- low-poly cars
- basic materials
- camera follow
- replay camera
- leaderboard
- driver info
- strategy events
- race-control notifications

No:
- high-end car physics
- photorealistic environments
- complex pit-lane simulation
- cinematic rendering pipeline

The purpose of the 3D layer is to make the simulation understandable and engaging.

---

# 23. Race Viewer UI

Suggested layout:

```text
┌──────────────────────────────────────────────────────────────┐
│ LAP 31 / 57                         1x   2x   4x   8x        │
├──────────────────────────────────────┬───────────────────────┤
│                                      │ P1 DRIVER A            │
│             3D TRACK                 │ P2 DRIVER B            │
│                                      │ P3 YOUR DRIVER         │
│                                      │ P4 DRIVER D             │
│                                      │ ...                     │
│                                      │                         │
├──────────────────────────────────────┴───────────────────────┤
│ YOUR DRIVER                                                   │
│ Tyre: MEDIUM   Age: 17   Fuel: 42%   ERS: 68%                │
│ Pace: NORMAL   [ATTACK] [STANDARD] [CONSERVE]                │
│ [BOX]                                                         │
└──────────────────────────────────────────────────────────────┘
```

---

# 24. Dashboard Screens

Minimum screens:

```text
Main Menu
Team Selection
Career Dashboard
Race Calendar
Team Overview
Drivers
Staff
Car
R&D
Finance
Sponsors
Strategy
Race Weekend
Race Viewer
Standings
Statistics
Contracts
Settings
Save/Load
```

Do not build all screens before the simulation works.

---

# 25. Claude Integration

Claude is an optional layer around the deterministic simulation.

## Good use cases

### Race Engineer

User:
> "Why should I pit?"

Game provides structured state.

Claude:
> Explains the numerical strategy result in natural language.

### Post-Race Report

Claude summarizes:
- major strategic mistakes
- tyre performance
- pace trends
- driver performance
- key decisions

### Team Briefing

Before a race:
- strengths
- weaknesses
- risks
- suggested priorities

### Natural-Language Assistant

Player can ask:
- "Why is our car slow here?"
- "Should we prioritize aero or reliability?"
- "Why did our driver lose positions?"
- "How is the championship looking?"

## Hard Rule

Claude does not:
- directly mutate race state
- invent lap times
- determine championship points
- bypass game rules
- make non-deterministic numerical simulation decisions

---

# 26. Claude Development Workflow

Before coding:

1. Ask Claude to inspect this architecture.
2. Ask the engineering/architecture agent to identify dependencies.
3. Ask the game-design agents to validate the core loop.
4. Ask scope-guardian to check MVP scope.
5. Only then generate implementation tasks.

For each feature:

```text
Design
 ↓
Technical Spec
 ↓
Data Model
 ↓
Implementation
 ↓
Unit Tests
 ↓
Integration Test
 ↓
Code Review
 ↓
Scope Check
 ↓
Unity Integration
```

Do not ask Claude to "build the whole game" in one shot.

---

# 27. Required Claude Plugin Usage

The GameDev Claude Plugins marketplace contains specialized plugins for different game-development disciplines. Use them intentionally instead of treating the plugin collection as one generic tool.

## Highest Priority

### thinking
Use for:
- architecture decisions
- trade-offs
- assumptions
- pre-mortems
- first-principles analysis
- challenging weak ideas

Useful commands:
- `/first-principles`
- `/pre-mortem`
- `/devils-advocate`
- `/bias-check`

### game-design
Use for:
- mechanics
- player loop
- economy
- balance
- progression

Agents:
- mechanics-architect
- systems-weaver
- balance-oracle
- player-psychologist
- economy-designer

Useful commands:
- `/gdd`
- `/one-page`
- `/loop-check`

### engineering
Use for:
- architecture
- C# systems
- performance
- debugging
- refactoring
- code review

Agents:
- architecture-sage
- performance-detective
- debug-hunter
- gameplay-coder
- tools-builder
- verify-implementation

Useful commands:
- `/tech-spec`
- `/tech-stack`
- `/code-review`
- `/pattern`
- `/refactoring-plan`

### ui-ux
Use for:
- management dashboard
- race UI
- navigation
- onboarding
- usability

Useful commands:
- `/wireframe`
- `/ux-audit`

### ai-systems
Use for:
- AI team behavior
- driver personalities
- decision trees
- strategy behavior

Useful commands:
- `/ai-architecture`
- `/behavior-tree`
- `/npc-spec`
- `/difficulty-curve`

### devops
Use for:
- automated tests
- build process
- GitHub Actions
- release pipeline
- project health

Useful commands:
- `/pipeline-spec`
- `/test-strategy`
- `/build-audit`
- `/deploy-checklist`

### scope-guardian
Use before adding significant features.

Useful commands:
- `/scope-check`
- `/scope-report`

The scope-guardian plugin exists specifically to protect feature alignment and detect scope creep.

---

# 28. Secondary Plugins

Use as needed.

### art
- visual direction
- asset planning
- style guide

### technical-art
- Unity asset pipeline
- low-poly car/track optimization
- shaders
- rendering

### juice
Use near polish stage:
- transitions
- animation easing
- notification feedback
- subtle game feel

### accessibility
Apply to:
- color-independent information
- text sizes
- UI readability
- keyboard/controller navigation
- notification clarity

### product
Use for:
- milestones
- backlog
- priorities
- user stories

### user-research
Use once a playable prototype exists:
- playtests
- player surveys
- UX analysis

### audio
Use after gameplay works:
- pit radio
- UI feedback
- engine ambience
- race alerts

### procedural
Use only where helpful:
- procedural fictional calendars
- seeded events
- controlled variation

### marketing
Use only near release:
- store page
- trailer
- devlog

### operations
Do not prioritize for V1. Consider after a playable release.

### multiplayer
Do not use for V1.

### web-games
Do not use unless a browser/WebGL version becomes a deliberate target.

### certification
Use only when targeting a specific console/platform.

### narrative
Use only for optional team radio/story systems.

### level-design
Only lightly relevant because this is not a conventional level-based game.

### social-systems
Not part of MVP.

---

# 29. Data Schema Principles

Create a canonical internal schema.

Example:

```json
{
  "driverId": "driver_001",
  "teamId": "team_001",
  "pace": 88.4,
  "qualifying": 91.2,
  "racecraft": 84.8,
  "tyreManagement": 87.3,
  "wetSkill": 90.1,
  "consistency": 82.7
}
```

Avoid exposing external source-specific field names throughout the Unity project.

Use adapters:

```text
JolpicaAdapter
FastF1Adapter
OpenF1Adapter
F1DBAdapter
KaggleAdapter
```

All adapters output the same internal structures.

---

# 30. Model Calibration

Create a separate calibration workflow.

Goal:
convert observations into game parameters.

Examples:

```text
Observed tyre pace drop
        ↓
Tyre degradation coefficient

Observed pit stop distribution
        ↓
Pit stop baseline + variance

Observed safety-car frequency
        ↓
Event probability model

Observed circuit overtaking
        ↓
Overtake difficulty coefficient
```

Do not hard-code arbitrary values when real data can reasonably calibrate them.

However, gameplay balance overrides realism when necessary.

---

# 31. Simulation Validation

Create test scenarios.

Examples:

### Test 1
Same random seed + same input → same result.

### Test 2
Fresh tyres should generally outperform heavily worn tyres under equal conditions.

### Test 3
A faster car should generally produce faster pace, not always win.

### Test 4
A pit stop should incur a measurable time loss.

### Test 5
Safety car should compress gaps.

### Test 6
Wet conditions should change tyre competitiveness.

### Test 7
Fuel load should affect pace.

### Test 8
Reliability failures should be possible but not overwhelmingly common.

### Test 9
Championship points must match official game rules defined by the project.

### Test 10
No simulation state should become NaN/invalid.

---

# 32. Deterministic Simulation

Every race should support a seed.

Example:

```text
Season Seed: 824173
Race Seed: 19033
```

Given the same:
- seed
- driver attributes
- car attributes
- circuit
- weather inputs
- strategy

the simulation should reproduce the same result.

This makes debugging and balancing much easier.

---

# 33. Save System

Save:
- current season
- race index
- team
- drivers
- staff
- car
- R&D
- finance
- sponsors
- contracts
- standings
- simulation seed
- career history

Use versioned save data.

Example:

```text
saveVersion: 1
```

Future versions can migrate old saves.

---

# 34. MVP Definition

MVP must contain:

### Management
- team creation/selection
- two drivers
- basic car stats
- basic budget

### Race
- 5 fictional teams
- 10 drivers
- 5 circuits
- race simulation
- tyres
- fuel
- pit stops
- weather
- Safety Car
- AI teams
- championship points

### UI
- dashboard
- race strategy
- race viewer
- standings
- basic R&D

### Data
- at least one reliable historical data pipeline
- canonical dataset
- calibration notebook/scripts

### Testing
- simulation unit tests
- deterministic seed
- basic integration tests

Do not add advanced Claude features until MVP simulation works.

---

# 35. V1

After MVP:

- full season
- more teams/drivers
- driver contracts
- staff
- sponsors
- facilities
- advanced R&D
- morale
- regulation changes
- race engineer AI
- post-race analysis
- replay
- statistics
- better race viewer
- audio
- polished UI

---

# 36. V2

Possible future expansion:

- deeper driver academy
- multiple championships
- historical season scenarios
- advanced AI strategy
- multiplayer
- online leagues
- modding
- community-created teams
- browser version

Only build V2 after validating V1.

---

# 37. Development Order

## Phase 0 — Project Setup

- Git repository
- Unity project
- Python environment
- folder structure
- architecture documents
- CI basics
- plugin/tool workflow

## Phase 1 — Data Pipeline

- source adapters
- normalized schemas
- initial historical dataset
- calibration notebook
- exported game data

## Phase 2 — Simulation Core

- driver model
- car model
- circuit model
- tyre model
- fuel model
- weather
- race loop
- pit stops
- safety car
- results

## Phase 3 — AI

- AI teams
- strategy decisions
- driver behavior
- team profiles

## Phase 4 — Management

- team management
- R&D
- finance
- staff
- sponsors
- contracts

## Phase 5 — Unity UI

- dashboard
- driver screen
- R&D
- finance
- strategy
- standings

## Phase 6 — Race Viewer

- track
- cars
- camera
- leaderboard
- race HUD
- speed controls

## Phase 7 — Claude

- race engineer
- reports
- natural-language explanation layer

## Phase 8 — Polish

- audio
- animation
- transitions
- accessibility
- performance
- UX cleanup

## Phase 9 — QA

- automated tests
- playtesting
- balancing
- regression testing

## Phase 10 — Release

- Windows build
- documentation
- GitHub release
- demo video
- portfolio page

---

# 38. Rules for Claude While Developing

1. **Read this document before implementing major features.**

2. **Do not rewrite working systems without a reason.**

3. **Do not create duplicate managers/services when an existing system can be extended.**

4. **Do not put business/simulation logic directly inside Unity UI scripts.**

5. **Do not add dependencies without explaining why.**

6. **Prefer simple deterministic models over unnecessary ML.**

7. **Use real data to calibrate where practical.**

8. **Keep external data adapters separate from game logic.**

9. **Write tests for simulation logic.**

10. **Use seeded randomness.**

11. **When a requested feature expands scope, run `/scope-check`.**

12. **Before a major architecture decision, use the engineering architecture agent.**

13. **Before major gameplay systems, use game-design systems/mechanics agents.**

14. **Before UI implementation, use ui-ux agents/commands.**

15. **Before AI behavior implementation, use ai-systems.**

16. **Before release/build work, use devops.**

17. **Do not start multiplayer in MVP.**

18. **Do not chase photorealistic graphics.**

19. **Do not allow Claude API responses to directly alter deterministic simulation state.**

20. **When uncertain, inspect the existing repository and documents before inventing structures.**

---

# 39. Claude Working Style

For every new feature, Claude should respond internally in this order:

```text
1. Understand requirement
2. Check architecture
3. Identify affected systems
4. Identify dependencies
5. Propose implementation plan
6. Check scope
7. Implement smallest coherent change
8. Add/update tests
9. Validate
10. Summarize files changed
11. Update documentation if architecture changed
```

Avoid giant one-shot code generation.

Prefer small, verifiable increments.

---

# 40. Definition of Done

A feature is not considered complete when code compiles.

It is complete when:

- implementation exists
- tests exist where relevant
- UI is connected
- edge cases are addressed
- data flow is validated
- save/load behavior is handled if needed
- documentation is updated
- no architecture rule is violated
- scope is still acceptable
- Unity playtest confirms intended behavior

---

# 41. First Task Claude Should Perform

Do NOT start implementing gameplay immediately.

First:

1. Inspect this MASTER_ARCHITECTURE.md.
2. Inspect the repository.
3. Identify current files and tools.
4. Confirm Unity version.
5. Confirm C# project structure.
6. Confirm Python environment.
7. Confirm Git status.
8. Confirm which GameDev Claude plugins are active.
9. Create a technical dependency map.
10. Produce a Phase 0 implementation plan.
11. Ask for confirmation before creating large amounts of code.

---

# 42. Initial Claude Prompt

Use this as the first message in the Claude project:

> You are the lead architect and engineering partner for this project.
>
> Read `MASTER_ARCHITECTURE.md` completely before taking action.
>
> This project is a motorsport management and simulation game. It is NOT a driving game.
>
> The authoritative architecture is defined by the document.
>
> Use the installed GameDev Claude plugins deliberately:
> - `thinking` for first-principles decisions, pre-mortems and challenging assumptions.
> - `game-design` for mechanics, systems, economy and balance.
> - `engineering` for architecture, C#, debugging, performance and refactoring.
> - `ui-ux` for management and race interfaces.
> - `ai-systems` for AI team behavior and strategy.
> - `devops` for tests, builds and CI.
> - `scope-guardian` before significant feature additions or scope changes.
> - `art` and `technical-art` for the minimal visual pipeline.
> - `juice` only during polish.
> - `accessibility` during UI development.
> - `product` for backlog/prioritization when needed.
> - `user-research` after a playable prototype exists.
>
> Do not use Claude as the deterministic race simulator. The core simulation must remain deterministic, testable C# code.
>
> Do not begin by generating the entire game.
>
> First inspect the repository and produce:
> 1. repository audit
> 2. architecture-to-repository mapping
> 3. missing folders/files
> 4. Phase 0 implementation plan
> 5. risks and assumptions
> 6. recommended first implementation task
>
> Wait for approval before making large changes.

---

# 43. Long-Term Portfolio Positioning

The finished project should demonstrate:

- C#
- Unity
- OOP
- algorithms
- simulation
- AI decision systems
- data engineering
- Python
- API integration
- data analysis
- testing
- software architecture
- UI/UX

The project should be presented as:

> **A data-driven motorsport management and race-strategy simulator built with Unity and C#, calibrated using historical motorsport datasets and supported by AI-powered race engineering explanations.**

This is a software/simulation project first and a visual game second.

---

# 44. Final Architecture Principle

Keep this simple:

```text
REAL DATA
   ↓
DATA ENGINEERING
   ↓
CALIBRATED MODELS
   ↓
DETERMINISTIC C# SIMULATION
   ↓
UNITY VISUALIZATION
   ↓
PLAYER DECISIONS
   ↓
SIMULATION RESULTS
   ↓
OPTIONAL CLAUDE EXPLANATION
```

The project succeeds when the **management decisions are interesting**, the **simulation is believable**, the **data pipeline is defensible**, and the **visual layer makes the experience enjoyable**.

Graphics are a supporting system, not the core project.
