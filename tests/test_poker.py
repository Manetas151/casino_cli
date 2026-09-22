import unittest

from casino.cards import Card, Rank, Suit
from casino.poker import (
    HandRank,
    evaluate_5,
    best_hand_from_7,
    is_royal,
    dealer_qualifies,
    compare,
)


def c(rank_str, suit):
    rank = next(r for r in Rank if r.value == rank_str)
    return Card(rank, suit)


class TestEvaluate5(unittest.TestCase):
    def test_high_card(self):
        hand = [c("A", Suit.SPADES), c("K", Suit.HEARTS), c("9", Suit.CLUBS), c("5", Suit.DIAMONDS), c("2", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.HIGH_CARD)
        self.assertEqual(tiebreak, (14, 13, 9, 5, 2))

    def test_pair(self):
        hand = [c("K", Suit.SPADES), c("K", Suit.HEARTS), c("9", Suit.CLUBS), c("5", Suit.DIAMONDS), c("2", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.PAIR)
        self.assertEqual(tiebreak, (13, 9, 5, 2))

    def test_two_pair(self):
        hand = [c("K", Suit.SPADES), c("K", Suit.HEARTS), c("9", Suit.CLUBS), c("9", Suit.DIAMONDS), c("2", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.TWO_PAIR)
        self.assertEqual(tiebreak, (13, 9, 2))

    def test_trips(self):
        hand = [c("9", Suit.SPADES), c("9", Suit.HEARTS), c("9", Suit.CLUBS), c("5", Suit.DIAMONDS), c("2", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.TRIPS)
        self.assertEqual(tiebreak, (9, 5, 2))

    def test_straight(self):
        hand = [c("9", Suit.SPADES), c("8", Suit.HEARTS), c("7", Suit.CLUBS), c("6", Suit.DIAMONDS), c("5", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.STRAIGHT)
        self.assertEqual(tiebreak, (9,))

    def test_wheel_straight(self):
        hand = [c("A", Suit.SPADES), c("2", Suit.HEARTS), c("3", Suit.CLUBS), c("4", Suit.DIAMONDS), c("5", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.STRAIGHT)
        self.assertEqual(tiebreak, (5,))

    def test_flush(self):
        hand = [c("A", Suit.SPADES), c("J", Suit.SPADES), c("9", Suit.SPADES), c("5", Suit.SPADES), c("2", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.FLUSH)
        self.assertEqual(tiebreak, (14, 11, 9, 5, 2))

    def test_full_house(self):
        hand = [c("9", Suit.SPADES), c("9", Suit.HEARTS), c("9", Suit.CLUBS), c("5", Suit.DIAMONDS), c("5", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.FULL_HOUSE)
        self.assertEqual(tiebreak, (9, 5))

    def test_quads(self):
        hand = [c("9", Suit.SPADES), c("9", Suit.HEARTS), c("9", Suit.CLUBS), c("9", Suit.DIAMONDS), c("2", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.QUADS)
        self.assertEqual(tiebreak, (9, 2))

    def test_straight_flush(self):
        hand = [c("9", Suit.SPADES), c("8", Suit.SPADES), c("7", Suit.SPADES), c("6", Suit.SPADES), c("5", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.STRAIGHT_FLUSH)
        self.assertEqual(tiebreak, (9,))
        self.assertFalse(is_royal(rank, tiebreak))

    def test_royal_flush(self):
        hand = [c("A", Suit.SPADES), c("K", Suit.SPADES), c("Q", Suit.SPADES), c("J", Suit.SPADES), c("10", Suit.SPADES)]
        rank, tiebreak = evaluate_5(hand)
        self.assertEqual(rank, HandRank.STRAIGHT_FLUSH)
        self.assertTrue(is_royal(rank, tiebreak))


class TestBestHandFrom7(unittest.TestCase):
    def test_picks_best_five_of_seven(self):
        cards = [
            c("A", Suit.SPADES), c("K", Suit.SPADES),  # hole
            c("Q", Suit.SPADES), c("J", Suit.SPADES), c("10", Suit.SPADES),  # flop+turn -> royal flush on board+hole
            c("2", Suit.HEARTS), c("3", Suit.CLUBS),
        ]
        rank, tiebreak, best5 = best_hand_from_7(cards)
        self.assertEqual(rank, HandRank.STRAIGHT_FLUSH)
        self.assertTrue(is_royal(rank, tiebreak))
        self.assertEqual(len(best5), 5)

    def test_ignores_worse_combo(self):
        # Board pairs but hole cards make trips the best available
        cards = [
            c("9", Suit.SPADES), c("9", Suit.HEARTS),  # hole pair
            c("9", Suit.CLUBS), c("2", Suit.DIAMONDS), c("4", Suit.SPADES),
            c("7", Suit.HEARTS), c("K", Suit.CLUBS),
        ]
        rank, tiebreak, _ = best_hand_from_7(cards)
        self.assertEqual(rank, HandRank.TRIPS)
        self.assertEqual(tiebreak[0], 9)


class TestQualifyAndCompare(unittest.TestCase):
    def test_dealer_qualifies_with_pair(self):
        self.assertTrue(dealer_qualifies(HandRank.PAIR))
        self.assertTrue(dealer_qualifies(HandRank.STRAIGHT_FLUSH))

    def test_dealer_does_not_qualify_with_high_card(self):
        self.assertFalse(dealer_qualifies(HandRank.HIGH_CARD))

    def test_compare(self):
        pair = (HandRank.PAIR, (13, 9, 5, 2))
        two_pair = (HandRank.TWO_PAIR, (13, 9, 2))
        self.assertEqual(compare(two_pair, pair), 1)
        self.assertEqual(compare(pair, two_pair), -1)
        self.assertEqual(compare(pair, pair), 0)


if __name__ == "__main__":
    unittest.main()
