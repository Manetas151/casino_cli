from enum import Enum
from dataclasses import dataclass
import random


class Suit(Enum):
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"


class Rank(Enum):
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    def __str__(self):
        return f"{self.rank.value}{self.suit.value}"

    def blackjack_value(self):
        if self.rank == Rank.ACE:
            return 1
        elif self.rank in (Rank.JACK, Rank.QUEEN, Rank.KING):
            return 10
        else:
            return int(self.rank.value)


class Deck:
    def __init__(self, cards: list[Card]):
        self.cards = cards

    @classmethod
    def new_shuffled(cls):
        cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        random.shuffle(cards)
        return cls(cards)

    def deal(self, count: int) -> list[Card]:
        dealt = self.cards[:count]
        self.cards = self.cards[count:]
        return dealt

    def has_cards(self, count: int = 1) -> bool:
        return len(self.cards) >= count
