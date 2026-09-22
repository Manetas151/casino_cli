from collections import Counter
from enum import IntEnum
from itertools import combinations

from blackjack.cards import Card, Rank

RANK_VALUE = {
    Rank.TWO: 2, Rank.THREE: 3, Rank.FOUR: 4, Rank.FIVE: 5, Rank.SIX: 6,
    Rank.SEVEN: 7, Rank.EIGHT: 8, Rank.NINE: 9, Rank.TEN: 10,
    Rank.JACK: 11, Rank.QUEEN: 12, Rank.KING: 13, Rank.ACE: 14,
}

RANK_NAME = {
    2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
    8: "Eight", 9: "Nine", 10: "Ten", 11: "Jack", 12: "Queen", 13: "King", 14: "Ace",
}


class HandRank(IntEnum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    TRIPS = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    QUADS = 8
    STRAIGHT_FLUSH = 9


def _straight_high(unique_values: set[int]) -> int | None:
    vals = set(unique_values)
    if 14 in vals:
        vals.add(1)  # wheel: A-2-3-4-5

    for high in range(14, 4, -1):
        if set(range(high - 4, high + 1)).issubset(vals):
            return high
    return None


def evaluate_5(cards: list[Card]) -> tuple[HandRank, tuple[int, ...]]:
    values = sorted((RANK_VALUE[c.rank] for c in cards), reverse=True)
    is_flush = len({c.suit for c in cards}) == 1
    unique_values = set(values)
    straight_high = _straight_high(unique_values) if len(unique_values) == 5 else None

    counts = Counter(values)
    grouped = sorted(counts.items(), key=lambda item: (-item[1], -item[0]))
    pattern = [count for _, count in grouped]

    if is_flush and straight_high is not None:
        return HandRank.STRAIGHT_FLUSH, (straight_high,)
    if pattern == [4, 1]:
        return HandRank.QUADS, (grouped[0][0], grouped[1][0])
    if pattern == [3, 2]:
        return HandRank.FULL_HOUSE, (grouped[0][0], grouped[1][0])
    if is_flush:
        return HandRank.FLUSH, tuple(values)
    if straight_high is not None:
        return HandRank.STRAIGHT, (straight_high,)
    if pattern == [3, 1, 1]:
        kickers = sorted((v for v, c in grouped[1:]), reverse=True)
        return HandRank.TRIPS, (grouped[0][0], *kickers)
    if pattern == [2, 2, 1]:
        pair_vals = sorted((v for v, c in grouped if c == 2), reverse=True)
        kicker = next(v for v, c in grouped if c == 1)
        return HandRank.TWO_PAIR, (*pair_vals, kicker)
    if pattern == [2, 1, 1, 1]:
        kickers = sorted((v for v, c in grouped[1:]), reverse=True)
        return HandRank.PAIR, (grouped[0][0], *kickers)
    return HandRank.HIGH_CARD, tuple(values)


def best_hand_from_7(cards: list[Card]) -> tuple[HandRank, tuple[int, ...], list[Card]]:
    best_rank = None
    best_tiebreak = None
    best_combo = None

    for combo in combinations(cards, 5):
        rank, tiebreak = evaluate_5(list(combo))
        if best_rank is None or (rank, tiebreak) > (best_rank, best_tiebreak):
            best_rank, best_tiebreak, best_combo = rank, tiebreak, combo

    return best_rank, best_tiebreak, list(best_combo)


def is_royal(rank: HandRank, tiebreak: tuple[int, ...]) -> bool:
    return rank == HandRank.STRAIGHT_FLUSH and tiebreak[0] == 14


def dealer_qualifies(rank: HandRank) -> bool:
    return rank >= HandRank.PAIR


def compare(a: tuple[HandRank, tuple[int, ...]], b: tuple[HandRank, tuple[int, ...]]) -> int:
    if a > b:
        return 1
    if a < b:
        return -1
    return 0


def describe_hand(rank: HandRank, tiebreak: tuple[int, ...]) -> str:
    def name(v: int) -> str:
        return RANK_NAME[v]

    if rank == HandRank.STRAIGHT_FLUSH:
        if is_royal(rank, tiebreak):
            return "Royal Flush"
        return f"Straight Flush, {name(tiebreak[0])} High"
    if rank == HandRank.QUADS:
        return f"Four of a Kind, {name(tiebreak[0])}s"
    if rank == HandRank.FULL_HOUSE:
        return f"Full House, {name(tiebreak[0])}s full of {name(tiebreak[1])}s"
    if rank == HandRank.FLUSH:
        return f"Flush, {name(tiebreak[0])} High"
    if rank == HandRank.STRAIGHT:
        return f"Straight, {name(tiebreak[0])} High"
    if rank == HandRank.TRIPS:
        return f"Three of a Kind, {name(tiebreak[0])}s"
    if rank == HandRank.TWO_PAIR:
        return f"Two Pair, {name(tiebreak[0])}s and {name(tiebreak[1])}s"
    if rank == HandRank.PAIR:
        return f"Pair of {name(tiebreak[0])}s"
    return f"High Card, {name(tiebreak[0])}"
