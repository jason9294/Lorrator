import random
from dataclasses import dataclass


@dataclass
class DiceResult:
    rolls: list[int]
    total: int
    num_dice: int
    num_sides: int
    notation: str


def dice(num: int, sides: int) -> DiceResult:
    if num <= 0:
        raise ValueError("Number of dice must be greater than 0")
    if sides <= 0:
        raise ValueError("Number of sides must be greater than 0")

    rolls = [random.randint(1, sides) for _ in range(num)]
    return DiceResult(
        rolls=rolls,
        total=sum(rolls),
        num_dice=num,
        num_sides=sides,
        notation=f"{num}d{sides}",
    )
