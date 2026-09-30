import socket
import pickle

class Network:
    def __init__(self, bankroll):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1" 
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player_id = self.connect(bankroll)

    def connect(self, bankroll):
        try:
            self.client.connect(self.addr)
            pid = self.client.recv(2048).decode()
            self.client.send(str.encode(str(bankroll)))
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