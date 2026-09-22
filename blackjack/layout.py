SCREEN_COLS = 120
SCREEN_ROWS = 40

CARD_DEAL_DELAY = 1.0

# --- Shared region geometry (row, col, height, width) ---
# Reused by both game modes; each mode decides what content goes in each slot.

TOP_BOX = (2, 1, 13, 90)          # blackjack: dealer's hand | hold'em: community cards
TOP_SIDEBAR = (2, 91, 13, 30)     # blackjack: status        | hold'em: dealer's hidden hand

PROMPT_BOX = (15, 1, 8, 90)
INFO_SIDEBAR = (15, 91, 8, 30)    # blackjack: current bet   | hold'em: ante/blind/play bets

BOTTOM_BOX = (24, 1, 16, 120)     # blackjack: your hand(s)  | hold'em: your hole cards
INSET_BOX = (36, 1, 4, 22)        # both: bankroll ("amount")
