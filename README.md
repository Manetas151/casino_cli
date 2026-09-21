# Blackjack Simulator CLI

A terminal-based Blackjack simulator written in Python (stdlib only). Supports up to 5 players playing simultaneously against a dealer.

## Rules

- **Standard Casino Rules**: Dealer hits on 16 or less, stands on hard 17+, hits soft 17, stands on soft 18+.
- **Blackjack Payout**: 3:2 (natural 2-card 21).
- **Split**: A player may split a pair (matching rank) into two independent hands. Each hand is dealt one additional card and played separately.
  - **No resplitting**: Resulting hands from a split cannot be split again.
  - **Split Aces**: Each gets exactly one more card, then auto-stands.
  - **Split 21**: A 21 achieved after splitting pays 1:1, not the 3:2 blackjack rate.
- **Double Down**: A player may double their bet on the first two cards, receiving exactly one more card, then auto-standing.
- **Insurance**: When the dealer shows an Ace, players may place an insurance side bet (up to half their main bet). If the dealer has blackjack, insurance pays 2:1. Otherwise, the insurance bet is forfeited.

## Setup & Play

### Installation

No external dependencies needed (Python 3.6+). Just run:

```bash
python -m blackjack
```

### Game Flow

1. Enter the number of players (1–5).
2. Each player enters their name and starting bankroll (in whole dollars).
3. Each round:
   - Each active player is prompted for a bet. Enter `0` to end the session for everyone.
   - If a player's bankroll is ≤ $0, the entire session ends immediately.
   - Cards are dealt and displayed in ASCII art.
   - If the dealer shows an Ace, players may place an insurance bet.
   - Players play their hands (hit, stand, split, double down).
   - The dealer plays their hand.
   - Results are settled and bankrolls updated.
4. When the session ends, a summary is printed: wins, losses, pushes, and final bankroll per player.

## Testing

Run unit tests:

```bash
python -m unittest discover -s tests
```

Tests cover:
- Deck integrity (52 unique cards, proper shuffling).
- Hand scoring (soft/hard aces, multiple aces, bust detection).
- Split eligibility.
- Blackjack detection.

## Implementation Notes

### Money

All amounts are whole-dollar integers. The 3:2 blackjack payout on an odd bet floors to the nearest dollar (e.g., a $5 bet pays $7 + $5 = $12, not $12.50).

### ASCII Card Rendering

Cards are rendered as 5-line ASCII boxes using Unicode suit symbols (♠ ♥ ♦ ♣). If your terminal doesn't support UTF-8, cards may display incorrectly; consider running in a UTF-8-capable terminal (most modern terminals support this by default).

### Session Stop Conditions

- **Player bets 0**: The session ends immediately; all players' stats are printed.
- **Player's bankroll ≤ $0**: The session ends immediately before that player is prompted to bet; all players' stats are printed.

### Statistics

- **Wins, Losses, Pushes**: Counted per resolved hand, not per round. If a player splits and wins one hand while losing another, they gain 1 win and 1 loss.
- **Final Bankroll**: Shows total money remaining after all rounds.

### Dealer Insurance Peek

The dealer only peeks for blackjack when showing an Ace. If the dealer's up-card is a 10-value card, no peek occurs; players must act without knowing if the dealer has blackjack. This is a common casino simplification.
