from dataclasses import dataclass, field

from blackjack.cards import Card
from blackjack.player import Player
from blackjack.poker import (
    HandRank,
    best_hand_from_7,
    dealer_qualifies,
    compare,
    describe_hand,
    is_royal,
)

BLIND_PAYTABLE = {
    HandRank.STRAIGHT: (1, 1),
    HandRank.FLUSH: (3, 2),
    HandRank.FULL_HOUSE: (3, 1),
    HandRank.QUADS: (10, 1),
    HandRank.STRAIGHT_FLUSH: (50, 1),
}
ROYAL_FLUSH_MULT = (500, 1)


@dataclass
class HoldemState:
    player_cards: list[Card] = field(default_factory=list)
    dealer_cards: list[Card] = field(default_factory=list)
    community: list[Card] = field(default_factory=list)
    ante: int = 0
    blind: int = 0
    play_bet: int = 0
    folded: bool = False


def blind_multiplier(rank: HandRank, tiebreak: tuple[int, ...]) -> tuple[int, int] | None:
    if is_royal(rank, tiebreak):
        return ROYAL_FLUSH_MULT
    return BLIND_PAYTABLE.get(rank)


def settle_round(player: Player, state: HoldemState) -> tuple[str, str, str]:
    """Applies payouts to player.bankroll and updates wins/losses/pushes.

    Returns (result_message, dealer_hand_description, player_hand_description).
    """
    if state.folded:
        player.losses += 1
        msg = f"You folded. Lost Ante (${state.ante}) and Blind (${state.blind})."
        return msg, "", ""

    player_rank, player_tiebreak, _ = best_hand_from_7(state.player_cards + state.community)
    dealer_rank, dealer_tiebreak, _ = best_hand_from_7(state.dealer_cards + state.community)

    player_desc = describe_hand(player_rank, player_tiebreak)
    dealer_desc = describe_hand(dealer_rank, dealer_tiebreak)

    result = compare((player_rank, player_tiebreak), (dealer_rank, dealer_tiebreak))
    qualifies = dealer_qualifies(dealer_rank)

    lines = []

    if not qualifies:
        player.bankroll += state.ante
        lines.append(f"Dealer doesn't qualify (needs a pair) — Ante pushes (${state.ante}).")
    elif result > 0:
        player.bankroll += state.ante * 2
        lines.append(f"Ante wins ${state.ante}.")
    elif result == 0:
        player.bankroll += state.ante
        lines.append("Ante pushes.")
    else:
        lines.append(f"Ante lost (${state.ante}).")

    if result > 0:
        mult = blind_multiplier(player_rank, player_tiebreak)
        if mult:
            num, den = mult
            payout = state.blind + (state.blind * num) // den
            player.bankroll += payout
            lines.append(f"Blind wins ${payout - state.blind} ({num}:{den}).")
        else:
            player.bankroll += state.blind
            lines.append("Blind pushes (below a Straight).")
    elif result == 0:
        player.bankroll += state.blind
        lines.append("Blind pushes.")
    else:
        lines.append(f"Blind lost (${state.blind}).")

    if state.play_bet > 0:
        if result > 0:
            player.bankroll += state.play_bet * 2
            lines.append(f"Play wins ${state.play_bet}.")
        elif result == 0:
            player.bankroll += state.play_bet
            lines.append("Play pushes.")
        else:
            lines.append(f"Play lost (${state.play_bet}).")

    if result > 0:
        player.wins += 1
    elif result == 0:
        player.pushes += 1
    else:
        player.losses += 1

    header = f"You: {player_desc}  |  Dealer: {dealer_desc}"
    message = header + "\n" + " ".join(lines)
    return message, dealer_desc, player_desc
