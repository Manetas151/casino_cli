# Blackjack Simulator CLI

A terminal-based Blackjack simulator written in Python (stdlib only), played against a dealer on a full-screen ASCII table.

## Rules

- **Standard Casino Rules**: Dealer hits on 16 or less, stands on hard 17+, hits soft 17, stands on soft 18+.
- **Blackjack Payout**: 3:2 (natural 2-card 21).
- **Split**: You may split a pair (matching rank) into two independent hands. Each hand is dealt one additional card and played separately.
  - **No resplitting**: Resulting hands from a split cannot be split again.
  - **Split Aces**: Each gets exactly one more card, then auto-stands.
  - **Split 21**: A 21 achieved after splitting pays 1:1, not the 3:2 blackjack rate.
- **Double Down**: You may double your bet on the first two cards, receiving exactly one more card, then auto-standing.
- **Insurance**: When the dealer shows an Ace, you may place an insurance side bet (up to half your main bet). If the dealer has blackjack, insurance pays 2:1. Otherwise, the insurance bet is forfeited.

## Setup & Play

### Requirements

No external dependencies needed (Python 3.10+ for `list[Card]`-style type hints). A terminal at least **120 columns x 40 rows**, ANSI/VT100-capable and UTF-8-capable.

```bash
python3 -m blackjack
```

### Game Flow

1. Enter your name and starting bankroll (in whole dollars) — plain text prompts.
2. The screen clears and the table view takes over for the rest of the session. Each round:
   - You're prompted for a bet. Enter `0` to end the session.
   - If your bankroll is ≤ $0, the session ends automatically.
   - Cards are dealt one at a time, each with a short pause, and shown as ASCII art in the Dealer's Hand and Your Hand boxes.
   - If the dealer shows an Ace, you may place an insurance bet.
   - Play your hand (hit, stand, split, double down) via the prompt box.
   - The dealer plays their hand, one card at a time.
   - Results are settled and your bankroll is updated.
3. When the session ends, a summary is printed below the table: wins, losses, pushes, and final bankroll.

## Testing

Run unit tests:

```bash
python3 -m unittest discover -s tests
```

Tests cover:
- Deck integrity (52 unique cards, proper shuffling).
- Hand scoring (soft/hard aces, multiple aces, bust detection).
- Split eligibility.
- Blackjack detection.

## Implementation Notes

### Table Rendering

The game draws a fixed 120x40 full-screen frame using ANSI cursor addressing (`blackjack/screen.py`, `blackjack/table.py`) — a Dealer's Hand box + status sidebar up top, a Prompt box + bet sidebar in the middle, and Your Hand box + bankroll ("Amount") box at the bottom. Every state change (a card dealt, a choice made) triggers a full redraw. If your terminal is smaller than 120x40, the game exits at startup with a plain-text message asking you to enlarge it.

### Card Dealing Delay

Every single card dealt — during the initial deal, on a hit, a double, a split, or a dealer hit — triggers a redraw followed by a 1 second pause, so cards visibly land one at a time instead of appearing all at once.

### Money

All amounts are whole-dollar integers. The 3:2 blackjack payout on an odd bet floors to the nearest dollar (e.g., a $5 bet pays $7 + $5 = $12, not $12.50).

### Session Stop Conditions

- **You bet 0**: The session ends immediately.
- **Your bankroll ≤ $0**: The session ends automatically before you're prompted to bet.

### Statistics

- **Wins, Losses, Pushes**: Counted per resolved hand, not per round. If you split and win one hand while losing another, that's 1 win and 1 loss.
- **Final Bankroll**: Shown in the summary after the session ends.

### Dealer Insurance Peek

The dealer only peeks for blackjack when showing an Ace. If the dealer's up-card is a 10-value card, no peek occurs; you must act without knowing if the dealer has blackjack. This is a common casino simplification.
