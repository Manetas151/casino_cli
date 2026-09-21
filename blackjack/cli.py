from blackjack.cards import Deck, Rank
from blackjack.hand import Hand
from blackjack.player import Player
from blackjack.game import (
    deal_initial_hands,
    offer_insurance,
    resolve_insurance,
    play_player_hand_queue,
    play_dealer_hand,
    settle_round,
)
from blackjack.rendering import print_hand


def prompt_int(prompt_text: str, min_val: int = 0, max_val: int = None) -> int:
    while True:
        try:
            value = int(input(prompt_text))
            if value < min_val or (max_val is not None and value > max_val):
                print(f"Please enter a value between {min_val} and {max_val}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def prompt_nonempty(prompt_text: str) -> str:
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Please enter a non-empty value.")


def main():
    print("=== Blackjack Simulator ===\n")

    num_players = prompt_int("How many players? (1-5): ", 1, 5)
    players = []

    for i in range(num_players):
        name = prompt_nonempty(f"Player {i + 1} name: ")
        bankroll = prompt_int(f"Starting bankroll for {name}: $", 1)
        players.append(Player(name=name, bankroll=bankroll))

    round_num = 1

    while True:
        print(f"\n{'=' * 50}")
        print(f"Round {round_num}")
        print(f"{'=' * 50}\n")

        stop = False
        for player in players:
            if player.bankroll <= 0:
                print(f"{player.name} cannot cover any bet. Ending session.")
                stop = True
                break

            bet = prompt_int(
                f"{player.name}, enter your bet (bankroll ${player.bankroll}, 0 to stop): $",
                0,
                player.bankroll,
            )

            if bet == 0:
                print("A player entered 0 — ending the session for everyone.")
                stop = True
                break

            player.bankroll -= bet
            player.hands = [Hand(cards=[], bet=bet)]

        if stop:
            break

        deck = Deck.new_shuffled()

        dealer_hand = Hand()

        deal_initial_hands(players, dealer_hand, deck)

        print_hand("Dealer", dealer_hand.cards, hide_last=True, show_total=False)
        for player in players:
            print_hand(
                player.name,
                player.hands[0].cards,
                show_total=True,
                total_str=player.hands[0].display_total(),
            )

        dealer_upcard_is_ace = dealer_hand.cards[0].rank == Rank.ACE
        dealer_blackjack = False

        if dealer_upcard_is_ace:
            offer_insurance(players)
            dealer_blackjack = dealer_hand.is_blackjack()
            resolve_insurance(players, dealer_blackjack)

            if dealer_blackjack:
                print("\nDealer has Blackjack!")
                print_hand(
                    "Dealer",
                    dealer_hand.cards,
                    show_total=True,
                    total_str=dealer_hand.display_total(),
                )

        if not dealer_blackjack:
            for player in players:
                player.hands = play_player_hand_queue(player, dealer_upcard_is_ace, deck)

            print_hand(
                "Dealer",
                dealer_hand.cards,
                show_total=True,
                total_str=dealer_hand.display_total(),
            )
            play_dealer_hand(dealer_hand, deck)
            print_hand(
                "Dealer (final)",
                dealer_hand.cards,
                show_total=True,
                total_str=dealer_hand.display_total(),
            )

        settle_round(players, dealer_hand)

        print("\n--- Round Results ---")
        for player in players:
            print(f"{player.name}: ${player.bankroll}")

        round_num += 1

    print(f"\n{'=' * 50}")
    print("Session Summary")
    print(f"{'=' * 50}\n")

    for player in players:
        print(
            f"{player.name}: {player.wins} wins, {player.losses} losses, {player.pushes} pushes, final: ${player.bankroll}"
        )


if __name__ == "__main__":
    main()
