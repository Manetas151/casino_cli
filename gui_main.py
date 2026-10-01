import sys
import os
import pygame
import game_state
from casino.cards import Deck, Card, Suit, Rank
from casino.player import Player
from casino.hand import Hand
from casino.game import settle_round as blackjack_settle, resolve_insurance
from casino.holdem import HoldemState, settle_round as holdem_settle

# Φορτώνουμε το δίκτυο και την κατάσταση παιχνιδιού
from network import Network
from game_state import GameState

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
TABLE_COLOR = (34, 139, 34)
WHITE, BLACK, RED, GRAY, BLUE, GOLD, DARK_GREEN = (255, 255, 255), (0, 0, 0), (220, 20, 20), (200, 200, 200), (0, 100, 200), (255, 215, 0), (20, 100, 50)
HIGHLIGHT = (255, 255, 100)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pygame Casino")
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 64)

# --- ASSET MANAGEMENT ---
CARD_IMAGES = {}
CARD_WIDTH, CARD_HEIGHT = 80, 112 

def load_assets():
    base_path = os.path.join("assets", "cards")
    if not os.path.exists(base_path): return
    back_path = os.path.join(base_path, "card_back.png")
    if os.path.exists(back_path):
        img = pygame.image.load(back_path).convert_alpha()
        CARD_IMAGES["BACK"] = pygame.transform.smoothscale(img, (CARD_WIDTH, CARD_HEIGHT))
    rank_to_kenney = {Rank.ACE: "A", Rank.TWO: "02", Rank.THREE: "03", Rank.FOUR: "04", Rank.FIVE: "05", Rank.SIX: "06", Rank.SEVEN: "07", Rank.EIGHT: "08", Rank.NINE: "09", Rank.TEN: "10", Rank.JACK: "J", Rank.QUEEN: "Q", Rank.KING: "K"}
    for suit in Suit:
        for rank in Rank:
            filepath = os.path.join(base_path, f"card_{suit.name.lower()}_{rank_to_kenney[rank]}.png")
            if os.path.exists(filepath):
                img = pygame.image.load(filepath).convert_alpha()
                CARD_IMAGES[f"{rank.name}_{suit.name}"] = pygame.transform.smoothscale(img, (CARD_WIDTH, CARD_HEIGHT))

class Button:
    def __init__(self, x, y, width, height, text, bg_color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.bg_color = bg_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, width=2, border_radius=5)
        text_surf = font.render(self.text, True, BLACK)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_card(surface, card: Card, x: int, y: int, hidden: bool = False):
    if hidden and "BACK" in CARD_IMAGES:
        surface.blit(CARD_IMAGES["BACK"], (x, y))
        return
    elif not hidden and card and f"{card.rank.name}_{card.suit.name}" in CARD_IMAGES:
        surface.blit(CARD_IMAGES[f"{card.rank.name}_{card.suit.name}"], (x, y))
        return
    card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    pygame.draw.rect(surface, WHITE, card_rect, border_radius=8)
    pygame.draw.rect(surface, BLACK, card_rect, width=2, border_radius=8)
    if hidden:
        pygame.draw.rect(surface, BLUE, card_rect.inflate(-16, -16), border_radius=4)
        return
    color = RED if card.suit in (Suit.HEARTS, Suit.DIAMONDS) else BLACK
    text_surf = font.render(f"{card.rank.value}{card.suit.value}", True, color)
    surface.blit(text_surf, text_surf.get_rect(center=card_rect.center))

def draw_stats(player):
    stats = font.render(f"{player.name} | Bankroll: ${player.bankroll} | W: {player.wins} L: {player.losses} P: {player.pushes}", True, WHITE)
    screen.blit(stats, (20, 20))
    if player.bankroll <= 0:
        warning = font.render("BROKE! +$500 Auto-Refill activated!", True, GOLD)
        screen.blit(warning, (20, 60))
        player.bankroll += 500

def advance_turn(player, dealer_hand, active_hand_idx):
    if active_hand_idx + 1 < len(player.hands):
        return "PLAYER_TURN", active_hand_idx + 1, f"Playing Hand {active_hand_idx + 2}"
    else:
        if all(h.is_bust() for h in player.hands):
            outcomes = blackjack_settle(player, dealer_hand)
            return "GAME_OVER", active_hand_idx, f"Result: {', '.join(outcomes)}"
        return "DEALER_TURN", active_hand_idx, "Dealer's Turn..."

