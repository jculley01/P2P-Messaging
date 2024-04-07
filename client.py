import socket
import threading
import requests
import json
import sys

SERVER_URL = "http://127.0.0.1:5000"

class P2PClient:
    def __init__(self, username):
        self.username = username
        self.server_url = SERVER_URL
        self.peers = {}
        self.messages = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 0))
        self.listen_port = self.sock.getsockname()[1]

    def register_with_server(self):
        response = requests.post(f"{self.server_url}/register", json={
            'username': self.username,
            'address': self.sock.getsockname()
        })
        print(response.json())

    def fetch_peers(self):
        response = requests.get(f"{self.server_url}/clients")
        self.peers = response.json()
        print("Available peers:")
        for peer, address in self.peers.items():
            if peer != self.username:
                print(f"{peer} at {address}")

    def listen_for_messages(self):
        self.sock.listen()
        print(f"Listening for messages on port {self.listen_port}")
        while True:
            conn, addr = self.sock.accept()
            threading.Thread(target=self.handle_message, args=(conn,)).start()

    def handle_message(self, conn):
        data = conn.recv(1024).decode('utf-8')
        message = json.loads(data)
        print(f"New message from {message['from']}: {message['content']}")
        conn.close()

    def send_message(self, peer_username, content):
        if peer_username in self.peers:
            peer_address = tuple(self.peers[peer_username])
            message = json.dumps({'from': self.username, 'content': content})
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(peer_address)
                s.sendall(message.encode('utf-8'))
            print(f"Sent message to {peer_username}.")
        else:
            print(f"{peer_username} not found or is offline.")

    def start(self):
        self.register_with_server()
        threading.Thread(target=self.listen_for_messages).start()
        self.fetch_peers()

if __name__ == '__main__':
    username = input("Enter your username: ")
    client = P2PClient(username)
    client.start()

    while True:
        print("\nEnter the username of the peer you want to message (or 'refresh' to update peer list): ")
        peer_username = input()
        if peer_username.lower() == 'refresh':
            client.fetch_peers()
            continue
        content = input("Enter your message: ")
        client.send_message(peer_username, content)
