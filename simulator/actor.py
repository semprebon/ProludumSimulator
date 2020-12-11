from simulator import conditions
from simulator.conditions import Condition
from simulator.actions import *
from simulator.dice import DicePool
from simulator.text import bcolors
import logging

class Actor:
    def __init__(self, data, faction):
        self.data = data
        self.faction = faction
        self.health = data['level']
        self.conditions = {}
        self.active = 0
        self.reactive = 0

    def has_condition(self, name, target=None):
        return self.conditions.get(conditions.key(name, target)) != None

    def add_condition(self, condition):
        existing_condition = self.conditions.get(condition.key())
        if existing_condition == None or existing_condition.severity < condition.severity:
            self.conditions[condition.key()] = condition

    def recover_from_fleeting_conditions(self):
        print(f"conditions: {list(self.conditions.keys())}")
        self.conditions = { key: cond for key, cond in self.conditions.items() if cond.severity > Condition.FLEETING }

    def name(self):
        return f"{self.data['name']}"

    def take_turn(self, others):
        roll = DicePool(self.data['level']).roll()
        action = self.pick_action(roll, others)
        print(f"{action.describe()}")
        action.resolve()
        self.recover_from_fleeting_conditions()

    def pick_foe(self, foes):
        import random
        if len(foes) == 0:
            return None
        else:
            return random.choice(foes)

    def takes_damage(self, damage):
        self.health = self.health - damage

    def defense(self):
        defense = self.data["armor"]
        if self.has_condition("staggerd"):
            defense = defense - 1
        return defense

    def extract_situation(self, foes):
        situation = {}
        situation["staggered"] = self.has_condition("staggered")
        situation["attack_advantage"] = any([ foe.has_condition("staggered") for foe in foes]) and not self.has_condition("hindered")
        situation["multiple_attackers"] = len(foes) > 1
        return situation

    def pick_action(self, roll, others):
        foes = [c for c in others if c.faction != self.faction]
        situation = self.extract_situation(foes)
        # node = self.data["tactics"]
        # while isinstance(node, dict):
        #     if situation[node["tag"]]:
        #         node = node[True]
        #     else:
        #         node = node[False]
        # print(f"action={node}")
        logging.info(f"pick_action: {self.name()};{situation}")
        import random
        node = random.choice(self.data["actions"])

        foe = self.pick_foe(foes)
        if foe == None:
            return Wait(self)
        else:
            action = by_name(node)
        return action(self, foe)

    def describe(self):
        print(f"{bcolors.OKBLUE}{self.name()}{bcolors.ENDC}: health: {self.health}  conditions: {list(self.conditions.keys())}")

