using System;
using NUnit.Framework;
using RaceManager.Simulation;

namespace RaceManager.Simulation.Tests
{
    public class DeterministicRaceStubTests
    {
        [Test]
        public void SameSeed_ProducesIdenticalLapSequence()
        {
            var runA = new DeterministicRaceStub(seed: 824173).SimulateLapTimesMs(20);
            var runB = new DeterministicRaceStub(seed: 824173).SimulateLapTimesMs(20);

            Assert.That(runB, Is.EqualTo(runA));
        }

        [Test]
        public void DifferentSeeds_ProduceDifferentLapSequences()
        {
            var runA = new DeterministicRaceStub(seed: 824173).SimulateLapTimesMs(20);
            var runC = new DeterministicRaceStub(seed: 19033).SimulateLapTimesMs(20);

            Assert.That(runC, Is.Not.EqualTo(runA));
        }

        [Test]
        public void LapCount_MatchesRequestedLaps()
        {
            var laps = new DeterministicRaceStub(seed: 1).SimulateLapTimesMs(57);

            Assert.That(laps.Count, Is.EqualTo(57));
        }

        [Test]
        public void InvalidLapCount_Throws()
        {
            var stub = new DeterministicRaceStub(seed: 1);

            Assert.Throws<ArgumentOutOfRangeException>(() => stub.SimulateLapTimesMs(0));
        }

        [Test]
        public void NoLapTime_IsEverNegativeOrZero()
        {
            // Cheap stand-in for Validation Test 10 (section 31): no
            // simulation state should become NaN/invalid. A lap time of
            // zero or less is an obviously invalid physical result.
            var laps = new DeterministicRaceStub(seed: 42).SimulateLapTimesMs(50);

            foreach (var lapMs in laps)
            {
                Assert.That(lapMs, Is.GreaterThan(0));
            }
        }
    }
}
