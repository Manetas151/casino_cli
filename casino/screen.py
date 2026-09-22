import re
import shutil
import sys

from casino.cards import Card
from casino.rendering import render_card

ANSI_RE = re.compile(r"\033\[[0-9;]*m")

RESET = "\033[0m"
BOLD_YELLOW = "\033[1;33m"
BOLD_GREEN = "\033[1;32m"
RED = "\033[1;31m"
DIM = "\033[2m"


def visible_len(text: str) -> int:
    return len(ANSI_RE.sub("", text))


def move_cursor(row: int, col: int) -> None:
    sys.stdout.write(f"\033[{row};{col}H")


def clear_and_home() -> None:
    sys.stdout.write("\033[2J\033[H")


def clear_to_eol() -> None:
    sys.stdout.write("\033[K")


def hide_cursor() -> None:
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def check_terminal_size(min_cols: int = 120, min_rows: int = 40) -> bool:
    size = shutil.get_terminal_size(fallback=(0, 0))
    return size.columns >= min_cols and size.lines >= min_rows


class Screen:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = [[" "] * cols for _ in range(rows)]

    def write_at(self, row: int, col: int, text: str) -> None:
        if row < 1 or row > self.rows:
            return

        r = self.grid[row - 1]
        c = col
        pending_prefix = ""
        last_cell_col = None

        for seg in re.split(r"(\033\[[0-9;]*m)", text):
            if not seg:
                continue
            if ANSI_RE.fullmatch(seg):
                pending_prefix += seg
                continue
            for ch in seg:
                if 1 <= c <= self.cols:
                    r[c - 1] = pending_prefix + ch
                    pending_prefix = ""
                    last_cell_col = c
                c += 1

        if pending_prefix and last_cell_col is not None:
            r[last_cell_col - 1] += pending_prefix

    def draw_box(self, row: int, col: int, height: int, width: int, title: str | None = None) -> None:
        top = "┌" + "─" * (width - 2) + "┐"
        bottom = "└" + "─" * (width - 2) + "┘"

        self.write_at(row, col, top)
        self.write_at(row + height - 1, col, bottom)

        for r in range(row + 1, row + height - 1):
            self.write_at(r, col, "│")
            self.write_at(r, col + width - 1, "│")

        if title:
            label = f" {title} "
            self.write_at(row, col + 2, label)

    def render(self) -> None:
        clear_and_home()
        lines = ["".join(row) for row in self.grid]
        sys.stdout.write("\n".join(lines))
        sys.stdout.flush()


def render_cards_block(
    screen: Screen,
    row: int,
    col: int,
    cards: list[Card],
    hide_last: bool,
    max_width: int,
) -> None:
    card_w = 9
    gap = 2
    per_row = max(1, (max_width + gap) // (card_w + gap))

    for i, card in enumerate(cards):
        is_last = i == len(cards) - 1
        art = render_card(card, face_down=is_last and hide_last)

        line_in_group = i // per_row
        pos_in_group = i % per_row

        card_col = col + pos_in_group * (card_w + gap)
        card_row = row + line_in_group * 6

        for line_idx, line in enumerate(art):
            screen.write_at(card_row + line_idx, card_col, line)
