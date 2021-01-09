""""""
from simulator.condition import Condition, ConditionType


class ObservationsMixin:
    """ This class contains predicte methods used by tactics to make decisions.
        Putting these methods in a seperate mixin class allows them to be
        programattically extracted for use in the GP optimizer"""

    def if_staggered(self, t, f):
        return t if self.actor.has_condition(ConditionType.STAGGERED) else f

    def if_hindered(self, t, f):
        return t if self.actor.has_condition(ConditionType.HINDERED) else f

    def if_near_death(self, t, f):
        return t if self.actor.health == 1 else f

    def if_foe_staggered(self, t, f):
        return t if self.actor.foe and self.actor.foe.has_condition(ConditionType.STAGGERED) else f

    def if_foe_hindered(self, a, b):
        if self.foe:
            return a if self.foe and self.foe.has_condition(ConditionType.HINDERED) else b
        else:
            return b

    def if_foe_defending(self, a, b):
        if self.foe:
            return a if self.foe and self.foe.has_condition(ConditionType.DEFENDING) else b
        else:
            return b

    def if_foe_near_death(self, a, b):
        if self.foe:
            return a if self.foe and self.foe.health == 1 else b
        else:
            return b

    def if_foe_prepared(self, a, b):
        if self.foe:
            return a if self.foe.has_condition(ConditionType.PREPARED_FOR, self) else b
        else:
            return b

    def if_multiple_attackers(self, a, b):
        return a if len(self.actor.opponents()) > 1 else b

    def if_prepared_for_foe(self, a, b):
        if self.foe:
            return a if self.actor.has_condition(ConditionType.PREPARED_FOR, self.foe) else b
        else:
            return b

    # TODO: no way currently to implement this
    def if_has_melee_weapon(self, a, b):
        return a if self.has_melee_attack() else b

    def if_foe_adjacent(self, a, b):
        if self.foe:
            return a if self.actor.distance_to_foe() <= 1 else b
        else:
            return b

    def if_foe_in_move_range(self, a, b):
        if self.foe:
            return a if self.actor.distance_to_foe() <= self.actor.speed() else b
        else:
            return b

    def if_foe_in_attack_range(self, a, b):
        if self.foe:
            return a if self.actor.distance_to_foe() in self.actor.attack_range() else b
        else:
            return b

