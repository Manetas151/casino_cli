import unittest

from casino.cards import Card, Deck, Rank, Suit
from casino.hand import Hand
from casino.player import Player
from casino.blackjack import settle_round, play_dealer_hand


def make_player(cards, bet=50, bankroll=100):
    player = Player(name="Test", bankroll=bankroll)
    player.hands = [Hand(cards=cards, bet=bet)]
    return player


class TestSettleRound(unittest.TestCase):
    def test_player_bust_and_dealer_bust_is_a_loss(self):
        # Regression test: player busting must always lose, even if the
        # dealer also busts afterward — previously the dealer-bust check
        # ran first and incorrectly turned this into a win.
        player = make_player([Card(Rank.TEN, Suit.SPADES), Card(Rank.KING, Suit.HEARTS), Card(Rank.FIVE, Suit.CLUBS)])
        dealer_hand = Hand(
            cards=[Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.KING, Suit.CLUBS), Card(Rank.THREE, Suit.SPADES)]
        )

        self.assertTrue(player.hands[0].is_bust())
        self.assertTrue(dealer_hand.is_bust())

        outcomes = settle_round(player, dealer_hand)

        self.assertEqual(outcomes, ["LOSS"])
        self.assertEqual(player.bankroll, 100)
        self.assertEqual(player.losses, 1)
        self.assertEqual(player.wins, 0)

    def test_player_bust_dealer_not_bust_is_a_loss(self):
        player = make_player([Card(Rank.TEN, Suit.SPADES), Card(Rank.KING, Suit.HEARTS), Card(Rank.FIVE, Suit.CLUBS)])
        dealer_hand = Hand(cards=[Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.EIGHT, Suit.CLUBS)])

        outcomes = settle_round(player, dealer_hand)

        self.assertEqual(outcomes, ["LOSS"])
        self.assertEqual(player.bankroll, 100)

    def test_dealer_bust_player_not_bust_is_a_win(self):
        player = make_player([Card(Rank.TEN, Suit.SPADES), Card(Rank.NINE, Suit.HEARTS)])
        dealer_hand = Hand(
            cards=[Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.KING, Suit.CLUBS), Card(Rank.THREE, Suit.SPADES)]
        )

        outcomes = settle_round(player, dealer_hand)

        self.assertEqual(outcomes, ["WIN"])
        self.assertEqual(player.bankroll, 200)

    def test_push(self):
        player = make_player([Card(Rank.TEN, Suit.SPADES), Card(Rank.EIGHT, Suit.HEARTS)])
        dealer_hand = Hand(cards=[Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.EIGHT, Suit.CLUBS)])

        outcomes = settle_round(player, dealer_hand)

        self.assertEqual(outcomes, ["PUSH"])
        self.assertEqual(player.bankroll, 150)

    def test_blackjack_pays_three_to_two(self):
        player = make_player([Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)])
        dealer_hand = Hand(cards=[Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.EIGHT, Suit.CLUBS)])

        outcomes = settle_round(player, dealer_hand)

        self.assertEqual(outcomes, ["BLACKJACK_WIN"])
        self.assertEqual(player.bankroll, 100 + 50 + 75)


class TestPlayDealerHand(unittest.TestCase):
    def test_dealer_does_not_draw_when_all_player_hands_are_bust(self):
        player = make_player([Card(Rank.TEN, Suit.SPADES), Card(Rank.KING, Suit.HEARTS), Card(Rank.FIVE, Suit.CLUBS)])
        dealer_hand = Hand(cards=[Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.FIVE, Suit.CLUBS)])
        deck = Deck.new_shuffled()
        cards_before = len(deck.cards)

        play_dealer_hand(dealer_hand, deck, player)

        self.assertEqual(len(dealer_hand.cards), 2)
        self.assertEqual(len(deck.cards), cards_before)

    def test_dealer_draws_normally_when_player_is_not_bust(self):
        player = make_player([Card(Rank.TEN, Suit.SPADES), Card(Rank.NINE, Suit.HEARTS)])
        dealer_hand = Hand(cards=[Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.FIVE, Suit.CLUBS)])
        deck = Deck.new_shuffled()

        play_dealer_hand(dealer_hand, deck, player)

        total, _ = dealer_hand.value()
        self.assertGreaterEqual(total, 17)


if __name__ == "__main__":
    unittest.main()
