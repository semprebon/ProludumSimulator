# Condition Severities
import random

from simulator import actor
from simulator.actions_mixin import *
from simulator.condition import Condition, ConditionType

Balanced = { 'enhancements': {} }
Attack = attack_defaults()
Melee = { 'range': range(1,2) }
ThrowRange = { 'range': range(2,4) }
LongRange = { 'range': range(2,61) }

# damage types
Impaling = { 'minor_effect': condition_with_escalation(ConditionType.HINDERED, WOUND_FOE_EFFECT)}
Cutting = { 'minor_effect': apply_condition_to_foe_effect(ConditionType.BLEEDING) }
Crushing = { 'minor_effect': apply_condition_to_foe_effect(ConditionType.STAGGERED) }

# Preparation effected
AimBonus = { 'vantage': actor_condition_modifier(ConditionType.PREPARED_FOR, 1) }
WindupBonus = { 'success': actor_condition_modifier(ConditionType.PREPARED_FOR, 1) }
AdditionalAttack = { 'enhancements': { lambda ds: ds.additional_attack(): 1 } }

class Item:

    def __init__(self, *actions):
        self.actions = actions

    @classmethod
    def define_action(cls, name, property_sets=[]):
        properties = { 'name': name }
        for set in property_sets: # merge properties
            properties = { **properties, **set }
        return properties

ITEMS = {
    'Longbow': Item(
        Item.define_action("ranged_attack", [Attack, LongRange, Impaling, AimBonus]),
        Item.define_action("prepare")),
    'Knife': Item(
        Item.define_action("thrust_attack", [Attack, Melee, Impaling, AdditionalAttack]),
        Item.define_action("swing_attack", [Attack, Melee, Cutting, AdditionalAttack])),
    'LongSword': Item(
        Item.define_action("thrust_attack", [Attack, Melee, Balanced, Impaling]),
        Item.define_action("swing_attack", [Attack, Melee, Balanced, Cutting]),
        Item.define_action("defend", [{}])),
    'HeavyMaul': Item(
        Item.define_action("swing_attack", [Attack, Melee, Crushing, WindupBonus]),
        Item.define_action("prepare")),
    'ShortSword': Item(
        Item.define_action("thrust_attack", [Attack, Melee, Impaling, AdditionalAttack]),
        Item.define_action("swing_attack", [Attack, Melee, Cutting, AdditionalAttack])),
    'Bite': Item(
        Item.define_action("bite_attack", [Attack, Melee, Impaling])),
    'Shield': Item(
        Item.define_action("defend", [{}])),
}

