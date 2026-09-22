import time

from casino.cards import Card, Deck
from casino.layout import (
    SCREEN_COLS,
    SCREEN_ROWS,
    CARD_DEAL_DELAY,
    TOP_BOX,
    TOP_SIDEBAR,
    PROMPT_BOX,
    INFO_SIDEBAR,
    BOTTOM_BOX,
    INSET_BOX,
)
from casino.screen import (
    Screen,
    move_cursor,
    clear_to_eol,
    visible_len,
    render_cards_block,
)


def draw_static_frame(screen: Screen) -> None:
    title = " ULTIMATE TEXAS HOLD'EM "
    pad = (SCREEN_COLS - visible_len(title)) // 2
    screen.write_at(1, max(1, pad), title)

    t_row, t_col, t_h, t_w = TOP_BOX
    screen.draw_box(t_row, t_col, t_h, t_w, title="COMMUNITY CARDS")

    s_row, s_col, s_h, s_w = TOP_SIDEBAR
    screen.draw_box(s_row, s_col, s_h, s_w, title="DEALER")

    p_row, p_col, p_h, p_w = PROMPT_BOX
    screen.draw_box(p_row, p_col, p_h, p_w, title="PROMPT")

    b_row, b_col, b_h, b_w = INFO_SIDEBAR
    screen.draw_box(b_row, b_col, b_h, b_w, title="BETS")

    y_row, y_col, y_h, y_w = BOTTOM_BOX
    screen.draw_box(y_row, y_col, y_h, y_w, title="YOUR HAND")

    a_row, a_col, a_h, a_w = INSET_BOX
    screen.draw_box(a_row, a_col, a_h, a_w, title="AMOUNT")


def render_community_cards(screen: Screen, community: list[Card]) -> None:
    row, col, h, w = TOP_BOX
    interior_col = col + 2
    interior_row = row + 2
    interior_w = w - 4

    if not community:
        screen.write_at(interior_row, interior_col, "(waiting for the flop...)")
        return

    render_cards_block(screen, interior_row, interior_col, community, False, interior_w)


def render_dealer_hole(screen: Screen, cards: list[Card], hide: bool, hand_description: str) -> None:
    row, col, h, w = TOP_SIDEBAR
    interior_col = col + 2
    interior_row = row + 2
    interior_w = w - 4

    if not cards:
        screen.write_at(interior_row, interior_col, "(hidden)")
        return

    display_cards = [None] * len(cards) if hide else cards
    render_cards_block(screen, interior_row, interior_col, display_cards, False, interior_w)

    if not hide and hand_description:
        screen.write_at(interior_row + 6, interior_col, hand_description[:interior_w])


def render_bets(screen: Screen, ante: int, blind: int, play_bet: int, bankroll: int, message: str) -> None:
    b_row, b_col, b_h, b_w = INFO_SIDEBAR
    bet_col = b_col + 2

    screen.write_at(b_row + 2, bet_col, f"Ante: ${ante}")
    screen.write_at(b_row + 3, bet_col, f"Blind: ${blind}")
    screen.write_at(b_row + 4, bet_col, f"Play: ${play_bet}")

    a_row, a_col, a_h, a_w = INSET_BOX
    amount_col = a_col + 2
    screen.write_at(a_row + 2, amount_col, f"${bankroll}")

    p_row, p_col, p_h, p_w = PROMPT_BOX
    msg_col = p_col + 2
    msg_width = p_w - 4
    max_lines = 3

    lines = message.split("\n") if message else []
    for i in range(max_lines):
        row = p_row + 2 + i
        screen.write_at(row, msg_col, " " * msg_width)
        if i < len(lines):
            screen.write_at(row, msg_col, lines[i][:msg_width])


def render_player_hole(screen: Screen, cards: list[Card], hand_description: str) -> None:
    y_row, y_col, y_h, y_w = BOTTOM_BOX
    interior_row = y_row + 2
    interior_col = y_col + 3
    interior_w = y_w - 6

    if not cards:
        screen.write_at(interior_row, interior_col, "(waiting for the ante...)")
        return

    render_cards_block(screen, interior_row + 2, interior_col, cards, False, interior_w)

    if hand_description:
        screen.write_at(interior_row + 8, interior_col, f"Best hand: {hand_description}")


def redraw_holdem_table(
    player_cards: list[Card],
    dealer_cards: list[Card],
    hide_dealer: bool,
    community: list[Card],
    ante: int,
    blind: int,
    play_bet: int,
    bankroll: int,
    message: str = "",
    dealer_description: str = "",
    player_description: str = "",
) -> None:
    screen = Screen(SCREEN_ROWS, SCREEN_COLS)
    draw_static_frame(screen)

    render_community_cards(screen, community)
    render_dealer_hole(screen, dealer_cards, hide_dealer, dealer_description)
    render_bets(screen, ante, blind, play_bet, bankroll, message)
    render_player_hole(screen, player_cards, player_description)

    screen.render()


def prompt_in_frame(text: str) -> str:
    p_row, p_col, p_h, p_w = PROMPT_BOX
    input_row = p_row + p_h - 3
    input_col = p_col + 2

    move_cursor(input_row, input_col)
    clear_to_eol()
    return input(text)


def deal_card_with_delay(
    target: list[Card],
    deck: Deck,
    redraw_fn,
) -> Card:
    card = deck.deal(1)[0]
    target.append(card)
    redraw_fn()
    time.sleep(CARD_DEAL_DELAY)
    return card
