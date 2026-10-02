import socket
import threading
import pickle
from game_state import GameState

HOST = '192.168.1.18' 
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind((HOST, PORT))
except socket.error as e:
    print(str(e))

server.listen()
print(f"[*] Ο Server ξεκίνησε. Περιμένει συνδέσεις στο {HOST}:{PORT}...")

game = GameState()

def threaded_client(conn):
    try:
        # Παίρνουμε το όνομα και το bankroll
        init_data = conn.recv(2048).decode().split(":")
        player_name = init_data[0]
        starting_bankroll = int(init_data[1]) if len(init_data) > 1 else 1000
        
        # Στέλνουμε πίσω το όνομα ως επιβεβαίωση ID
        conn.send(str.encode(player_name))
    except:
        conn.close()
        return
        
    # Αν ο παίκτης ΔΕΝ υπάρχει ήδη (νέος παίκτης), τον προσθέτουμε στο τραπέζι
    if player_name not in game.players:
        game.add_player(player_name, starting_bankroll)
    
    player_id = player_name
    
    while True:
        try:
            data = conn.recv(8192)
            if not data:
                break
            
            action = data.decode('utf-8').strip()
            
            # --- ΕΠΑΝΑΦΟΡΑ ΤΗΣ ΛΟΓΙΚΗΣ ΤΟΥ ΠΑΙΧΝΙΔΙΟΥ ---
            if "START" in action and game.game_phase == "WAITING":
                game.start_hand()
            
            elif "ACTION:" in action and game.get_current_player_id() == player_id:
                try:
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
                    
            elif "END_HAND" in action:
                game.game_phase = "WAITING"
            # ---------------------------------------------
            
            data_to_send = pickle.dumps(game)
            if 'struct' in globals():
                size_header = struct.pack(">I", len(data_to_send))
                conn.sendall(size_header + data_to_send)
            else:
                conn.sendall(data_to_send)
                
        except Exception as e:
            break
            
    print(f"[-] Ο Παίκτης {player_id} αποσυνδέθηκε.")
    if player_id in game.players:
        game.players[player_id]["folded"] = True
        game.players[player_id]["has_acted"] = True
        game.next_turn()
    conn.close()
    # Add this at the very bottom of server.py
while True:
    conn, addr = server.accept()
    print(f"[+] Νέα σύνδεση από: {addr}")
    
    # Start a new thread for each connected client
    thread = threading.Thread(target=threaded_client, args=(conn,))
    thread.start()