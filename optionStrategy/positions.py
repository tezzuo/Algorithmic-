from optionStrategy.position import Position


class Positions:
    def __init__(self, position: Position, quantity: int):
        self.position = position
        self.quantity = quantity