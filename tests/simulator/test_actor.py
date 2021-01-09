import unittest
from unittest.mock import Mock

from simulator.actor import Actor

class TestTakesDamage(unittest.TestCase):

    def setUp(self):
        self.simulator = Mock()

    def test_damage_with_no_vitality(self):
        actor = Actor({ 'vitality': 0, 'health': 3 }, 'Heroes', self.simulator)
        actor.takes_damage(1)
        self.assertEqual(2, actor.health)
        self.assertEqual(0, actor.vitality)

    def test_damage_with_some_vitality(self):
        actor = Actor({ 'vitality': 1, 'health': 3 }, 'Heroes', self.simulator)
        actor.takes_damage(2)
        self.assertEqual(2, actor.health)
        self.assertEqual(0, actor.vitality)

    def test_damage_with_lots_of_vitality(self):
        actor = Actor({ 'vitality': 3, 'health': 3 }, 'Heroes', self.simulator)
        actor.takes_damage(2)
        self.assertEqual(3, actor.health)
        self.assertEqual(1, actor.vitality)

    def test_damage_overkill(self):
        actor = Actor({ 'vitality': 0, 'health': 3 }, 'Heroes', self.simulator)
        actor.takes_damage(4)
        self.assertEqual(0, actor.health)
        self.assertEqual(0, actor.vitality)

class TestTrackAverage(unittest.TestCase):

    def test_no_data(self):
        actor = Actor({}, 'Heroes', Mock())
        self.assertEqual(None, actor.average("roll"))

    def test_with_data(self):
        actor = Actor({}, 'Heroes', Mock())
        actor.track_average('roll', 1)
        actor.track_average('roll', 2)
        self.assertEqual(1.5, actor.average("roll"))

