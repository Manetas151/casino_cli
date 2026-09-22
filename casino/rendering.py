from casino.cards import Card
from typing import Optional


def render_card(card: Optional[Card], face_down: bool = False) -> list[str]:
    if face_down or card is None:
        return [
            "┌───────┐",
            "│◠◠◠◠◠◠◠│",
            "│★★★⚜★★★│",
            "│◡◡◡◡◡◡◡│",
            "└───────┘",
        ]

    rank_str = card.rank.value
    suit_str = card.suit.value
    if suit_str == "♠" or suit_str == "♥":
        colour = "\033[1;31m"
    else:
        colour = "\033[30m"

    if len(rank_str) == 1:
        top_rank = rank_str + "      "
        bot_rank = "      " + rank_str
    else:
        top_rank = rank_str + "     "
        bot_rank = "     " + rank_str

    return [
        "┌───────┐",
        f"│{top_rank}│",
        f"│   {colour}{suit_str}{"\033[0m"}   │",
        f"│{bot_rank}│",
        "└───────┘",
    ]
