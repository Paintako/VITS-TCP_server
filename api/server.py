import socket
import threading
from logs import service_logger
# Define server address and port
SERVER_HOST = ''
SERVER_PORT = 9999

# Function to handle client connections
def request_handler(client_socket, addr):
    logger.info('New client connected: {}'.format(addr))

    # Receive data from client
    data = client_socket.recv(1024).decode()
    logger.info('Data received from client: {}'.format(data))

    # Send data back to client
    resend_data = 'Hello from server'
    client_socket.send(resend_data.encode())

    # Close client connection
    client_socket.close()

def start_server():
    # Create socket for server to listen on
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((SERVER_HOST, SERVER_PORT))
    except socket.error as e:
        logger.error('Bind failed: {}'.format(e))
        return
    
    logger.info('Server started')
    while True:
        # Listen for connections
        server_socket.listen(5)
        # Accept connections, can handle multiple clients by creating a new thread for each client
        conn, addr = server_socket.accept()
        threading.Thread(target=request_handler, args=(conn,addr)).start()

if __name__ == '__main__':
    logger = service_logger.ServiceLogger()
    start_server()
    
