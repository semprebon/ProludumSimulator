def key(name, other):
    '''Returns an indentifer for the condition to differentiates it from others'''
    return name if other == None else f"{name}|{id(other)}"


class Condition:

    FLEETING = 0        # lasts until end of actors next turn
    RECOVERABLE = 1     # lasts until actor successfully makes a recovery action
    ENCOUNTER = 2       # lasts until the end of the encounter

    def __init__(self, name, severity=FLEETING, other=None):
        if not isinstance(severity, int):
            raise ValueError
        self.name = name
        self.severity = severity
        self.other = other


    def key(self):
        '''Returns an indentifer for the condition to differentiat it from others'''
        return key(self.name, self.other)

