from collections import deque
from casino.cards import Deck, Rank
from casino.hand import Hand
from casino.player import Player
from casino.table import deal_card_with_delay, redraw_table, prompt_in_frame


def deal_initial_hands(player: Player, dealer_hand: Hand, deck: Deck):
    for _ in range(2):
        deal_card_with_delay(player.hands[0], deck, dealer_hand, player, hide_dealer_hole=True)
        deal_card_with_delay(dealer_hand, deck, dealer_hand, player, hide_dealer_hole=True)


def offer_insurance(player: Player, dealer_hand: Hand):
    hand = player.hands[0]
    max_insurance = hand.bet // 2
    if max_insurance == 0:
        return

    message = f"Dealer shows an Ace. Insurance? (0-{max_insurance}, 0 to decline)"
    while True:
        redraw_table(dealer_hand, True, player, message=message)
        try:
            amount = int(prompt_in_frame(f"Insurance bet ($0-{max_insurance}): $"))
            if amount < 0 or amount > max_insurance or amount > player.bankroll:
                message = f"Invalid amount. Must be 0-${max_insurance} and within bankroll."
                continue
            hand.insurance_bet = amount
            player.bankroll -= amount
            break
        except ValueError:
            message = "Please enter a valid number."


def resolve_insurance(player: Player, dealer_blackjack: bool):
    hand = player.hands[0]
    if hand.insurance_bet > 0:
        if dealer_blackjack:
            player.bankroll += hand.insurance_bet * 2
        hand.insurance_bet = 0


def play_player_hand_queue(player: Player, dealer_upcard_is_ace: bool, deck: Deck, dealer_hand: Hand):
    hand_queue = deque(player.hands)

    while hand_queue:
        hand = hand_queue.popleft()
        idx = player.hands.index(hand)

        if hand.split_from_aces:
            continue

        if hand.is_blackjack():
            hand.done = True
            continue

        while not hand.done:
            options = ["(H)it", "(S)tand"]
            if hand.can_split() and player.bankroll >= hand.bet:
                options.append("(P)lit")
            if len(hand.cards) == 2 and player.bankroll >= hand.bet:
                options.append("(D)ouble down")

            message = f"Options: {', '.join(options)}"
            redraw_table(dealer_hand, True, player, message=message, active_hand_index=idx)
            choice = prompt_in_frame("Your choice: ").strip().upper()

            if choice == "H":
                deal_card_with_delay(hand, deck, dealer_hand, player, True, active_hand_index=idx)
                if hand.is_bust():
                    hand.done = True
            elif choice == "S":
                hand.done = True
            elif choice == "P" and hand.can_split() and player.bankroll >= hand.bet:
                new_bet = hand.bet
                player.bankroll -= new_bet
                h1 = Hand(
                    cards=[hand.cards[0]],
                    bet=hand.bet,
                    is_split_hand=True,
                    split_from_aces=(hand.cards[0].rank == Rank.ACE),
                )
                h2 = Hand(
                    cards=[hand.cards[1]],
                    bet=new_bet,
                    is_split_hand=True,
                    split_from_aces=(hand.cards[1].rank == Rank.ACE),
                )

                player.hands[idx:idx + 1] = [h1, h2]

                deal_card_with_delay(h1, deck, dealer_hand, player, True, active_hand_index=idx)
                deal_card_with_delay(h2, deck, dealer_hand, player, True, active_hand_index=idx + 1)

                if hand.cards[0].rank == Rank.ACE:
                    h1.done = True
                    h2.done = True

                hand_queue.append(h1)
                hand_queue.append(h2)
                hand.done = True
            elif choice == "D" and len(hand.cards) == 2 and player.bankroll >= hand.bet:
                player.bankroll -= hand.bet
                hand.bet *= 2
                hand.doubled = True
                deal_card_with_delay(hand, deck, dealer_hand, player, True, active_hand_index=idx)
                hand.done = True
            else:
                redraw_table(dealer_hand, True, player, message="Invalid choice.", active_hand_index=idx)

    return player.hands


def play_dealer_hand(dealer_hand: Hand, deck: Deck, player: Player):
    while True:
        total, is_soft = dealer_hand.value()
        if total > 21:
            break
        if total > 17 or (total == 17 and not is_soft):
            break
        deal_card_with_delay(dealer_hand, deck, dealer_hand, player, hide_dealer_hole=False)


def settle_round(player: Player, dealer_hand: Hand) -> list[str]:
    dealer_total, _ = dealer_hand.value()
    outcomes = []

    for hand in player.hands:
        hand_total, _ = hand.value()

        if dealer_total > 21:
            outcome = "WIN"
        elif hand_total > 21:
            outcome = "LOSS"
        elif hand_total == dealer_total:
            outcome = "PUSH"
        elif hand_total > dealer_total:
            if hand.is_blackjack():
                outcome = "BLACKJACK_WIN"
            else:
                outcome = "WIN"
        else:
            outcome = "LOSS"

        if outcome == "BLACKJACK_WIN":
            payout = hand.bet + (hand.bet * 3) // 2
            player.bankroll += payout
            player.wins += 1
        elif outcome == "WIN":
            payout = hand.bet * 2
            player.bankroll += payout
            player.wins += 1
        elif outcome == "PUSH":
            player.bankroll += hand.bet
            player.pushes += 1
        else:
            player.losses += 1

        outcomes.append(outcome)

    return outcomes
