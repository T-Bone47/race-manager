# UnityProject/

This folder is intentionally close to empty. Unity Editor generates a lot of required metadata here (`.meta` files, `ProjectSettings/*.asset`, `Packages/manifest.json`, etc.) that only the Editor itself can produce correctly — hand-authoring it risks conflicting with Unity's own project-creation flow, so it wasn't faked.

## Setup (do this locally, in Unity Hub / Unity Editor)

1. Confirm you're on **Unity 6 (LTS)** per `Documentation/MASTER_ARCHITECTURE.md` section 3. If you're on a different version, note it — some of the C#/`LangVersion` assumptions in `RaceManager.Simulation.csproj` may need revisiting.
2. In Unity Hub, create a new **3D (URP or Built-in — either is fine for this project's scope)** project with this exact folder (`UnityProject/`) as its location. Unity will populate `Assets/`, `Packages/`, `ProjectSettings/`, etc.
3. Under `Assets/`, create the subfolders `MASTER_ARCHITECTURE.md` section 8 calls for: `Art/`, `Audio/`, `Materials/`, `Prefabs/`, `Scenes/{Boot,MainMenu,Dashboard,RaceWeekend,RaceViewer}/`, `UI/`, `ScriptableObjects/`, `Simulation/`, `Gameplay/`, `AI/`, `Services/`, `SaveSystem/`, `Tests/`.
4. Wire in `RaceManager.Simulation` (the C# class library one level up) — either:
   - as a **project reference** (Unity 2021+ supports referencing an external `.csproj` via a `.asmref`/custom `csc.rsp`, though the simpler and more common approach for a solo project is:)
   - **linked/copied source**: place (or symlink) the `.cs` files from `RaceManager.Simulation/` into `Assets/Simulation/`, wrapped in an Assembly Definition (`.asmdef`) named `RaceManager.Simulation` so Unity compiles them as their own assembly, matching section 7.2's "independent from the Unity UI" requirement.
5. Confirm the empty project opens and builds cleanly with no console errors, then report back — that's the one verification step in this whole setup that has to happen on your machine; it can't be checked from a chat sandbox.

Once this is done, Phase 0 is genuinely complete (see the top-level `README.md` checklist).
