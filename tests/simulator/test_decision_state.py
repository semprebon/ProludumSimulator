import unittest
from unittest.mock import Mock

from simulator import weapons
from simulator.actions_mixin import attack_defaults
from simulator.actor import Actor
from simulator.condition import ConditionType
from simulator.decision_state import DecisionState
from simulator.simulator import Simulator
from simulator.weapons import Condition
from tests.simulator import fixed_dice
from tests.simulator.fixed_dice import FixedDicePool


class TestDecisionState(unittest.TestCase):

    def setUp(self):
        self.simulator = Simulator({ 'heroes': [], 'villains': [] })
        self.actor = Actor({'weapons': ['Knife'] , 'tactics': 'thrust_attack'},
                  'Heroes', self.simulator)

    def set_message_and_return(self, message, value):
        self.messages.append(message)
        return value

    def test_item_action_included_in_actions(self):
        self.actor = Actor({'weapons': ['LongSword'] , 'tactics': 'thrust_attack'}, 'Heroes', self.simulator)
        decision_state = DecisionState(self.actor)
        assert "thrust_attack" in decision_state.actions()
        assert "ranged_attack" not in decision_state.actions()

    def test_action_property_overrides(self):
        self.actor.foe = Actor({'tactics': 'thrust_attack'}, 'Villains', self.simulator)
        decision_state = DecisionState(self.actor)
        decision_state._action_properties["thrust_attack"]['vantage'] = lambda ds: self.set_message_and_return("vantage_modified", 3)

        self.messages = []
        decision_state.thrust_attack()
        self.assertEqual("vantage_modified", self.messages[0])

    def test_standard_actions_included_in_actions(self):
        decision_state = DecisionState(self.actor)
        assert "retreat" in decision_state.actions()

    def test_observations_included(self):
        decision_state = DecisionState(self.actor)
        assert "if_foe_in_move_range" in [ observation.__name__ for observation in decision_state.observations() ]

    def test_decision_state_can_use_decision_tree(self):
        simulator = Simulator("solo_vs_goblins")
        actor = simulator.combatant_by_name('Brutus')
        decision_state = DecisionState(actor)
        decision_state.add_action("thrust_attack",
                                  { **ATTACK_DEFAULTS, **{ 'vantage': lambda ds: self.set_message_and_return("ran", 3)} })
        decision_state.set_tactics("thrust_attack")

        self.messages = []
        decision_state.take_turn()
        self.assertEqual("ran", self.messages[0])

    def test_fleeting_condition_removed_at_end_of_turn(self):
        actor = Actor({ 'tactics': 'wait'}, 'Heroes', self.simulator)
        actor.add_condition(Condition(ConditionType.PREPARED_FOR, actor))
        self.assertEqual(True, actor.has_condition(ConditionType.PREPARED_FOR, actor))
        decision_state = DecisionState(actor)
        decision_state.take_turn()
        self.assertEqual(False, actor.has_condition(ConditionType.PREPARED_FOR, actor))

class TestStaggeredIncreasesSuccess(unittest.TestCase):

    def setUp(self):
        self.simulator = Simulator({ 'heroes': [], 'villains': [] })
        self.actor = Actor({'weapons': ['Knife'] , 'tactics': 'thrust_attack'},
                  'Heroes', self.simulator)
        self.foe = Actor({'weapons': ['Knife'] , 'level': 2, 'tactics': 'thrust_attack'},
                  'Villains', self.simulator)
        self.actor.foe = self.foe

    def test_foe_staggered_with_1_success(self):
        self.actor.dice_pool_class = FixedDicePool
        self.foe.add_condition(Condition(ConditionType.STAGGERED))
        decision_state = DecisionState(self.actor)

        FixedDicePool.roll_value = 1
        decision_state.take_turn()

        self.assertEqual(1, self.foe.health)

    def test_foe_staggered_with_2_successes(self):
        self.actor.dice_pool_class = FixedDicePool
        self.foe.add_condition(Condition(ConditionType.STAGGERED))
        decision_state = DecisionState(self.actor)

        FixedDicePool.roll_value = [2,1]
        decision_state.take_turn()

        self.assertEqual(0, self.foe.health)
