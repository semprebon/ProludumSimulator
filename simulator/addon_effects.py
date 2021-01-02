import random

from simulator.condition import Condition


class AddonEffects:
    """ This class contains methods for applying add-on effects as part of an action,
        using any remaining action points"""

    def wound(self, foe):
        if foe == None or foe.health <= 0:
            return False
        foe.takes_damage(1)
        return True

    def recover(self, foe):
        """
        Recover from one condition
        """
        names = [ name for name, cond in self.conditions.items() if cond.severity == Condition.RECOVERABLE ]
        if len(names) == 0:
            return False

        name = random.choice(names)
        del self.conditions[name]
        return True

    def escalate_condition(self, foe):
        """
        Convert a foes recoverable condition to am encounter condition
        """
        if foe == None or foe.health <= 0:
            return False

        names = [ name for name, cond in foe.conditions.items() if cond.severity == Condition.RECOVERABLE ]
        if len(names) == 0:
            return False

        cond = foe.conditions[random.choice(names)]
        foe.add_condition(Condition(cond.name, Condition.ENCOUNTER, cond.other))
        return True
