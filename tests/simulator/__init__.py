import unittest

from simulator.actor import Actor

class TestAction(unittest.TestCase):

    brutus = Actor({}, 'Heroes', None)
    class StubbedAction(Action):
        pass

    spear_thrust = StubbedAction(brutus)

    def test_simple_action(self):
        self.spear_thrust.execute()
