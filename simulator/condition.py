from enum import Enum


def key(name, other):
    '''Returns an indentifer for the condition to differentiates it from others'''
    return name if other == None else f"{name}|{id(other)}"


# condition severities
FLEETING = 0  # lasts until end of actors next turn after it is triggeed
RECOVERABLE = 1  # lasts until actor successfully makes a recovery action
ENCOUNTER = 2  # lasts until the end of the encounter

class ConditionType(Enum):
    """ The various condition types """

    STAGGERED = (RECOVERABLE),     # Adds 1 to successes of a successful attack on the actor. Note that a successful
                        # attack on a staggard foe will increase a 1 success to a 2, resulting in a major
                        # effect
    HINDERED = (RECOVERABLE),      # adds disadvantage (1 less dice rolled) to actions by the actor. Subsequent HINDERED
                        # effect results in a wound.
    BLEEDING = (RECOVERABLE),      # Foe takes 1 wound at the end of their turn if they make an attack
    DEFENDING = (FLEETING, True, True),     # Adds disadvantage to attacks against the actor by the target
    PREPARED_FOR = (FLEETING, True, True)   # Improves subsequent action against specific foe, depending on weapon
                        # On ranged attacks, prepared (i.e. aim) adds advantage, making success more likely
                        # On melee attacks, prepared (i.e., windup) adds to success, making damage more likely
                        # for a successful attack

    def __init__(self, duration=RECOVERABLE, directed=False, beneficial=False):
        self.duration = duration
        self.directed = directed
        self.beneficial = beneficial

class Condition:
    def __init__(self, condition_type, other=None):
        if condition_type.directed and other == None:
            raise ValueError(f"Condition type {condition_type.name} requires a subject but none given")
        if not condition_type.directed and other != None:
            raise ValueError(f"Condition type {condition_type.name} prohibits a subject but given {other.name()}")

        self.condition_type = condition_type
        self.other = other

    def key(self):
        return key(self.condition_type.name, self.other)

    def as_dict(self):
        other = self.other.name() if self.other else None
        return { 'name': self.name, 'severity': self.severity, 'other': other }

    def duration(self):
        return self.condition_type.duration

    def __str__(self):
        return f"{self.condition_type.name} {f'>{self.other.name()}' if self.other else ''}"
