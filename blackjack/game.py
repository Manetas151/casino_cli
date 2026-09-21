from collections import deque
from blackjack.cards import Deck, Rank
from blackjack.hand import Hand
from blackjack.player import Player
from blackjack.rendering import print_hand


def deal_initial_hands(players: list[Player], dealer_hand: Hand, deck: Deck):
    for _ in range(2):
        for player in players:
            player.hands[0].cards.append(deck.deal(1)[0])
        dealer_hand.cards.append(deck.deal(1)[0])


def offer_insurance(players: list[Player]):
    for player in players:
        hand = player.hands[0]
        max_insurance = hand.bet // 2
        if max_insurance == 0:
            continue

        while True:
            try:
                amount = int(
                    input(
                        f"{player.name}, insurance bet (max ${max_insurance}, or 0 to decline): $"
                    )
                )
                if amount < 0 or amount > max_insurance or amount > player.bankroll:
                    print(f"Invalid amount. Must be 0–${max_insurance} and within bankroll.")
                    continue
                hand.insurance_bet = amount
                player.bankroll -= amount
                break
            except ValueError:
                print("Please enter a valid number.")


def resolve_insurance(players: list[Player], dealer_blackjack: bool):
    for player in players:
        hand = player.hands[0]
        if hand.insurance_bet > 0:
            if dealer_blackjack:
                player.bankroll += hand.insurance_bet * 2
            hand.insurance_bet = 0


def play_player_hand_queue(
    player: Player, dealer_upcard_is_ace: bool, deck: Deck
) -> list[Hand]:
    hand_queue = deque(player.hands)
    finished_hands = []

    while hand_queue:
        hand = hand_queue.popleft()

        if hand.split_from_aces:
            finished_hands.append(hand)
            continue

        if hand.is_blackjack():
            hand.done = True
            finished_hands.append(hand)
            continue

        while not hand.done:
            print_hand(
                f"{player.name}'s hand (bet: ${hand.bet})",
                hand.cards,
                show_total=True,
                total_str=hand.display_total(),
            )

            options = ["(H)it", "(S)tand"]
            if hand.can_split() and player.bankroll >= hand.bet:
                options.append("(P)lit")
            if len(hand.cards) == 2 and player.bankroll >= hand.bet:
                options.append("(D)ouble down")

            print(f"Options: {', '.join(options)}")

            choice = input("Your choice: ").strip().upper()

            if choice == "H":
                card = deck.deal(1)[0]
                hand.cards.append(card)
                if hand.is_bust():
                    print(f"{player.name} busts with {hand.display_total()}")
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

                h1.cards.append(deck.deal(1)[0])
                h2.cards.append(deck.deal(1)[0])

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
                card = deck.deal(1)[0]
                hand.cards.append(card)
                if hand.is_bust():
                    print(f"{player.name} busts with {hand.display_total()}")
                hand.done = True
            else:
                print("Invalid choice.")

        finished_hands.append(hand)

    return finished_hands


def play_dealer_hand(dealer_hand: Hand, deck: Deck):
    while True:
        total, is_soft = dealer_hand.value()
        if total > 21:
            break
        if total > 17 or (total == 17 and not is_soft):
            break
        card = deck.deal(1)[0]
        dealer_hand.cards.append(card)


def settle_round(players: list[Player], dealer_hand: Hand):
    dealer_total, _ = dealer_hand.value()
    dealer_blackjack = dealer_hand.is_blackjack()

    for player in players:
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
