# Casino Table Simulator CLI

A terminal-based casino simulator written in Python (stdlib only), played on a full-screen ASCII table. Two game modes: **Blackjack** and **Ultimate Texas Hold'em**.

## Setup & Play

### Requirements

No external dependencies needed (Python 3.10+ for `list[Card]`-style type hints). A terminal at least **120 columns x 40 rows**, ANSI/VT100-capable and UTF-8-capable.

```bash
python3 -m blackjack
```

You'll be asked which game to play, then for your name and starting bankroll, before the table view takes over.

## Blackjack

### Rules

- **Standard Casino Rules**: Dealer hits on 16 or less, stands on hard 17+, hits soft 17, stands on soft 18+.
- **Blackjack Payout**: 3:2 (natural 2-card 21).
- **Split**: You may split a pair (matching rank) into two independent hands. Each hand is dealt one additional card and played separately.
  - **No resplitting**: Resulting hands from a split cannot be split again.
  - **Split Aces**: Each gets exactly one more card, then auto-stands.
  - **Split 21**: A 21 achieved after splitting pays 1:1, not the 3:2 blackjack rate.
- **Double Down**: You may double your bet on the first two cards, receiving exactly one more card, then auto-standing.
- **Insurance**: When the dealer shows an Ace, you may place an insurance side bet (up to half your main bet). If the dealer has blackjack, insurance pays 2:1. Otherwise, the insurance bet is forfeited.

### Game Flow

Each round: you're prompted for a bet (`0` ends the session), cards are dealt one at a time in the Dealer's Hand / Your Hand boxes, you play (hit/stand/split/double) via the prompt box, the dealer plays out their hand, and results settle.

### Dealer Insurance Peek

The dealer only peeks for blackjack when showing an Ace. If the dealer's up-card is a 10-value card, no peek occurs; you must act without knowing if the dealer has blackjack. This is a common casino simplification.

## Ultimate Texas Hold'em

### Rules

- **Ante & Blind**: Equal, mandatory bets placed before any cards are dealt.
- **Play bet escalation**: After seeing your 2 hole cards, you may check or bet **4x** your Ante. If you check, the flop is dealt and you may check or bet **2x**. If you check again, the turn and river are dealt and you must either bet **1x** or **fold** (forfeiting Ante and Blind).
- **Dealer qualification**: The dealer needs at least a pair to "qualify". If the dealer doesn't qualify, the Ante pushes regardless of the hand comparison; Blind and Play are still settled normally.
- **Best hand**: Your best 5-card hand from your 2 hole cards + the 5 community cards, standard poker hand rankings (including the wheel straight, A-2-3-4-5).
- **Blind paytable** (pays only if you win and your hand is at least a Straight, otherwise pushes): Straight 1:1, Flush 3:2, Full House 3:1, Four of a Kind 10:1, Straight Flush 50:1, Royal Flush 500:1.
- **Play bet**: Always 1:1 if you win, pushes on a tie, loses if you lose — unaffected by dealer qualification.

### Game Flow

Each round: enter your Ante (`0` ends the session; Blind auto-matches it). Your 2 hole cards and the dealer's 2 hidden hole cards are dealt one at a time. Decide check/bet at each street. The community cards (flop, turn, river) appear one at a time in the board box as they're revealed. At showdown, the dealer's hand is revealed, hands are compared, and all three bets (Ante/Blind/Play) settle independently.

## Testing

Run unit tests:

```bash
python3 -m unittest discover -s tests
```

Tests cover:
- Deck integrity (52 unique cards, proper shuffling).
- Blackjack hand scoring (soft/hard aces, multiple aces, bust detection, split eligibility).
- Poker hand evaluation (all hand ranks including the wheel straight and royal flush, best-5-of-7 selection, dealer qualification, hand comparison).

## Implementation Notes

### Table Rendering

The game draws a fixed 120x40 full-screen frame using ANSI cursor addressing (`blackjack/screen.py`, shared region geometry in `blackjack/layout.py`). Blackjack (`blackjack/table.py`) and Hold'em (`blackjack/holdem_table.py`) reuse the same six regions but repurpose them: in Hold'em, the big top box that shows the dealer's hand in Blackjack instead shows the community cards, and the narrow top sidebar that shows Blackjack's dealer status instead shows the dealer's hidden hole cards. Every state change (a card dealt, a choice made) triggers a full redraw. If your terminal is smaller than 120x40, the game exits at startup with a plain-text message asking you to enlarge it.

### Card Dealing Delay

Every single card dealt — in either game mode — triggers a redraw followed by a 1 second pause, so cards visibly land one at a time instead of appearing all at once. In Hold'em this includes dealing the flop's 3 cards individually, not all at once.

### Money

All amounts are whole-dollar integers. Payouts that aren't even money floor to the nearest dollar (e.g., Blackjack's 3:2 payout on a $5 bet pays $7 + $5 = $12, not $12.50).

### Session Stop Conditions

- **Blackjack**: betting `0`, or an empty bankroll, ends the session.
- **Hold'em**: entering `0` as your Ante, or not having enough bankroll to cover an Ante + Blind, ends the session.

### Statistics

- **Wins, Losses, Pushes**: In Blackjack, counted per resolved hand (a split round can contribute more than one). In Hold'em, counted per round based on the overall hand comparison (a fold always counts as a loss).
- **Final Bankroll**: Shown in the summary after the session ends.
