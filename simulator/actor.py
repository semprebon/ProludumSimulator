import sys

from simulator.condition import ConditionType, FLEETING, RECOVERABLE
from simulator.decision_state import DecisionState
from simulator import condition
from simulator.dice import DicePool
from simulator.text import bcolors
import logging

class Actor:
    DEFAULT_DATA = { 'name': 'None', 'level': 3, 'armor': 0, 'vitality': 0,
                     'speed': 6, 'weapons': [], 'tactics': "wait", 'position': 0 }

    def __init__(self, data, faction, simulator):
        from simulator.weapons import ITEMS
        self.data = { **self.DEFAULT_DATA, **data }
        self.active_items = [ ITEMS[name] for name in self.data['weapons'] ]
        self.faction = faction
        self.simulator = simulator
        self.tactics_code = self.parse_tactics(self.data['tactics'])
        self.averages = {}
        self.dice_pool_class = DicePool
        self.reset()

    def parse_tactics(self, str):
        import re
        return compile(re.sub(r'(\w+)', r'self.\1', str), 'tactics', "eval")

    def set_decision_state_class(self):
        self.decision_state_class = DecisionState

    def decision_state(self):
        return self.decision_state_class(self)

    # def add_mixins(self):
    #     from simulator.observations_mixin import ObservationMixin
    #     from simulator.addon_effects import AddonEffects
    #
    #     """ add in mixin classes from character data and observations, and add each mixin's
    #         methods to list of actions/observations actor can take"""
    #     def is_mix_method(cls, method_name):
    #         return callable(getattr(cls, method_name)) and not method_name.startswith("__")
    #
    #     import inspect
    #
    #     names = self.data['weapons']
    #     action_mixins = [ p[1] for p in inspect.getmembers(sys.modules["simulator.weapons"]) if p[0] in names ]
    #
    #     self.__class__ = type(self.name()+"Expanded",
    #                           tuple(action_mixins + [ObservationMixin, AddonEffects, self.__class__]), {})
    #     self.actions = [ getattr(self, name)
    #                 for mixin in action_mixins for name in dir(mixin) if is_mix_method(mixin, name) ]
    #     self.observations = [ getattr(self, name)
    #                 for name in dir(ObservationMixin) if is_mix_method(ObservationMixin, name) ]

    def reset(self):
        self.health = self.data['level']
        self.vitality = self.data['vitality']
        self.conditions = {}
        self.foe = None
        self.position = self.simulator.faction_position(self.faction) or self.data['position']

    def suffix_name(self, count):
        self.data['name'] = f'{self.data["name"]}{count}'

    def has_condition(self, cond, target=None):
        return self.conditions.get(condition.key(cond.name, target), None) != None

    def add_condition(self, condition):
        existing_condition = self.conditions.get(condition.key())
        if existing_condition == None:
            self.conditions[condition.key()] = condition

    def expiring_conditions(self):
        return [ cond for key, cond in self.conditions.items() if cond.duration() == condition.FLEETING ]

    def recover_from_condition(self):
        keys = [ key for key, cond in self.conditions.items() if cond.duration() == RECOVERABLE ]
        if len(keys) > 0:
            del self.conditions[keys[0]]
            return keys[0]
        return None

    def expire_conditions(self, conditions):
        self.conditions = { key: cond for key, cond in self.conditions.items() if cond not in conditions }

    def recover_from_fleeting_conditions(self):
        #print(f"conditions: {list(self.conditions.keys())}")
        self.conditions = { key: cond for key, cond in self.conditions.items() if not cond.check_expired() }

    def add_active_item(self, item):
        self.active_items.append(item)

    def use_addon_effect(self, action_points, effect, schedule):
        cost = schedule.get(effect, None)
        if cost and cost <= action_points:
            if effect(self.foe):
                return action_points - cost
        return action_points

    def name(self):
        return f"{self.data['name']}"

    def take_turn(self, others):
        roll = self.dice_pool_class(self.data['level']).roll()
        self.take_action(roll, others)
        self.recover_from_fleeting_conditions()

    # TODO: Complete this abbreviated action generator
    # def implement_action(self, roll=None, roll_mod=None, foe_roll_mod=None,
    #                      success_mod=None, foe_success_mod=None, threshold=2, minor_effect=None, major_effect=None,
    #                      enhancement_bonus=None, enhancements={ }):
    #
    #     successes = roll(self.foe)
    #
    #     successes = self.attack_roll(self.foe) + 1 if self.has_condition(Condition.AIM_AT, self.foe) else 0
    #     action_points = self.apply_effect(successes, threshold=2,
    #             minor_effect=actor.apply_condition(self.foe, Condition.HINDERED),
    #             major_effect=wound_foe(self.foe))
    #     self.allocate_action_points(action_points, { self.escalate_condition: 2, self.recover: 1 })
    #
    # def normalize_action_conditions(self, conds):
    #     if conds == None:
    #         conds = []
    #     if not isinstance(conds, list):
    #         conds = [conds]
    #     modifier = 0
    #     for cond in conds:
    #         return sum([ 1 if self.has_condition(conds) or self.has_condition(conds, self.foe) else 0 for c in conds])


    def skill_roll(self, vantage):
        self.roll = self.dice_pool_class(self.health + vantage).roll()
        #print(f"{self.name()} rolls {self.roll} on {self.health + vantage} dice")
        return self.roll

    def foes(self):
        return [c for c in self.simulator.combatants if c.faction != self.faction]

    # General actions
    def wait(self):
        return True

    def move_towards(self, target, distance=None):
        distance = distance if distance else self.speed()
        if target:
            dir = 1 if target.position > self.position else -1
            len = min(abs(target.position - self.position), distance)
            self.position = self.position + dir*len
            return True
        return False

    def move_towards_foe(self):
        return self.move_towards(self.foe)

    def move_away(self, target, distance=None):
        distance = distance if distance else self.speed()
        if target:
            dir = 1 if self.position > target.position else -1
            self.position = self.position + dir*distance
            return True
        return False

    def move_away_from_foe(self):
        return self.move_away(self.foe)

    def takes_damage(self, damage):
        #print(f"{self.name()} takes {damage}! Health {self.health} -> {self.health-damage}")
        if self.health == 0:
            return False

        if self.vitality > 0:
            reduction = min(self.vitality, damage)
            damage -= reduction
            self.vitality -= reduction
        self.health = max(self.health - damage, 0)
        return True

    def defense(self):
        defense = self.data["armor"]
        if self.has_condition("staggered"):
            defense = defense - 1
        return defense

    def distance_to(self, other):
        return abs(other.position - self.position)

    def distance_to_foe(self):
        return self.distance_to(self.foe)

    def speed(self):
        return self.data['speed']

    def pick_action(self):
        return self.basic_attack if self.tactics == None else eval(self.tactics)

    def attack_range(self):
        if len(self.active_items) == 0 or len(self.active_items[0].actions) == 0:
            return range(-1,-1)
        return self.active_items[0].actions[0]['range']

    def describe(self):
        return (f"{bcolors.OKBLUE}{self.name()}{bcolors.ENDC}(health={self.health},pos={self.position},conditions={list(self.conditions.keys())})")

    def extract_data_hash(self):
        cond_str = ','.join([ str(v) for k,v in self.conditions.items() ])
        return { 'health': self.health, 'vitality': self.vitality, 'position': self.position, 'cond': cond_str }

    def opponents(self):
        return self.simulator.foes_of(self)

    def if_foe_and(self, cond, true, false):
        return true if self.foe and cond() else false

    def track_average(self, label, amount):
        (count, sum) = self.averages.get(label, (0,0))
        self.averages[label] = (count+1, sum+amount)

    def average(self, label):
        (count, sum) = self.averages.get(label, (0,0))
        return float(sum)/float(count) if count > 0 else None