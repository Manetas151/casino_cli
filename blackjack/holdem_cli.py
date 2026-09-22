from blackjack.cards import Deck
from blackjack.player import Player
from blackjack.holdem import HoldemState, settle_round
from blackjack.holdem_table import redraw_holdem_table, prompt_in_frame, deal_card_with_delay


def _make_redraw(player: Player, state: HoldemState):
    def redraw(message="", hide_dealer=True, dealer_desc="", player_desc=""):
        redraw_holdem_table(
            state.player_cards,
            state.dealer_cards,
            hide_dealer,
            state.community,
            state.ante,
            state.blind,
            state.play_bet,
            player.bankroll,
            message=message,
            dealer_description=dealer_desc,
            player_description=player_desc,
        )

    return redraw


def _prompt_ante(player: Player, round_num: int, redraw) -> int:
    message = f"Round {round_num}. Enter your Ante (Blind matches it, 0 to stop):"
    while True:
        redraw(message=message)
        max_ante = player.bankroll // 2
        try:
            value = int(prompt_in_frame(f"Ante (max ${max_ante}, 0 to stop): $"))
            if value < 0 or value > max_ante:
                message = f"Please enter a value between 0 and {max_ante} (need Ante+Blind)."
                continue
            return value
        except ValueError:
            message = "Please enter a valid number."


def _prompt_preflop(player: Player, state: HoldemState, redraw) -> str:
    can_bet = player.bankroll >= state.ante * 4
    options = "(C)heck or (B)et 4x Ante" if can_bet else "(C)heck — not enough bankroll to bet 4x"
    message = f"Your hand is dealt. {options}."
    while True:
        redraw(message=message)
        choice = prompt_in_frame("Check or Bet: ").strip().upper()
        if choice == "C":
            return "check"
        if choice == "B" and can_bet:
            return "bet"
        message = "Invalid choice."


def _prompt_flop(player: Player, state: HoldemState, redraw) -> str:
    can_bet = player.bankroll >= state.ante * 2
    options = "(C)heck or (B)et 2x Ante" if can_bet else "(C)heck — not enough bankroll to bet 2x"
    message = f"Flop is out. {options}."
    while True:
        redraw(message=message)
        choice = prompt_in_frame("Check or Bet: ").strip().upper()
        if choice == "C":
            return "check"
        if choice == "B" and can_bet:
            return "bet"
        message = "Invalid choice."


def _prompt_river(player: Player, state: HoldemState, redraw) -> str:
    can_bet = player.bankroll >= state.ante
    if not can_bet:
        return "fold"
    message = "Final decision. (B)et 1x Ante or (F)old."
    while True:
        redraw(message=message)
        choice = prompt_in_frame("Bet or Fold: ").strip().upper()
        if choice == "B":
            return "bet"
        if choice == "F":
            return "fold"
        message = "Invalid choice."


def run_holdem(player: Player) -> None:
    round_num = 1

    while True:
        state = HoldemState()
        redraw = _make_redraw(player, state)

        if player.bankroll < 2:
            redraw(message="You cannot cover an Ante + Blind. Ending session.")
            prompt_in_frame("Press Enter to see your summary...")
            break

        ante = _prompt_ante(player, round_num, redraw)
        if ante == 0:
            redraw(message="Ending the session.")
            prompt_in_frame("Press Enter to see your summary...")
            break

        state.ante = ante
        state.blind = ante
        player.bankroll -= ante * 2

        deck = Deck.new_shuffled()

        deal_card_with_delay(state.player_cards, deck, lambda: redraw("Dealing your hand..."))
        deal_card_with_delay(state.dealer_cards, deck, lambda: redraw("Dealing your hand..."))
        deal_card_with_delay(state.player_cards, deck, lambda: redraw("Dealing your hand..."))
        deal_card_with_delay(state.dealer_cards, deck, lambda: redraw("Dealing your hand..."))

        preflop = _prompt_preflop(player, state, redraw)

        if preflop == "bet":
            state.play_bet = ante * 4
            player.bankroll -= state.play_bet
            for _ in range(3):
                deal_card_with_delay(state.community, deck, lambda: redraw("Dealing the board..."))
            deal_card_with_delay(state.community, deck, lambda: redraw("Dealing the board..."))
            deal_card_with_delay(state.community, deck, lambda: redraw("Dealing the board..."))
        else:
            for _ in range(3):
                deal_card_with_delay(state.community, deck, lambda: redraw("Dealing the flop..."))

            flop_choice = _prompt_flop(player, state, redraw)

            if flop_choice == "bet":
                state.play_bet = ante * 2
                player.bankroll -= state.play_bet
                deal_card_with_delay(state.community, deck, lambda: redraw("Dealing the turn..."))
                deal_card_with_delay(state.community, deck, lambda: redraw("Dealing the river..."))
            else:
                deal_card_with_delay(state.community, deck, lambda: redraw("Dealing the turn..."))
                deal_card_with_delay(state.community, deck, lambda: redraw("Dealing the river..."))

                river_choice = _prompt_river(player, state, redraw)

                if river_choice == "fold":
                    state.folded = True
                else:
                    state.play_bet = ante
                    player.bankroll -= state.play_bet

        message, dealer_desc, player_desc = settle_round(player, state)
        redraw(message=message, hide_dealer=state.folded, dealer_desc=dealer_desc, player_desc=player_desc)
        prompt_in_frame("Press Enter for next round...")

        round_num += 1
