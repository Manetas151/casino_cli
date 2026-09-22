from dataclasses import dataclass, field
from casino.hand import Hand


@dataclass
class Player:
    name: str
    bankroll: int
    hands: list[Hand] = field(default_factory=list)
    wins: int = 0
    losses: int = 0
    pushes: int = 0
