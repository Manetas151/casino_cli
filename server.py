import socket
import threading
import pickle
from game_state import GameState

HOST = '127.0.0.1' 
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind((HOST, PORT))
except socket.error as e:
    print(str(e))

server.listen()
print(f"[*] Ο Server ξεκίνησε. Περιμένει συνδέσεις στο {HOST}:{PORT}...")

game = GameState()

def threaded_client(conn, player_id):
    conn.send(str.encode(str(player_id)))
    try:
        bankroll_data = conn.recv(2048).decode()
        starting_bankroll = int(bankroll_data)
    except:
        starting_bankroll = 1000 
        
    game.add_player(player_id, starting_bankroll)
    
    while True:
        try:
            data = conn.recv(8192)
            if not data:
                break
            
            action = data.decode('utf-8').strip()
            
            if action == "START" and game.game_phase == "WAITING":
                game.start_hand()
            
            elif "ACTION:" in action and game.get_current_player_id() == player_id:
                try:
                    # Καθαρισμός του πακέτου από τυχόν κολλημένα "GET" λόγω ταχύτητας
                    idx = action.rfind("ACTION:")
                    clean = action[idx:].replace("GET", "").strip()
                    parts = clean.split(":")
                    act = parts[1]
                    player = game.players[player_id]
                    
                    if act == "FOLD":
                        player["folded"] = True
                        player["has_acted"] = True
                        game.next_turn()
                        
                    elif act == "CALL":
                        call_amount = game.current_highest_bet - player["current_bet"]
                        if player["bankroll"] <= call_amount:
                            call_amount = player["bankroll"] 
                            
                        player["bankroll"] -= call_amount
                        player["current_bet"] += call_amount
                        game.pot += call_amount
                        player["has_acted"] = True
                        game.next_turn()
                            
                    elif act == "RAISE":
                        added_raise = int(parts[2])
                        call_amount = game.current_highest_bet - player["current_bet"]
                        total_cost = call_amount + added_raise
                        
                        if player["bankroll"] <= total_cost:
                            total_cost = player["bankroll"] 
                            
                        player["bankroll"] -= total_cost
                        player["current_bet"] += total_cost
                        game.pot += total_cost
                        
                        if player["current_bet"] > game.current_highest_bet:
                            game.current_highest_bet = player["current_bet"]
                            for pid in game.active_players:
                                if pid != player_id and not game.players.get(pid, {}).get("folded", True):
                                    game.players[pid]["has_acted"] = False
                                    
                        player["has_acted"] = True
                        game.next_turn()
                except Exception as e:
                    print(f"Σφάλμα κατά την εκτέλεση της κίνησης: {e}")
                    
            elif action == "END_HAND":
                game.game_phase = "WAITING"
                    
            conn.sendall(pickle.dumps(game))
        except Exception as e:
            break
            
    print(f"[-] Ο Παίκτης {player_id} αποσυνδέθηκε.")
    if player_id in game.players:
        del game.players[player_id]
        if len(game.players) < 2:
            game.game_phase = "WAITING"
    conn.close()

current_player = 0
while True:
    conn, addr = server.accept()
    print(f"[+] Νέα σύνδεση από: {addr}")
    threading.Thread(target=threaded_client, args=(conn, str(current_player))).start()
    current_player += 1