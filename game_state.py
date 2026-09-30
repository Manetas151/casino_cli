from casino.cards import Deck
from casino.poker import best_hand_from_7, compare, describe_hand

class GameState:
    def __init__(self):
        self.players = {}        
        self.community_cards = []
        self.pot = 0
        self.game_phase = "WAITING" 
        self.deck = None
        self.active_players = []
        self.turn_index = 0      
        self.current_highest_bet = 0
        self.showdown_message = ""
        
    def add_player(self, player_id, starting_bankroll):
        self.players[player_id] = {
            "bankroll": starting_bankroll,
            "cards": [],
            "current_bet": 0,
            "folded": False,
            "has_acted": False
        }

    def start_hand(self):
        if len(self.players) >= 2:
            self.deck = Deck.new_shuffled()
            self.community_cards = []
            self.pot = 0
            self.game_phase = "PREFLOP"
            self.active_players = list(self.players.keys())
            self.turn_index = 0
            self.current_highest_bet = 0
            self.showdown_message = ""
            
            for pid in self.players:
                self.players[pid]["cards"] = self.deck.deal(2)
                self.players[pid]["current_bet"] = 0
                self.players[pid]["folded"] = False
                self.players[pid]["has_acted"] = False

    def get_current_player_id(self):
        if not self.active_players: return None
        return self.active_players[self.turn_index]

    def resolve_showdown(self):
        # Βρίσκουμε τους παίκτες που δεν έχουν κάνει fold και δεν έχουν αποσυνδεθεί
        active = [pid for pid in self.active_players if not self.players.get(pid, {}).get("folded", True)]
        
        # Failsafe #1: Αν έμεινε 1 ή 0 παίκτες
        if len(active) <= 1:
            if len(active) == 1:
                winner = active[0]
                self.players[winner]["bankroll"] += self.pot
                self.showdown_message = f"Player {winner} wins ${self.pot} (Everyone else folded)"
            else:
                self.showdown_message = "Everyone folded. Pot remains."
            self.pot = 0
            self.game_phase = "SHOWDOWN"
            return

        # Failsafe #2: Σιγουρευόμαστε ότι υπάρχουν πάντα 5 κοινές κάρτες πριν το Showdown
        while len(self.community_cards) < 5:
            self.community_cards.extend(self.deck.deal(1))

        best_pids = []
        best_hand_val = None

        for pid in active:
            hole_cards = self.players.get(pid, {}).get("cards", [])
            
            # Failsafe #3: Αν κάποιος παίκτης δεν έχει 2 κάρτες (π.χ. αποσύνδεση), τον αγνοούμε
            if len(hole_cards) < 2:
                continue
                
            rank, tiebreak, combo = best_hand_from_7(hole_cards + self.community_cards)
            hand_val = (rank, tiebreak)
            
            if best_hand_val is None:
                best_pids = [pid]
                best_hand_val = hand_val
            else:
                cmp = compare(hand_val, best_hand_val)
                if cmp > 0:
                    best_pids = [pid]
                    best_hand_val = hand_val
                elif cmp == 0:
                    best_pids.append(pid)
        
        # Failsafe #4: Σε περίπτωση που η λίστα βγει άδεια (π.χ. σοβαρό error)
        if not best_pids:
            self.showdown_message = "No valid hands found."
            self.pot = 0
            self.game_phase = "SHOWDOWN"
            return

        win_amount = self.pot // len(best_pids)
        for pid in best_pids:
            self.players[pid]["bankroll"] += win_amount
        
        win_names = " & ".join([f"Player {p}" for p in best_pids])
        desc = describe_hand(*best_hand_val)
        self.showdown_message = f"{win_names} wins ${self.pot} with {desc}!"
        self.pot = 0
        self.game_phase = "SHOWDOWN"

    def fast_forward_to_showdown(self):
        while self.game_phase not in ["SHOWDOWN", "WAITING"]:
            if self.game_phase == "PREFLOP":
                self.community_cards = self.deck.deal(3)
                self.game_phase = "FLOP"
            elif self.game_phase == "FLOP":
                self.community_cards.extend(self.deck.deal(1))
                self.game_phase = "TURN"
            elif self.game_phase == "TURN":
                self.community_cards.extend(self.deck.deal(1))
                self.game_phase = "RIVER"
            elif self.game_phase == "RIVER":
                self.resolve_showdown()

    def next_turn(self):
        if not self.active_players: return
        start_index = self.turn_index
        while True:
            self.turn_index = (self.turn_index + 1) % len(self.active_players)
            pid = self.active_players[self.turn_index]
            p = self.players.get(pid)
            
            if not p:
                if self.turn_index == start_index: break
                continue
                
            if (not p["folded"] and p["bankroll"] > 0) or self.turn_index == start_index:
                break
        self.check_phase_advance()

    def check_phase_advance(self):
        ready = True
        active_count = 0
        players_can_act = 0
        
        for pid in list(self.active_players):
            p = self.players.get(pid)
            if not p: continue
            
            if not p["folded"]:
                active_count += 1
                if p["bankroll"] > 0:
                    players_can_act += 1
                    if not p["has_acted"] or p["current_bet"] < self.current_highest_bet:
                        ready = False

        if active_count <= 1:
            self.resolve_showdown()
            return

        if ready:
            if players_can_act <= 1:
                self.fast_forward_to_showdown()
            else:
                self.advance_phase()

    def advance_phase(self):
        for pid in self.active_players:
            if pid in self.players:
                self.players[pid]["has_acted"] = False
                self.players[pid]["current_bet"] = 0
        self.current_highest_bet = 0
        
        if not self.active_players: return
        self.turn_index = 0
        start_idx = self.turn_index
        while True:
            pid = self.active_players[self.turn_index]
            p = self.players.get(pid)
            if p and not p["folded"] and p["bankroll"] > 0:
                break
            self.turn_index = (self.turn_index + 1) % len(self.active_players)
            if self.turn_index == start_idx: break
                
        if self.game_phase == "PREFLOP":
            self.community_cards = self.deck.deal(3)
            self.game_phase = "FLOP"
        elif self.game_phase == "FLOP":
            self.community_cards.extend(self.deck.deal(1))
            self.game_phase = "TURN"
        elif self.game_phase == "TURN":
            self.community_cards.extend(self.deck.deal(1))
            self.game_phase = "RIVER"
        elif self.game_phase == "RIVER":
            self.resolve_showdown()