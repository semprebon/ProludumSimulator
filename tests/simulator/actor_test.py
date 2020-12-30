import unittest

from simulator.actor import Actor
from simulator.data_loader import load_data
from simulator.decision_state import DecisionState
from simulator.simulator import Simulator
from simulator.weapons import Knife


class TestDecisionState(unittest.TestCase):

    simulator = Simulator("brutus_vs_goblins")
    actor = simulator.combatant_by_name('Goblin')

    def set_message_and_return(self, message, value):
        self.messages.append(message)
        return value

    def test_can_run_parsed_tactics(self):
        simulator = Simulator("brutus_vs_goblins")
        actor = Actor(load_data('brutus', directory='data/actors')[0], 'Heroes', simulator)
        decision_state = DecisionState(self.actor)
        decision_state.take_turn()
        assert "melee_thrust" in [ action.__name__ for action in decision_state.actions() ]

        self.messages = []
