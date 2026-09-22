from dataclasses import dataclass, field
from casino.cards import Card, Rank


@dataclass
class Hand:
    cards: list[Card] = field(default_factory=list)
    bet: int = 0
    insurance_bet: int = 0
    doubled: bool = False
    is_split_hand: bool = False
    split_from_aces: bool = False
    done: bool = False

    def value(self) -> tuple[int, bool]:
        if not self.cards:
            return 0, False

        total = sum(card.blackjack_value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == Rank.ACE)
        is_soft = False

        if aces > 0 and total + 10 <= 21:
            total += 10
            is_soft = True

        return total, is_soft

    def is_bust(self) -> bool:
        total, _ = self.value()
        return total > 21

    def is_blackjack(self) -> bool:
        if len(self.cards) != 2 or self.is_split_hand:
            return False
        total, _ = self.value()
        return total == 21

    def can_split(self) -> bool:
        if len(self.cards) != 2 or self.is_split_hand or self.doubled:
            return False
        return self.cards[0].rank == self.cards[1].rank

    def display_total(self) -> str:
        total, is_soft = self.value()

        if self.is_bust():
            return f"{total} (bust)"
        elif self.is_blackjack():
            return "21 (Blackjack)"
        elif is_soft:
            return f"{total} (soft)"
        else:
            return str(total)
