import sys
import time
import json
import os

from casino.cards import Deck, Rank
from casino.hand import Hand
from casino.player import Player
from casino.blackjack import (
    deal_initial_hands,
    offer_insurance,
    resolve_insurance,
    play_player_hand_queue,
    play_dealer_hand,
    settle_round,
)
from casino.blackjack_table import redraw_table, prompt_in_frame, SCREEN_ROWS
from casino.screen import check_terminal_size, move_cursor, show_cursor
from casino.holdem_cli import run_holdem
from casino.banners import show_banner
from casino.screen import BOLD_GREEN, RESET

OUTCOME_BANNER = {
    "BLACKJACK_WIN": "win",
    "WIN": "win",
    "PUSH": "draw",
    "LOSS": "lose",
}

PLAYERS_FILE = os.path.join(os.path.dirname(__file__), "players.json")


def load_players() -> dict:
    try:
        with open(PLAYERS_FILE, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"players": []}

    if not isinstance(data, dict) or not isinstance(data.get("players"), list):
        return {"players": []}

    return data


def find_saved_bankroll(players: dict, name: str) -> int | None:
    for entry in players["players"]:
        if entry.get("name") == name:
            try:
                return int(entry.get("money", 0))
            except (TypeError, ValueError):
                return None
    return None


def save_player(players: dict, name: str, bankroll: int) -> None:
    for entry in players["players"]:
        if entry.get("name") == name:
            entry["money"] = bankroll
            break
    else:
        players["players"].append({"name": name, "money": bankroll})

    with open(PLAYERS_FILE, "w") as file:
        json.dump(players, file, indent=4)


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


def prompt_game_choice() -> str:
    print("\nWhich game would you like to play?")
    print("  1) Blackjack")
    print("  2) Ultimate Texas Hold'em")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return "blackjack"
        if choice == "2":
            return "holdem"
        print("Please enter 1 or 2.")


def run_blackjack(player: Player) -> None:
    round_num = 1

    while True:
        player.hands = []
        dealer_hand = Hand()

        if player.bankroll <= 0:
            redraw_table(dealer_hand, True, player, message="You cannot cover any bet. Ending session.")
            prompt_in_frame("Press Enter to see your summary...")
            break

        message = f"Round {round_num}. Enter your bet (0 to stop):"
        bet = None
        while bet is None:
            redraw_table(dealer_hand, True, player, message=message)
            try:
                value = int(prompt_in_frame(f"{BOLD_GREEN}Bet (bankroll ${player.bankroll}, 0 to stop): ${RESET}"))
                if value < 0 or value > player.bankroll:
                    message = f"Please enter a value between 0 and {player.bankroll}."
                    continue
                bet = value
            except ValueError:
                message = "Please enter a valid number."

        if bet == 0:
            redraw_table(dealer_hand, True, player, message="Ending the session.")
            prompt_in_frame("Press Enter to see your summary...")
            break

        player.bankroll -= bet
        player.hands = [Hand(cards=[], bet=bet)]

        deck = Deck.new_shuffled()

        deal_initial_hands(player, dealer_hand, deck)

        dealer_upcard_is_ace = dealer_hand.cards[0].rank == Rank.ACE
        dealer_blackjack = False

        if dealer_upcard_is_ace:
            offer_insurance(player, dealer_hand)
            dealer_blackjack = dealer_hand.is_blackjack()
            resolve_insurance(player, dealer_blackjack)

            if dealer_blackjack:
                redraw_table(dealer_hand, False, player, message="Dealer has Blackjack!")
                prompt_in_frame("Press Enter to continue...")

        if not dealer_blackjack:
            player.hands = play_player_hand_queue(player, dealer_upcard_is_ace, deck, dealer_hand)

            redraw_table(dealer_hand, False, player, message="Dealer reveals hole card...")
            play_dealer_hand(dealer_hand, deck, player)

        outcomes = settle_round(player, dealer_hand)

        time.sleep(1)

        for outcome in outcomes:
            show_banner(OUTCOME_BANNER[outcome])

        redraw_table(
            dealer_hand,
            False,
            player,
            message=f"Round {round_num} complete. Bankroll: ${player.bankroll}",
        )
        prompt_in_frame("Press Enter for next round...")

        round_num += 1


def main():
    print("=== Casino Table Simulator ===\n")

    if not check_terminal_size():
        print(
            "Your terminal is too small for the table view. "
            "Please resize it to at least 120 columns x 40 rows and try again."
        )
        sys.exit(1)

    players = load_players()

    name = prompt_nonempty("\nYour name: ")

    saved_bankroll = find_saved_bankroll(players, name)

    if saved_bankroll is not None:
        print(f"Welcome back, {name}! Loaded bankroll: ${saved_bankroll}")
        bankroll = saved_bankroll
    else:
        bankroll = prompt_int(f"Starting bankroll for {name}: $", 1)

    player = Player(name=name, bankroll=bankroll)
    game_choice = prompt_game_choice()

    try:
        if game_choice == "blackjack":
            run_blackjack(player)
        else:
            run_holdem(player)
    finally:
        save_player(players, player.name, player.bankroll)

    show_cursor()
    move_cursor(SCREEN_ROWS + 2, 1)
    print(f"\n{'=' * 50}")
    print("Session Summary")
    print(f"{'=' * 50}\n")
    print(
        f"{player.name}: {player.wins} wins, {player.losses} losses, {player.pushes} pushes, final: ${player.bankroll}"
    )


if __name__ == "__main__":
    main()
