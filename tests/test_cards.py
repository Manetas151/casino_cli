import unittest
from casino.cards import Deck, Card, Rank, Suit


class TestDeck(unittest.TestCase):
    def test_new_shuffled_has_52_cards(self):
        deck = Deck.new_shuffled()
        self.assertEqual(len(deck.cards), 52)

    def test_new_shuffled_has_all_unique_cards(self):
        deck = Deck.new_shuffled()
        self.assertEqual(len(set(deck.cards)), 52)

    def test_deal_removes_cards(self):
        deck = Deck.new_shuffled()
        initial_count = len(deck.cards)
        dealt = deck.deal(5)
        self.assertEqual(len(dealt), 5)
        self.assertEqual(len(deck.cards), initial_count - 5)

    def test_deal_no_duplication(self):
        deck = Deck.new_shuffled()
        dealt1 = deck.deal(26)
        dealt2 = deck.deal(26)
        all_dealt = dealt1 + dealt2
        self.assertEqual(len(set(all_dealt)), 52)


if __name__ == "__main__":
    unittest.main()
