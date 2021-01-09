# This class represents the state of the actor at the time they are taking an action.
from simulator.actions_mixin import ActionsMixin, STANDARD_ACTIONS
from simulator.condition import ConditionType
from simulator.observations_mixin import ObservationsMixin

class DecisionState(ObservationsMixin, ActionsMixin):
    """ This class represents the state of the actor at the time they are taking
        an action. It provides methods for each action available, as well as
        for any conditionals needed to support the decision tree. This allows
        the decision tree to easily be converted into a python expression of
        method calls on this object, whose execution will enact the decision."""

    # TODO: the GA requires a known set of actions, but the avalable actions are dynamic

    def __init__(self, actor):
        self.actor = actor
        self.foe = actor.foe
        self.simulator = actor.simulator
        self.set_tactics(actor.data['tactics'])
        self._actions = {}
        self._action_properties = {}
        self.create_standard_actions(STANDARD_ACTIONS)
        self.create_actions_for_items(actor.active_items)
        self.create_observations()

    def actions(self):
        return self._actions

    def observations(self):
        return self._observations

    def create_standard_actions(self, names):
        for name in names:
            self.add_action(name, {})

    def create_actions_for_items(self, items):
        for item in items:
            for action in item.actions:
                self.add_action(action['name'], action)

    def add_action(self, name, properties):
        method = self.__getattribute__(name)
        self._actions[name] = method.__get__(method, self)
        self._action_properties[name] = properties

    def create_observations(self):
        self._observations = []
        for name in dir(ObservationsMixin):
            if not name.startswith('_'):
                method = self.__getattribute__(name)
                self._observations.append(method.__get__(method, self))

    def resolve_attribute(self, name, overrides, default):
        attr = overrides.get(name, default)
        if not isinstance(attr, int):
            attr = attr(self)
        return attr

    def resolve_effect(self, name, overrides):
        return overrides.get(name, None)

    def skill_roll(self, overrides):
        vantage = self.resolve_attribute('vantage', overrides, 0)
        roll = self.actor.skill_roll(vantage)
        self.actor.track_average("skill_roll", roll)
        #print(f"{self.actor.name()} rolls {roll} with vantage #{vantage}")
        return roll

    def apply_effect(self, successes, overrides):
        threshold = self.resolve_attribute('threshold', overrides, 2)
        minor_effect = self.resolve_effect('minor_effect', overrides)
        major_effect = self.resolve_effect('major_effect', overrides) or minor_effect
        if successes <= 0:
            #print(f"{self.actor.name()} fails with {successes}")
            self.actor.track_average('major_effect', 0)
            self.actor.track_average('minor_effect', 0)
            pass
        else:
            successes += self.resolve_attribute('successes', overrides, 0)
            if successes >= threshold and major_effect:
                #print(f"{self.actor.name()} gets major effect {major_effect} with {successes}")
                self.actor.track_average('major_effect', 1)
                self.actor.track_average('minor_effect', 0)
                major_effect(self)
            elif successes > 0 and minor_effect:
                #print(f"{self.actor.name()} gets minor effect {minor_effect} with {successes}")
                self.actor.track_average('major_effect', 0)
                self.actor.track_average('minor_effect', 1)
                minor_effect(self)
            else:
                #print(f"effect(s) were missing; successes: {successes} effects: {minor_effect}/{major_effect}")
                pass
        return successes - threshold

    def try_enhancement(self, points, effect, enhancements):
        cost = enhancements.get(effect, None)
        if cost and cost <= points:
                if effect(self):
                    return points - cost
        return points

    def make_enhancements(self, enhancement_points, overrides):
        enhancements = overrides.get('enhancements', {})
        if self.foe and self.foe.health == 1:
            enhancement_points = self.try_enhancement(enhancement_points, self.wound_foe, enhancements)

        enhancement_points = self.try_enhancement(enhancement_points, self.recover, enhancements)

        self.try_enhancement(enhancement_points, self.wound_foe, enhancements)

        for effect, value in enhancements.items():
            if value < enhancement_points:
                enhancement_points = self.try_enhancement(enhancement_points, effect, enhancements)

    def implement_action(self, name, defaults):
        self.actor.track_average(f"action.{name}", 1)
        overrides = { **defaults, **self._action_properties[name] }
        if 'enhancements' in defaults:
            overrides['enhancements'] = { **defaults.get('enhancements', {}), **overrides.get('enhancements', {}) }

        if 'on_start_turn' in overrides:
            overrides['on_start_turn'](self)

        successes = self.skill_roll(overrides)
        if successes <= 0 and 'on_fail' in overrides:
            overrides['on_fail'](self)
        enhancement_points = self.apply_effect(successes, overrides)
        #print(f"{self.actor.name()} got {successes} successes and {enhancement_points} enhancements")
        self.make_enhancements(enhancement_points, overrides)
        if 'on_end_turn' in overrides:
            overrides['on_end_turn'](self)
        if self.actor.has_condition(ConditionType.BLEEDING):
            self.actor.takes_damage(1)

        return successes > 0

    def wound_foe(self):
        if self.foe:
            self.actor.track_average("wound_foe", 1)
            self.foe.takes_damage(1)
        else:
            self.actor.track_average("missing_foe", 1)

    def wound_or_approach_foe(self):
        if self.foe == None:
            self.actor.track_average("missing_foe", 1)
        else:
            self.actor.move_towards_foe()
            if self.if_foe_nearby(True, False):
                self.actor.track_average("wound_foe", 1)
                self.foe.takes_damage(1)
            else:
                self.actor.move_towards_foe()

    def has_melee_attack(self):
        return any(a == 'thrust_attack' or a == 'swing_attack' for a in self.actions().keys())

    def pick_foe(self):
        foes = self.simulator.foes_of(self.actor)
        import random
        if self.has_melee_attack():
            nearby_foes = [ foe for foe in foes if foe.position == self.actor.position ]
            if len(nearby_foes) > 0:
                foes = nearby_foes
        if len(foes) == 0:
            self.foe = None
        else:
            if self.foe not in foes:
                self.foe = random.choice(foes)
        return self.foe

    def execute_action(self):
        action = eval(self.tactics_code)
        success = action()
        return (action.__name__, success)

    def take_turn(self):
        if self.foe == None or self.foe.health == 0:
            self.actor.foe = self.pick_foe()
            self.foe = self.actor.foe

        expiring = self.actor.expiring_conditions()
        before = self.simulator.snapshot_state()
        (action_name, success) = self.execute_action()
        after = self.actor.simulator.snapshot_state()
        if self.simulator and self.simulator.options.get('log_action',False):
            foe_name = self.foe.name() if self.foe else 'None'
            if success:
                conds = [str(v) for v in self.actor.conditions.values()]
                print(f"{self.actor.name()}({self.actor.health}/{self.actor.vitality} {conds})/{action_name} vs {foe_name}: " + self.simulator.determine_state_change(before, after))
            else:
                print(f"{self.actor.name()}({self.actor.conditions})/{action_name} vs {foe_name}: failed")
        self.actor.expire_conditions(expiring)

    def set_tactics(self, tactics):
        import re
        if isinstance(tactics, str):
            code = compile(re.sub(r'(\w+)', r'self.\1', tactics), 'tactics', "eval")
        else:
            raise ValueError("set_tactics only works on string values")
        self.tactics_code = code

    def additional_attack(self):
        print("additional attack not implemented")

