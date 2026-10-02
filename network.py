import socket
import pickle

class Network:
    def __init__(self, player_name, bankroll):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.1.18"  # Μην ξεχάσεις την IP σου!
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player_id = self.connect(player_name, bankroll)

    def connect(self, player_name, bankroll):
        try:
            self.client.connect(self.addr)
            # Στέλνουμε το Όνομα και το Bankroll χωρισμένα με άνω-κάτω τελεία
            self.client.send(str.encode(f"{player_name}:{bankroll}"))
            pid = self.client.recv(2048).decode()
            return pid
        except socket.error as e:
            print(f"Σφάλμα σύνδεσης: {e}")

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            # Αυξήσαμε το buffer στο 32768 (32KB) για να χωράει όλο το Multiplayer τραπέζι!
            packet = self.client.recv(32768)
            return pickle.loads(packet)
        except socket.error as e:
            print(e)
            
    def disconnect(self):
        self.client.close()