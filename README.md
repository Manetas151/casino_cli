# Casino Table Simulator CLI

A terminal-based casino simulator written in Python (stdlib only), played on a full-screen ASCII table. Two game modes: **Blackjack** and **Ultimate Texas Hold'em**.

## Setup & Play

### Requirements

No external dependencies needed (Python 3.10+ for `list[Card]`-style type hints). A terminal at least **120 columns x 40 rows**, ANSI/VT100-capable and UTF-8-capable.

```bash
python3 -m casino
```

You'll be asked which game to play, then for your name and starting bankroll, before the table view takes over.
