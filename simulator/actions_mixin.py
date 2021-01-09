from simulator.condition import ConditionType, Condition

RECOVER_FROM_CONDITION_EFFECT = lambda ds: ds.actor.recover_from_condition()
MOVE_TOWARDS_EFFECT = lambda ds: ds.actor.move_towards_foe()
WOUND_FOE_EFFECT = lambda ds: ds.wound_foe()
WOUND_OR_APPROACH_EFFECT = lambda ds: ds.wound_or_approach_foe()
MOVE_AWAY_EFFECT = lambda ds: ds.actor.move_away_from_foe()

""" A collection of support methods for creating effects more complex than
    a simple method call. Each of these returns a lambda taking the
    decision state as an argument"""

def apply_condition_to_actor_effect(condition):
    if condition.directed:
        return lambda ds: ds.actor.add_condition(Condition(condition, ds.foe))
    else:
        return lambda ds: ds.actor.add_condition(Condition(condition))

def apply_condition_to_foe_effect(condition, other=None):
    return if_foe(lambda ds: ds.foe.add_condition(Condition(condition, other)))

def if_foe(effect):
    return lambda ds: effect(ds) if ds.foe else None

def condition_with_escalation(condition, escalation):
    return lambda ds: if_foe(escalation(ds)) if ds.foe.has_condition(condition) else apply_condition_to_foe_effect(condition)(ds)

def actor_condition_modifier(cond, value):
    if cond.directed:
        return lambda ds: value if ds.actor.has_condition(cond, ds.foe) else 0
    else:
        return lambda ds: value if ds.actor.has_condition(cond, None) else 0

def foe_condition_modifier(cond, value):
    if cond.directed:
        return lambda ds: value if ds.foe and ds.foe.has_condition(cond, ds.actor) else 0
    else:
        return lambda ds: value if ds.foe and ds.foe.has_condition(cond, None) else 0

def multimove(*args):
    return lambda ds: args[0](ds) if len(args) == 1 else args[0](ds) and multimove(*args[1:])

def attack_defaults():
    return ATTACK_DEFAULTS

ATTACK_DEFAULTS = {
        "vantage": actor_condition_modifier(ConditionType.HINDERED, 1),
        "threshold": lambda ds: 2 - foe_condition_modifier(ConditionType.STAGGERED, 1)(ds),
        "major_effect": WOUND_FOE_EFFECT
    }

class ActionsMixin:
    """ This class is mixed into DecisionState and provides the various action
        methods that are ultimately called when the decision tree is parsed and
        executed.

        In general, each method calls take_action with certain appropriate
        defaults for an action of that type."""

    # Standard actor actions
    def recover(self):
        """end one or more RECOVERABLE conditions based on an action roll
        """
        defaults = {
            'enhancements': { RECOVER_FROM_CONDITION_EFFECT: 1} }

        return self.implement_action('recover', defaults)

    def retreat(self):
        """move away from current foe"""
        move = lambda ds: ds.actor.move_away_from_foe()
        defaults = {
            'threshold': 1,
            'minor_effect': MOVE_AWAY_EFFECT,
            'major_effect': multimove(MOVE_AWAY_EFFECT, MOVE_AWAY_EFFECT),
            'enhancements': { RECOVER_FROM_CONDITION_EFFECT: 1 }}
        return self.implement_action('retreat', defaults)

    def approach(self):
        """move toward foe"""
        MOVE_TOWARDS_EFFECT(self)
        MOVE_TOWARDS_EFFECT(self)
        defaults = {
            'threshold': 1,
            'minor_effect': MOVE_TOWARDS_EFFECT,
            'major_effect': None,
            'enhancements': { RECOVER_FROM_CONDITION_EFFECT: 1 } }
        return self.implement_action('approach', defaults)

    def charge(self):
        """charge at foe"""
        if self.actor.distance_to(self.foe) > 1:
            return self.approach()
        defaults = { **ATTACK_DEFAULTS, **{ 'minor_effect': MOVE_TOWARDS_EFFECT, 'major_effect': WOUND_OR_APPROACH_EFFECT } }

    def wait(self):
        """do nothing"""
        return True

    # Weapon actions
    def melee_actions(self, action):
        if self.if_foe_in_move_range():
            action();
        else:
            self.approach()

    def thrust_attack(self):
        if self.if_foe_in_move_range(True, False):
            return self.implement_action('thrust_attack', ATTACK_DEFAULTS)
        else:
            return self.approach()

    def swing_attack(self):
        if self.if_foe_in_move_range(True, False):
            return self.implement_action('swing_attack', ATTACK_DEFAULTS)
        else:
            return self.approach()

    def defend(self):
        defaults = {
            "minor_effect": apply_condition_to_actor_effect(ConditionType.DEFENDING),
            "major_effect": None,
            "enhancements": { RECOVER_FROM_CONDITION_EFFECT: 1 } }
        return self.implement_action('defend', defaults)

    def defensive_attack(self):
        if self.foe_nearby(True, False):
            return self.implement_action('defensive_attack', ATTACK_DEFAULTS)
        else:
            return self.approach()

    def prepare(self):
        defaults = {
            'threshold': 1,
            'minor_effect': apply_condition_to_actor_effect(ConditionType.PREPARED_FOR),
            'major_effect': None }
        if self.foe:
            return self.implement_action('prepare', defaults)
        else:
            return self.wait()

    def bite_attack(self):
        if self.foe_nearby(True, False):
            return self.implement_action('bite_attack', ATTACK_DEFAULTS)
        else:
            return self.approach()

    def ranged_attack(self):
        defaults = {
            'vantage': actor_condition_modifier(ConditionType.PREPARED_FOR, 2),
            'threshold': 2,
            'minor_effect': condition_with_escalation(ConditionType.HINDERED, WOUND_FOE_EFFECT),
            'major_effect': WOUND_FOE_EFFECT }
        return self.implement_action('ranged_attack', defaults)

    def unarmed_attack(self):
        if self.foe_nearby(True, False):
            return self.implement_action('unarmed_attack', ATTACK_DEFAULTS)
        else:
            return self.approach()

    def kick_attack(self):
        if self.foe_nearby(True, False):
            return self.implement_action('kick_attack', ATTACK_DEFAULTS)
        else:
            return self.approach()

    def secondary_attack(self):
        return self.implement_action('secondary_attack', ATTACK_DEFAULTS)

STANDARD_ACTIONS = [ "recover", "retreat", "approach", "wait" ]