# --- SCENES ---

def run_menu(player, clock):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    
    while True:
        btn_bj = Button(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 140, 400, 70, "Play Blackjack (Local)", GRAY)
        btn_holdem = Button(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50, 400, 70, "Play Ultimate Hold'em (Local)", GRAY)
        btn_multi = Button(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 40, 400, 70, "Multiplayer Table (Online)", GOLD)
        btn_quit = Button(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 130, 400, 70, "Quit Game", RED)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_bj.is_clicked(event.pos): return "BLACKJACK"
                if btn_holdem.is_clicked(event.pos): return "HOLDEM"
                if btn_multi.is_clicked(event.pos): return "MULTIPLAYER"
                if btn_quit.is_clicked(event.pos): return "QUIT"

        screen.fill(TABLE_COLOR)
        title = large_font.render("ULTIMATE CASINO", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, int(SCREEN_HEIGHT * 0.15)))
        draw_stats(player)
        btn_bj.draw(screen)
        btn_holdem.draw(screen)
        btn_multi.draw(screen)
        btn_quit.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def run_blackjack(player, clock):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    deck = Deck.new_shuffled()
    dealer_hand = Hand()
    state = "BETTING"
    message = "Place your bet!"
    current_bet = 0
    active_hand_idx = 0
    dealer_blackjack = False

    while True:
        btn_chip_10 = Button(SCREEN_WIDTH//2 - 215, SCREEN_HEIGHT - 160, 100, 50, "+ $10", WHITE)
        btn_chip_50 = Button(SCREEN_WIDTH//2 - 105, SCREEN_HEIGHT - 160, 100, 50, "+ $50", WHITE)
        btn_clear = Button(SCREEN_WIDTH//2 + 5, SCREEN_HEIGHT - 160, 100, 50, "Clear", RED)
        btn_deal = Button(SCREEN_WIDTH//2 + 115, SCREEN_HEIGHT - 160, 100, 50, "Deal", GOLD)
        btn_menu = Button(SCREEN_WIDTH - 220, 20, 200, 50, "Main Menu", GRAY)
        
        btn_hit = Button(SCREEN_WIDTH//2 - 255, SCREEN_HEIGHT - 120, 120, 50, "Hit", WHITE)
        btn_stand = Button(SCREEN_WIDTH//2 - 125, SCREEN_HEIGHT - 120, 120, 50, "Stand", WHITE)
        btn_double = Button(SCREEN_WIDTH//2 + 5, SCREEN_HEIGHT - 120, 120, 50, "Double", GOLD)
        btn_split = Button(SCREEN_WIDTH//2 + 135, SCREEN_HEIGHT - 120, 120, 50, "Split", BLUE)
        
        btn_insure_yes = Button(SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT - 120, 150, 50, "Buy Insurance", GOLD)
        btn_insure_no = Button(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT - 120, 150, 50, "Decline", RED)
        btn_next = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 120, 200, 50, "Next Round", GOLD)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_menu.is_clicked(event.pos): return "MENU"

                if state == "BETTING":
                    if btn_chip_10.is_clicked(event.pos) and player.bankroll >= current_bet + 10: current_bet += 10
                    elif btn_chip_50.is_clicked(event.pos) and player.bankroll >= current_bet + 50: current_bet += 50
                    elif btn_clear.is_clicked(event.pos): current_bet = 0
                    elif btn_deal.is_clicked(event.pos) and current_bet > 0:
                        player.bankroll -= current_bet
                        player.hands = [Hand(cards=[], bet=current_bet)]
                        dealer_hand = Hand(cards=[])
                        active_hand_idx = 0
                        message = "Dealing..."
                        
                        deal_sequence = [
                            (player.hands[0], deck.deal(1)[0]),
                            (dealer_hand, deck.deal(1)[0]),
                            (player.hands[0], deck.deal(1)[0]),
                            (dealer_hand, deck.deal(1)[0])
                        ]
                        
                        for hand_target, card in deal_sequence:
                            hand_target.cards.append(card)
                            
                            screen.fill(TABLE_COLOR)
                            draw_stats(player)
                            btn_menu.draw(screen)
                            msg_text = large_font.render(message, True, WHITE)
                            screen.blit(msg_text, (SCREEN_WIDTH//2 - msg_text.get_width()//2, 280))
                            
                            if dealer_hand.cards:
                                dealer_x = SCREEN_WIDTH//2 - (len(dealer_hand.cards) * 90) // 2
                                dealer_lbl = font.render("Dealer:", True, WHITE)
                                screen.blit(dealer_lbl, (dealer_x, 60))
                                for i, c in enumerate(dealer_hand.cards):
                                    draw_card(screen, c, dealer_x + (i * 90), 100, hidden=(i == 1))
                                    
                            if player.hands[0].cards:
                                hand_center_x = SCREEN_WIDTH // 2
                                hand_x = hand_center_x - (len(player.hands[0].cards) * 30) // 2 - (CARD_WIDTH // 2)
                                lbl = font.render(f"Hand 1 (Bet: ${player.hands[0].bet})", True, HIGHLIGHT)
                                screen.blit(lbl, (hand_center_x - lbl.get_width()//2, 380))
                                for c_idx, c in enumerate(player.hands[0].cards): 
                                    draw_card(screen, c, hand_x + (c_idx * 30), 420)
                            
                            pygame.display.flip()
                            pygame.time.delay(800)

                        dealer_blackjack = dealer_hand.is_blackjack()
                        if dealer_hand.cards[0].rank == Rank.ACE:
                            state = "INSURANCE"
                            message = f"Insurance? (Costs ${current_bet // 2})"
                        elif player.hands[0].is_blackjack() or dealer_blackjack:
                            state = "GAME_OVER"
                            outcomes = blackjack_settle(player, dealer_hand)
                            message = f"Result: {outcomes[0]}"
                        else:
                            state = "PLAYER_TURN"
                            message = "Your Turn"

                elif state == "INSURANCE":
                    hand = player.hands[0]
                    insure_cost = hand.bet // 2
                    if btn_insure_yes.is_clicked(event.pos) and player.bankroll >= insure_cost:
                        player.bankroll -= insure_cost
                        hand.insurance_bet = insure_cost
                        resolve_insurance(player, dealer_blackjack)
                        if dealer_blackjack:
                            state, outcomes = "GAME_OVER", blackjack_settle(player, dealer_hand)
                            message = "Dealer Blackjack! Insurance Paid."
                        else:
                            state, message = "PLAYER_TURN", "No Blackjack."
                    elif btn_insure_no.is_clicked(event.pos):
                        if dealer_blackjack:
                            state, outcomes = "GAME_OVER", blackjack_settle(player, dealer_hand)
                            message = "Dealer Blackjack!"
                        else:
                            state, message = "PLAYER_TURN", "No Blackjack."

                elif state == "PLAYER_TURN":
                    hand = player.hands[active_hand_idx]
                    if btn_hit.is_clicked(event.pos):
                        hand.cards.extend(deck.deal(1))
                        if hand.is_bust(): state, active_hand_idx, message = advance_turn(player, dealer_hand, active_hand_idx)
                    elif btn_stand.is_clicked(event.pos):
                        state, active_hand_idx, message = advance_turn(player, dealer_hand, active_hand_idx)
                    elif btn_double.is_clicked(event.pos) and len(hand.cards) == 2 and player.bankroll >= hand.bet:
                        player.bankroll -= hand.bet
                        hand.bet *= 2
                        hand.doubled = True
                        hand.cards.extend(deck.deal(1))
                        state, active_hand_idx, message = advance_turn(player, dealer_hand, active_hand_idx)
                    elif btn_split.is_clicked(event.pos) and hand.can_split() and player.bankroll >= hand.bet:
                        player.bankroll -= hand.bet
                        h1 = Hand(cards=[hand.cards[0]], bet=hand.bet, is_split_hand=True)
                        h2 = Hand(cards=[hand.cards[1]], bet=hand.bet, is_split_hand=True)
                        h1.cards.extend(deck.deal(1))
                        h2.cards.extend(deck.deal(1))
                        player.hands.pop(active_hand_idx)
                        player.hands.insert(active_hand_idx, h2)
                        player.hands.insert(active_hand_idx, h1)

                elif state == "GAME_OVER":
                    if btn_next.is_clicked(event.pos):
                        if not deck.has_cards(20): deck = Deck.new_shuffled()
                        player.hands, dealer_hand, current_bet, state, message = [], Hand(), 0, "BETTING", "Place your bet!"

        if state == "DEALER_TURN":
            while True:
                screen.fill(TABLE_COLOR)
                draw_stats(player)
                btn_menu.draw(screen)
                
                msg_text = large_font.render(message, True, WHITE)
                screen.blit(msg_text, (SCREEN_WIDTH//2 - msg_text.get_width()//2, 280))
                
                dealer_x = SCREEN_WIDTH//2 - (len(dealer_hand.cards) * 90) // 2
                dealer_lbl = font.render("Dealer:", True, WHITE)
                screen.blit(dealer_lbl, (dealer_x, 60))
                for i, card in enumerate(dealer_hand.cards):
                    draw_card(screen, card, dealer_x + (i * 90), 100, hidden=False) 
                
                section_width = SCREEN_WIDTH // (len(player.hands) + 1)
                for h_idx, hand in enumerate(player.hands):
                    hand_center_x = section_width * (h_idx + 1)
                    hand_x = hand_center_x - (len(hand.cards) * 30) // 2 - (CARD_WIDTH // 2)
                    hand_total, _ = hand.value()
                    lbl = font.render(f"Hand {h_idx+1} (Total: {hand_total} | Bet: ${hand.bet})", True, WHITE)
                    screen.blit(lbl, (hand_center_x - lbl.get_width()//2, 380))
                    for c_idx, card in enumerate(hand.cards): 
                        draw_card(screen, card, hand_x + (c_idx * 30), 420)
                
                pygame.display.flip()
                pygame.time.delay(1000) 
                
                dealer_total, is_soft = dealer_hand.value()
                if dealer_total < 17 or (dealer_total == 17 and is_soft):
                    dealer_hand.cards.extend(deck.deal(1))
                else:
                    state = "GAME_OVER"
                    outcomes = blackjack_settle(player, dealer_hand)
                    message = f"Result: {', '.join(outcomes)}"
                    break 

        screen.fill(TABLE_COLOR)
        draw_stats(player)
        btn_menu.draw(screen)
        
        if state == "BETTING":
            pending_text = font.render(f"Pending Bet: ${current_bet}", True, GOLD)
            screen.blit(pending_text, (SCREEN_WIDTH//2 - pending_text.get_width()//2, SCREEN_HEIGHT - 220))
            
        msg_text = large_font.render(message, True, WHITE)
        screen.blit(msg_text, (SCREEN_WIDTH//2 - msg_text.get_width()//2, 280))

        if state != "BETTING" and player.hands:
            dealer_x = SCREEN_WIDTH//2 - (len(dealer_hand.cards) * 90) // 2
            dealer_lbl = font.render("Dealer:", True, WHITE)
            screen.blit(dealer_lbl, (dealer_x, 60))
            
            for i, card in enumerate(dealer_hand.cards):
                draw_card(screen, card, dealer_x + (i * 90), 100, hidden=(i == 1 and state in ["PLAYER_TURN", "INSURANCE"]))
            
            section_width = SCREEN_WIDTH // (len(player.hands) + 1)
            for h_idx, hand in enumerate(player.hands):
                hand_center_x = section_width * (h_idx + 1)
                hand_x = hand_center_x - (len(hand.cards) * 30) // 2 - (CARD_WIDTH // 2)
                
                hand_total, _ = hand.value()
                color = HIGHLIGHT if (state == "PLAYER_TURN" and h_idx == active_hand_idx) else WHITE
                lbl = font.render(f"Hand {h_idx+1} (Total: {hand_total} | Bet: ${hand.bet})", True, color)
                screen.blit(lbl, (hand_center_x - lbl.get_width()//2, 380))
                
                for c_idx, card in enumerate(hand.cards): 
                    draw_card(screen, card, hand_x + (c_idx * 30), 420)

        if state == "BETTING":
            btn_chip_10.draw(screen); btn_chip_50.draw(screen); btn_clear.draw(screen); btn_deal.draw(screen)
        elif state == "INSURANCE":
            btn_insure_yes.draw(screen); btn_insure_no.draw(screen)
        elif state == "PLAYER_TURN":
            btn_hit.draw(screen); btn_stand.draw(screen)
            if len(player.hands[active_hand_idx].cards) == 2 and player.bankroll >= player.hands[active_hand_idx].bet: btn_double.draw(screen)
            if player.hands[active_hand_idx].can_split() and player.bankroll >= player.hands[active_hand_idx].bet: btn_split.draw(screen)
        elif state == "GAME_OVER": btn_next.draw(screen)

        pygame.display.flip()
        clock.tick(60)


def run_holdem(player, clock):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    deck = Deck.new_shuffled()
    h_state = HoldemState()
    phase = "BET_ANTE"
    message = ""
    current_ante = 0

    def animate_community(num_cards):
        new_cards = deck.deal(num_cards)
        for card in new_cards:
            h_state.community.append(card)
            
            screen.fill((20, 100, 50))
            draw_stats(player)
            btn_menu = Button(SCREEN_WIDTH - 220, 20, 200, 50, "Main Menu", GRAY)
            btn_menu.draw(screen)
            
            dealer_x = SCREEN_WIDTH//2 - (len(h_state.dealer_cards)*90)//2
            d_lbl = font.render("Dealer Cards:", True, WHITE)
            screen.blit(d_lbl, (dealer_x, 70))
            for i, c in enumerate(h_state.dealer_cards):
                draw_card(screen, c, dealer_x + (i * 90), 100, hidden=True) 
            
            comm_x = SCREEN_WIDTH//2 - (len(h_state.community)*90)//2
            c_lbl = font.render("Community:", True, WHITE)
            screen.blit(c_lbl, (SCREEN_WIDTH//2 - c_lbl.get_width()//2, 220))
            for i, c in enumerate(h_state.community):
                draw_card(screen, c, comm_x + (i * 90), 250)

            player_x = SCREEN_WIDTH//2 - (len(h_state.player_cards)*90)//2
            p_lbl = font.render("Your Hole Cards:", True, WHITE)
            screen.blit(p_lbl, (player_x, 370))
            for i, c in enumerate(h_state.player_cards):
                draw_card(screen, c, player_x + (i * 90), 400)
            
            stats_lbl = font.render(f"Ante: ${h_state.ante} | Blind: ${h_state.blind} | Play: ${h_state.play_bet}", True, GOLD)
            screen.blit(stats_lbl, (20, SCREEN_HEIGHT - 60))

            msg_text = font.render("Dealing...", True, WHITE)
            screen.blit(msg_text, (SCREEN_WIDTH//2 - msg_text.get_width()//2, 520))

            pygame.display.flip()
            pygame.time.delay(600)

    while True:
        btn_chip_10 = Button(SCREEN_WIDTH//2 - 215, SCREEN_HEIGHT - 120, 100, 50, "+ $10", WHITE)
        btn_chip_50 = Button(SCREEN_WIDTH//2 - 105, SCREEN_HEIGHT - 120, 100, 50, "+ $50", WHITE)
        btn_clear = Button(SCREEN_WIDTH//2 + 5, SCREEN_HEIGHT - 120, 100, 50, "Clear", RED)
        btn_deal = Button(SCREEN_WIDTH//2 + 115, SCREEN_HEIGHT - 120, 100, 50, "Deal", GOLD)
        btn_menu = Button(SCREEN_WIDTH - 220, 20, 200, 50, "Main Menu", GRAY)
        
        btn_check = Button(SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT - 100, 150, 50, "Check", WHITE)
        btn_fold = Button(SCREEN_WIDTH//2 - 160, SCREEN_HEIGHT - 100, 150, 50, "Fold", RED)
        btn_bet4x = Button(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT - 100, 150, 50, "Bet 4x", GOLD)
        btn_bet2x = Button(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT - 100, 150, 50, "Bet 2x", GOLD)
        btn_bet1x = Button(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT - 100, 150, 50, "Bet 1x", GOLD)
        btn_next = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50, "Next Round", GOLD)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_menu.is_clicked(event.pos): return "MENU"

                if phase == "BET_ANTE":
                    if btn_chip_10.is_clicked(event.pos) and player.bankroll >= (current_ante + 10) * 2: current_ante += 10
                    elif btn_chip_50.is_clicked(event.pos) and player.bankroll >= (current_ante + 50) * 2: current_ante += 50
                    elif btn_clear.is_clicked(event.pos): current_ante = 0
                    elif btn_deal.is_clicked(event.pos) and current_ante > 0:
                        h_state.ante = current_ante
                        h_state.blind = current_ante
                        player.bankroll -= (current_ante * 2)
                        
                        h_state.player_cards.extend(deck.deal(2))
                        h_state.dealer_cards.extend(deck.deal(2))
                        phase = "PREFLOP"
                        message = "Pre-Flop: Check or Bet 4x Ante?"

                elif phase == "PREFLOP":
                    can_bet = player.bankroll >= h_state.ante * 4
                    if btn_check.is_clicked(event.pos):
                        animate_community(3)
                        phase, message = "FLOP", "Flop: Check or Bet 2x Ante?"
                    elif btn_bet4x.is_clicked(event.pos) and can_bet:
                        h_state.play_bet = h_state.ante * 4
                        player.bankroll -= h_state.play_bet
                        animate_community(5)
                        phase = "GAME_OVER"
                        message, _, _, _ = holdem_settle(player, h_state)

                elif phase == "FLOP":
                    can_bet = player.bankroll >= h_state.ante * 2
                    if btn_check.is_clicked(event.pos):
                        animate_community(2)
                        phase, message = "RIVER", "River: Fold or Bet 1x Ante?"
                    elif btn_bet2x.is_clicked(event.pos) and can_bet:
                        h_state.play_bet = h_state.ante * 2
                        player.bankroll -= h_state.play_bet
                        animate_community(2)
                        phase = "GAME_OVER"
                        message, _, _, _ = holdem_settle(player, h_state)

                elif phase == "RIVER":
                    can_bet = player.bankroll >= h_state.ante
                    if btn_fold.is_clicked(event.pos):
                        h_state.folded = True
                        phase = "GAME_OVER"
                        message, _, _, _ = holdem_settle(player, h_state)
                    elif btn_bet1x.is_clicked(event.pos) and can_bet:
                        h_state.play_bet = h_state.ante
                        player.bankroll -= h_state.play_bet
                        phase = "GAME_OVER"
                        message, _, _, _ = holdem_settle(player, h_state)

                elif phase == "GAME_OVER":
                    if btn_next.is_clicked(event.pos):
                        if not deck.has_cards(20): deck = Deck.new_shuffled()
                        h_state = HoldemState()
                        current_ante = 0
                        phase = "BET_ANTE"
                        message = ""

        screen.fill((20, 100, 50))
        draw_stats(player)
        btn_menu.draw(screen)

        if phase == "BET_ANTE":
            pending_text = font.render(f"Pending Ante: ${current_ante} (Total Cost: ${current_ante*2})", True, GOLD)
            screen.blit(pending_text, (SCREEN_WIDTH//2 - pending_text.get_width()//2, SCREEN_HEIGHT - 180))
        
        if phase != "BET_ANTE":
            dealer_x = SCREEN_WIDTH//2 - (len(h_state.dealer_cards)*90)//2
            d_lbl = font.render("Dealer Cards:", True, WHITE)
            screen.blit(d_lbl, (dealer_x, 70))
            for i, card in enumerate(h_state.dealer_cards):
                draw_card(screen, card, dealer_x + (i * 90), 100, hidden=(phase != "GAME_OVER"))
            
            comm_x = SCREEN_WIDTH//2 - (len(h_state.community)*90)//2
            if h_state.community:
                c_lbl = font.render("Community:", True, WHITE)
                screen.blit(c_lbl, (SCREEN_WIDTH//2 - c_lbl.get_width()//2, 220))
                for i, card in enumerate(h_state.community):
                    draw_card(screen, card, comm_x + (i * 90), 250)

            player_x = SCREEN_WIDTH//2 - (len(h_state.player_cards)*90)//2
            p_lbl = font.render("Your Hole Cards:", True, WHITE)
            screen.blit(p_lbl, (player_x, 370))
            for i, card in enumerate(h_state.player_cards):
                draw_card(screen, card, player_x + (i * 90), 400)
            
            stats_lbl = font.render(f"Ante: ${h_state.ante} | Blind: ${h_state.blind} | Play: ${h_state.play_bet}", True, GOLD)
            screen.blit(stats_lbl, (20, SCREEN_HEIGHT - 60))

        lines = message.split("\n")
        msg_start_y = 520 
        for i, line in enumerate(lines):
            msg_text = font.render(line, True, WHITE)
            screen.blit(msg_text, (SCREEN_WIDTH//2 - msg_text.get_width()//2, msg_start_y + (i * 30)))

        if phase == "BET_ANTE":
            btn_chip_10.draw(screen); btn_chip_50.draw(screen); btn_clear.draw(screen); btn_deal.draw(screen)
        elif phase == "PREFLOP":
            btn_check.draw(screen)
            if player.bankroll >= h_state.ante * 4: btn_bet4x.draw(screen)
        elif phase == "FLOP":
            btn_check.draw(screen)
            if player.bankroll >= h_state.ante * 2: btn_bet2x.draw(screen)
        elif phase == "RIVER":
            btn_fold.draw(screen)
            if player.bankroll >= h_state.ante: btn_bet1x.draw(screen)
        elif phase == "GAME_OVER":
            btn_next.draw(screen)

        pygame.display.flip()
        clock.tick(60)

def run_multiplayer(player, clock):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    
    try:
        net = Network(player.bankroll)
        my_id = net.player_id
    except:
        print("Ο Server είναι κλειστός!")
        return "MENU"

    pending_raise = 10 
    game_state = None

    while True:
        action_to_send = "GET"
        
        # 1. Ορίζουμε τα κουμπιά ΠΑΝΤΑ για να μην κρασάρει ποτέ!
        btn_start = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 120, 200, 60, "Start Game", GOLD)
        btn_next_hand = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 120, 200, 60, "Next Hand", BLUE)
        btn_fold = Button(SCREEN_WIDTH//2 - 380, SCREEN_HEIGHT - 120, 150, 60, "Fold", RED)
        btn_call = Button(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 120, 150, 60, "Check / Call", WHITE)
        btn_raise = Button(SCREEN_WIDTH//2 - 20, SCREEN_HEIGHT - 120, 180, 60, f"Raise +${pending_raise}", GOLD)
        btn_chip_10 = Button(SCREEN_WIDTH//2 + 180, SCREEN_HEIGHT - 120, 70, 60, "+10", GRAY)
        btn_chip_50 = Button(SCREEN_WIDTH//2 + 260, SCREEN_HEIGHT - 120, 70, 60, "+50", GRAY)
        btn_clear = Button(SCREEN_WIDTH//2 + 340, SCREEN_HEIGHT - 120, 90, 60, "Clear", RED)
        btn_menu = Button(SCREEN_WIDTH - 220, 20, 200, 50, "Leave Table", RED)

        is_my_turn = False
        if game_state:
            is_my_turn = (game_state.get_current_player_id() == my_id) and game_state.game_phase not in ["WAITING", "SHOWDOWN"]
            call_amt = game_state.current_highest_bet - game_state.players[my_id].get("current_bet", 0) if my_id in game_state.players else 0
            
            # Ανανέωση των κειμένων των κουμπιών
            btn_call.text = "Check" if call_amt == 0 else f"Call ${call_amt}"
            btn_raise.text = f"Raise +${pending_raise}"

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                net.disconnect()
                return "QUIT"
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_menu.is_clicked(event.pos): 
                    net.disconnect()
                    return "MENU"
                
                if game_state:
                    if game_state.game_phase == "WAITING" and btn_start.is_clicked(event.pos):
                        action_to_send = "START"
                    elif game_state.game_phase == "SHOWDOWN" and btn_next_hand.is_clicked(event.pos):
                        action_to_send = "END_HAND"
                    elif is_my_turn:
                        if btn_fold.is_clicked(event.pos): action_to_send = "ACTION:FOLD"
                        elif btn_call.is_clicked(event.pos): action_to_send = "ACTION:CALL"
                        elif btn_raise.is_clicked(event.pos):
                            action_to_send = f"ACTION:RAISE:{pending_raise}"
                            pending_raise = 10 
                        elif btn_chip_10.is_clicked(event.pos): pending_raise += 10
                        elif btn_chip_50.is_clicked(event.pos): pending_raise += 50
                        elif btn_clear.is_clicked(event.pos): pending_raise = 10

        try:
            game_state = net.send(action_to_send)
        except Exception as e:
            import traceback
            print(f"Σφάλμα Multiplayer: {e}")
            traceback.print_exc()  # Αυτό θα τυπώσει το πραγματικό πρόβλημα!
            return "MENU"

        screen.fill(DARK_GREEN)
        
        if game_state:
            turn_msg = " | YOUR TURN!" if is_my_turn else ""
            title = font.render(f"Multiplayer Lobby - You are Player {my_id} | Phase: {game_state.game_phase}{turn_msg}", True, WHITE)
            screen.blit(title, (20, 20))
            
            pot_text = large_font.render(f"Shared Pot: ${game_state.pot}", True, GOLD)
            screen.blit(pot_text, (SCREEN_WIDTH//2 - pot_text.get_width()//2, 80))
            
            if game_state.community_cards:
                comm_x = SCREEN_WIDTH//2 - (len(game_state.community_cards)*90)//2
                for i, card in enumerate(game_state.community_cards):
                    draw_card(screen, card, comm_x + (i * 90), 160)

            y_offset = 80
            for pid, p_data in game_state.players.items():
                color = HIGHLIGHT if pid == game_state.get_current_player_id() else WHITE
                status = " (Folded)" if p_data.get("folded") else f" (Bet: ${p_data.get('current_bet', 0)})"
                p_text = font.render(f"P{pid} | ${p_data['bankroll']}{status}", True, color)
                screen.blit(p_text, (SCREEN_WIDTH - 300, y_offset))
                y_offset += 40

            if game_state.game_phase == "SHOWDOWN":
                sd_msg = font.render(game_state.showdown_message, True, GOLD)
                screen.blit(sd_msg, (SCREEN_WIDTH//2 - sd_msg.get_width()//2, 330))
                
                ox = 50
                for pid, p_data in game_state.players.items():
                    if not p_data.get("folded") and p_data.get("cards"):
                        lbl = font.render(f"Player {pid}", True, WHITE)
                        screen.blit(lbl, (ox, 380))
                        for i, c in enumerate(p_data["cards"]):
                            draw_card(screen, c, ox + (i * 40), 420)
                        ox += 150
            
            elif game_state.game_phase != "WAITING":
                my_cards = game_state.players[my_id]["cards"]
                if my_cards and not game_state.players[my_id]["folded"]:
                    player_x = SCREEN_WIDTH//2 - (len(my_cards)*90)//2
                    p_lbl = font.render("Your Hole Cards:", True, WHITE)
                    screen.blit(p_lbl, (player_x, 470))
                    for i, card in enumerate(my_cards):
                        draw_card(screen, card, player_x + (i * 90), 500)
                elif game_state.players[my_id]["folded"]:
                    msg = font.render("You Folded.", True, RED)
                    screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 500))

            if game_state.game_phase == "WAITING":
                btn_start.draw(screen)
            elif game_state.game_phase == "SHOWDOWN":
                btn_next_hand.draw(screen)
            elif is_my_turn:
                btn_fold.draw(screen)
                btn_call.draw(screen)
                btn_raise.draw(screen)
                btn_chip_10.draw(screen)
                btn_chip_50.draw(screen)
                btn_clear.draw(screen)
            elif game_state.game_phase != "SHOWDOWN" and not game_state.players[my_id].get("folded"):
                wait_msg = font.render("Waiting for other players...", True, GRAY)
                screen.blit(wait_msg, (SCREEN_WIDTH//2 - wait_msg.get_width()//2, SCREEN_HEIGHT - 100))

        btn_menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def run_setup(clock):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    input_text = ""  
    
    while True:
        btn_start = Button(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 100, 400, 80, "Confirm & Start", GOLD)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT", 0
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_start.is_clicked(event.pos):
                    final_amount = int(input_text) if input_text else 0
                    if final_amount > 0: return "MENU", final_amount
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE: input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    final_amount = int(input_text) if input_text else 0
                    if final_amount > 0: return "MENU", final_amount
                elif event.unicode.isnumeric():
                    if len(input_text) < 7: input_text += event.unicode

        screen.fill(TABLE_COLOR)
        title = large_font.render("ENTER STARTING BANKROLL", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, int(SCREEN_HEIGHT * 0.2)))
        
        input_box = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 35, 300, 70)
        pygame.draw.rect(screen, WHITE, input_box, border_radius=5)
        pygame.draw.rect(screen, BLACK, input_box, width=3, border_radius=5)
        
        text_surf = large_font.render(f"${input_text}" if input_text else "$", True, BLACK)
        screen.blit(text_surf, text_surf.get_rect(center=input_box.center))
        btn_start.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def main():
    load_assets()
    clock = pygame.time.Clock()
    player = None
    
    current_scene = "SETUP"
    while current_scene != "QUIT":
        if current_scene == "SETUP":
            current_scene, start_amount = run_setup(clock)
            if current_scene != "QUIT":
                player = Player(name="Player", bankroll=start_amount)
        elif current_scene == "MENU":
            current_scene = run_menu(player, clock)
        elif current_scene == "BLACKJACK":
            current_scene = run_blackjack(player, clock)
        elif current_scene == "HOLDEM":
            current_scene = run_holdem(player, clock)
        elif current_scene == "MULTIPLAYER":
            current_scene = run_multiplayer(player, clock)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()