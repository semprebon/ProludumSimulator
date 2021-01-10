class FixedDicePool:

    roll_value = 0

    def __init__(self, count):
        self.count = 0

    def roll(self):
        if isinstance(self.roll_value, int):
            return self.roll_value
        else:
            return self.roll_value[self.count]
            self.count = self.count+1
            if count == len(self.roll_value):
                self.count = 0

