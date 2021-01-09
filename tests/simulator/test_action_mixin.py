import unittest
from unittest.mock import Mock

from simulator.actor import Actor
from simulator.decision_state import DecisionState


class RiggedDicePool:
    roll_value = 2

    def __init__(self, count):
        pass

    def roll(self):
        return self.roll_value


class TestMeleeAttack(unittest.TestCase):

    def test_can_move_to_attack(self):
        simulator = Mock()
        simulator.faction_position.return_value = 0
        actor = Actor({'name': 'attacker', 'weapons': ['Knife']}, "Heroes", simulator)
        actor.dice_pool_class = RiggedDicePool
        simulator.faction_position.return_value = actor.speed()
        foe = Actor({'name': 'defender'}, "Villains", simulator)
        actor.foe = foe
        actor.position = 1
        ds = DecisionState(actor)
        ds.thrust_attack()
        self.assertEquals(1, actor.average("wound_foe"))
