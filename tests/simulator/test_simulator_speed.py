import unittest

from simulator.simulator import Simulator


class TestSimulatorSpeed(unittest.TestCase):

    def test_run_simulator(self):
        simulator = Simulator("team_2_vs_goblins")
        simulator.run_until_done()

if __name__ == '__main__':
    unittest.main()
