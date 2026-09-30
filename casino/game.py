from casino.hand import Hand
from casino.player import Player

def resolve_insurance(player: Player, dealer_blackjack: bool):
    hand = player.hands[0]
    if hand.insurance_bet > 0:
        if dealer_blackjack:
            player.bankroll += hand.insurance_bet * 2
        hand.insurance_bet = 0

def settle_round(player: Player, dealer_hand: Hand) -> list[str]:
    dealer_total, _ = dealer_hand.value()
    outcomes = []

    for hand in player.hands:
        hand_total, _ = hand.value()

        if hand_total > 21:
            outcome = "LOSS"
        elif dealer_total > 21:
            outcome = "WIN"
        elif hand_total == dealer_total:
            outcome = "PUSH"
        elif hand_total > dealer_total:
            if hand.is_blackjack():
                outcome = "BLACKJACK WIN"
            else:
                outcome = "WIN"
        else:
            outcome = "LOSS"

        if outcome == "BLACKJACK WIN":
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