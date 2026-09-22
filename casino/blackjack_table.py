import time

from casino.cards import Card, Deck
from casino.hand import Hand
from casino.player import Player
from casino.layout import (
    SCREEN_COLS,
    SCREEN_ROWS,
    CARD_DEAL_DELAY,
    TOP_BOX as DEALER_BOX,
    TOP_SIDEBAR as DEALER_SIDEBAR,
    PROMPT_BOX,
    INFO_SIDEBAR as BET_SIDEBAR,
    BOTTOM_BOX as PLAYER_BOX,
    INSET_BOX as AMOUNT_BOX,
)
from casino.screen import (
    Screen,
    move_cursor,
    clear_to_eol,
    visible_len,
    render_cards_block,
    RESET,
    BOLD_YELLOW,
    RED,
    DIM,
)

HAND1_COL_OFFSET = 3
HAND2_COL_OFFSET = 60


def draw_static_frame(screen: Screen) -> None:
    title = " BLACKJACK "
    pad = (SCREEN_COLS - visible_len(title)) // 2
    screen.write_at(1, max(1, pad), title)

    d_row, d_col, d_h, d_w = DEALER_BOX
    screen.draw_box(d_row, d_col, d_h, d_w, title="DEALER'S HAND")

    s_row, s_col, s_h, s_w = DEALER_SIDEBAR
    screen.draw_box(s_row, s_col, s_h, s_w, title="STATUS")

    p_row, p_col, p_h, p_w = PROMPT_BOX
    screen.draw_box(p_row, p_col, p_h, p_w, title="PROMPT")

    b_row, b_col, b_h, b_w = BET_SIDEBAR
    screen.draw_box(b_row, b_col, b_h, b_w, title="BET")

    y_row, y_col, y_h, y_w = PLAYER_BOX
    screen.draw_box(y_row, y_col, y_h, y_w, title="YOUR HAND")

    a_row, a_col, a_h, a_w = AMOUNT_BOX
    screen.draw_box(a_row, a_col, a_h, a_w, title="AMOUNT")


def render_dealer_cards(screen: Screen, cards: list[Card], hide_last: bool) -> None:
    row, col, h, w = DEALER_BOX
    interior_col = col + 2
    interior_row = row + 2
    interior_w = w - 4

    if not cards:
        screen.write_at(interior_row, interior_col, "(waiting for cards...)")
        return

    render_cards_block(screen, interior_row, interior_col, cards, hide_last, interior_w)


def render_status(
    screen: Screen, dealer_hand: Hand, hide_dealer_hole: bool, bet: int, bankroll: int, message: str
) -> None:
    s_row, s_col, s_h, s_w = DEALER_SIDEBAR
    text_col = s_col + 2

    if hide_dealer_hole or not dealer_hand.cards:
        status_line = "??" if dealer_hand.cards else "-"
    else:
        status_line = dealer_hand.display_total()

    screen.write_at(s_row + 2, text_col, "Dealer total:")
    screen.write_at(s_row + 3, text_col, status_line)

    b_row, b_col, b_h, b_w = BET_SIDEBAR
    bet_col = b_col + 2
    screen.write_at(b_row + 2, bet_col, "Current bet:")
    screen.write_at(b_row + 3, bet_col, f"${bet}")

    a_row, a_col, a_h, a_w = AMOUNT_BOX
    amount_col = a_col + 2
    screen.write_at(a_row + 2, amount_col, f"${bankroll}")

    p_row, p_col, p_h, p_w = PROMPT_BOX
    msg_col = p_col + 2
    msg_row = p_row + 2
    screen.write_at(msg_row, msg_col, " " * (p_w - 4))
    if message:
        screen.write_at(msg_row, msg_col, message[: p_w - 4])


def render_player_cards(screen: Screen, hands: list[Hand], active_hand_index: int | None) -> None:
    p_row, p_col, p_h, p_w = PLAYER_BOX
    interior_row = p_row + 2

    if not hands:
        screen.write_at(interior_row, p_col + 2, "(waiting for bet...)")
        return

    sub_col_width = (p_w - 4) if len(hands) == 1 else (p_w // 2 - 4)
    offsets = [HAND1_COL_OFFSET] if len(hands) == 1 else [HAND1_COL_OFFSET, HAND2_COL_OFFSET]

    for i, hand in enumerate(hands):
        base_col = p_col + offsets[i]
        is_active = active_hand_index == i

        label = f"HAND {i + 1} (bet: ${hand.bet})"
        if is_active:
            header = f"{BOLD_YELLOW}▶ {label}{RESET}"
        elif hand.done:
            header = f"{DIM}{label} (done){RESET}"
        else:
            header = label

        screen.write_at(interior_row, base_col, header)

        render_cards_block(screen, interior_row + 2, base_col, hand.cards, False, sub_col_width)

        total_str = hand.display_total()
        if hand.is_bust():
            total_str = f"{RED}{total_str}{RESET}"
        screen.write_at(interior_row + 8, base_col, f"Total: {total_str}")


def redraw_table(
    dealer_hand: Hand,
    hide_dealer_hole: bool,
    player: Player,
    message: str = "",
    active_hand_index: int | None = None,
) -> None:
    screen = Screen(SCREEN_ROWS, SCREEN_COLS)
    draw_static_frame(screen)

    render_dealer_cards(screen, dealer_hand.cards, hide_dealer_hole)

    bet = player.hands[0].bet if player.hands else 0
    render_status(screen, dealer_hand, hide_dealer_hole, bet, player.bankroll, message)
    render_player_cards(screen, player.hands, active_hand_index)

    screen.render()


def prompt_in_frame(text: str) -> str:
    p_row, p_col, p_h, p_w = PROMPT_BOX
    input_row = p_row + p_h - 3
    input_col = p_col + 2

    move_cursor(input_row, input_col)
    clear_to_eol()
    return input(text)


def deal_card_with_delay(
    hand: Hand,
    deck: Deck,
    dealer_hand: Hand,
    player: Player,
    hide_dealer_hole: bool,
    active_hand_index: int | None = None,
    message: str = "",
) -> Card:
    card = deck.deal(1)[0]
    hand.cards.append(card)
    redraw_table(dealer_hand, hide_dealer_hole, player, message=message, active_hand_index=active_hand_index)
    time.sleep(CARD_DEAL_DELAY)
    return card
