import unittest

from simulator import weapons
from simulator.actions_mixin import attack_defaults
from simulator.actor import Actor
from simulator.data_loader import load_data
from simulator.decision_state import DecisionState
from simulator.simulator import Simulator
from simulator.weapons import Item


class TestDecisionState(unittest.TestCase):

    knife = Item(
        Item.define_action('thrust_attack', [weapons.Melee, weapons.Attack, weapons.Impaling]))
    actor = Actor({ 'name': 'Goblin', 'level': 3, 'vitality': 1, 'weapons': [] , 'tactics': 'thrust_attack'},
                  'Heroes', None)
    actor.add_active_item(knife)

    def set_message_and_return(self, message, value):
        self.messages.append(message)
        return value

    def test_item_action_included_in_actions(self):
        decision_state = DecisionState(self.actor)
        assert "thrust_attack" in decision_state.actions()
        assert "swing_attack" not in decision_state.actions()

    def test_action_property_overrides(self):
        self.actor.foe = Actor({ 'name': 'Kobold', 'level': 1, 'vitality': 1, 'weapons': [] , 'tactics': 'thrust_attack'},
                  'Villains', None)
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
        assert "if_foe_nearby" in [ observation.__name__ for observation in decision_state.observations() ]

    def test_decision_state_can_use_decision_tree(self):
        simulator = Simulator("brutus_vs_goblins")
        actor = simulator.combatant_by_name('Brutus')
        decision_state = DecisionState(actor)
        decision_state.add_action("thrust_attack",
                                  { **attack_defaults(), **{ 'vantage': lambda ds: self.set_message_and_return("ran", 3)} })
        decision_state.set_tactics("thrust_attack")

        self.messages = []
        decision_state.take_turn()
        self.assertEqual("ran", self.messages[0])
