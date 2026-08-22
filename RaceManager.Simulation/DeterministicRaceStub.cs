using System;
using System.Collections.Generic;

namespace RaceManager.Simulation
{
    /// <summary>
    /// Phase 0 scaffold only. This is deliberately NOT the real pace / tyre /
    /// fuel / strategy model -- that's Phase 2 (Simulation Core) per
    /// MASTER_ARCHITECTURE.md section 37, and belongs in its own class once
    /// the calibrated coefficients exist.
    ///
    /// Its only job right now is to prove, mechanically, that this project's
    /// simulation layer can run and be tested with zero Unity dependency, and
    /// that a given seed always reproduces the same result -- Validation
    /// Test 1 in section 31, and the core requirement in section 32
    /// (Deterministic Simulation).
    /// </summary>
    public class DeterministicRaceStub
    {
        private const int BaseLapMilliseconds = 90000; // toy 1:30.000, placeholder only
        private const int VariationRangeMilliseconds = 400;

        public int Seed { get; }

        public DeterministicRaceStub(int seed)
        {
            Seed = seed;
        }

        /// <summary>
        /// Produces a reproducible sequence of lap times (in milliseconds) for
        /// a single toy driver across the given number of laps. Same seed +
        /// same lap count always produces an identical sequence, on any
        /// machine, forever -- that guarantee is the entire point of this
        /// class existing before any real simulation logic does.
        /// </summary>
        public IReadOnlyList<int> SimulateLapTimesMs(int lapCount)
        {
            if (lapCount <= 0)
            {
                throw new ArgumentOutOfRangeException(nameof(lapCount), "Lap count must be positive.");
            }

            var random = new Random(Seed);
            var laps = new List<int>(lapCount);

            for (int i = 0; i < lapCount; i++)
            {
                // Toy variation only. Real degradation/fuel/traffic/weather
                // penalties are Phase 2 -- see section 13's LapTime formula.
                int variationMs = random.Next(-VariationRangeMilliseconds, VariationRangeMilliseconds + 1);
                int lapMs = BaseLapMilliseconds + variationMs;
                laps.Add(lapMs);
            }

            return laps;
        }
    }
}
