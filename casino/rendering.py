from casino.cards import Card
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
