import unittest
from blackjack.hand import Hand
from blackjack.cards import Card, Rank, Suit


class TestHand(unittest.TestCase):
    def test_hard_total(self):
        hand = Hand(cards=[Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])
        total, is_soft = hand.value()
        self.assertEqual(total, 17)
        self.assertFalse(is_soft)

    def test_soft_total(self):
        hand = Hand(
            cards=[Card(Rank.ACE, Suit.SPADES), Card(Rank.SIX, Suit.HEARTS)]
        )
        total, is_soft = hand.value()
        self.assertEqual(total, 17)
        self.assertTrue(is_soft)

    def test_soft_to_hard_conversion(self):
        hand = Hand(
            cards=[
                Card(Rank.ACE, Suit.SPADES),
                Card(Rank.SIX, Suit.HEARTS),
                Card(Rank.TEN, Suit.DIAMONDS),
            ]
        )
        total, is_soft = hand.value()
        self.assertEqual(total, 17)
        self.assertFalse(is_soft)

    def test_multiple_aces(self):
        hand = Hand(
            cards=[
                Card(Rank.ACE, Suit.SPADES),
                Card(Rank.ACE, Suit.HEARTS),
                Card(Rank.NINE, Suit.DIAMONDS),
            ]
        )
        total, is_soft = hand.value()
        self.assertEqual(total, 21)
        self.assertTrue(is_soft)

    def test_bust(self):
        hand = Hand(
            cards=[Card(Rank.TEN, Suit.SPADES), Card(Rank.KING, Suit.HEARTS), Card(Rank.FIVE, Suit.DIAMONDS)]
        )
        self.assertTrue(hand.is_bust())

    def test_is_blackjack(self):
        hand = Hand(cards=[Card(Rank.ACE, Suit.SPADES), Card(Rank.TEN, Suit.HEARTS)])
        self.assertTrue(hand.is_blackjack())

    def test_split_hand_is_not_blackjack(self):
        hand = Hand(
            cards=[Card(Rank.ACE, Suit.SPADES), Card(Rank.TEN, Suit.HEARTS)],
            is_split_hand=True,
        )
        self.assertFalse(hand.is_blackjack())

    def test_can_split_matching_ranks(self):
        hand = Hand(cards=[Card(Rank.EIGHT, Suit.SPADES), Card(Rank.EIGHT, Suit.HEARTS)])
        self.assertTrue(hand.can_split())

    def test_cannot_split_different_ranks(self):
        hand = Hand(
            cards=[Card(Rank.TEN, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)]
        )
        self.assertFalse(hand.can_split())

    def test_cannot_split_already_split_hand(self):
        hand = Hand(
            cards=[Card(Rank.EIGHT, Suit.SPADES), Card(Rank.EIGHT, Suit.HEARTS)],
            is_split_hand=True,
        )
        self.assertFalse(hand.can_split())


if __name__ == "__main__":
    unittest.main()
