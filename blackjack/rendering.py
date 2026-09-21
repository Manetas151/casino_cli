from blackjack.cards import Card
from typing import Optional


def render_card(card: Optional[Card], face_down: bool = False) -> list[str]:
    if face_down or card is None:
        return [
            "┌───────┐",
            "│░░░░░░░│",
            "│░░░░░░░│",
            "│░░░░░░░│",
            "└───────┘",
        ]

    rank_str = card.rank.value
    suit_str = card.suit.value

    if len(rank_str) == 1:
        top_rank = rank_str + "      "
        bot_rank = "      " + rank_str
    else:
        top_rank = rank_str + "     "
        bot_rank = "     " + rank_str

    return [
        "┌───────┐",
        f"│{top_rank}│",
        f"│   {suit_str}   │",
        f"│{bot_rank}│",
        "└───────┘",
    ]


def render_hand(cards: list[Card], hide_last: bool = False) -> str:
    if not cards:
        return "(no cards)"

    rendered_cards = []
    for i, card in enumerate(cards):
        is_last = i == len(cards) - 1
        rendered_cards.append(render_card(card, face_down=is_last and hide_last))

    num_lines = len(rendered_cards[0])
    lines = []
    for line_idx in range(num_lines):
        line_parts = [card[line_idx] for card in rendered_cards]
        lines.append("  ".join(line_parts))

    return "\n".join(lines)


def print_hand(
    label: str,
    cards: list[Card],
    hide_last: bool = False,
    show_total: bool = True,
    total_str: Optional[str] = None,
):
    print(f"\n{label}:")
    print(render_hand(cards, hide_last))
    if show_total and total_str:
        print(f"Total: {total_str}")
