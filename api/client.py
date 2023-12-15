import socket

SERVER, PORT = '', 9999

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER, PORT))

    def send(self, data):
        self.sock.sendall(data)

    def receive(self):
        return self.sock.recv(1024)

    def close(self):
        self.sock.close()

if __name__ == '__main__':
    client = Client()
    data = 'Hello World'
    data = data.encode()
    client.send(data)
    print(client.receive().decode())
    client.close()
    