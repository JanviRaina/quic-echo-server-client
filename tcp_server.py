import socket
import ssl

def handle_client(client_socket):
    # Handle client connection
    request = client_socket.recv(1024)
    print(f"Received: {request.decode()}")
    
    # Respond with the same message
    client_socket.send(b"Echo: " + request)
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 4444))
    server.listen(5)
    print("TCP server listening on 127.0.0.1:4444")
    
    # SSL wrap for the server
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="tcp_cert.pem", keyfile="tcp_key.pem")
    
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        
        # Wrap the client connection with SSL
        ssl_client_socket = context.wrap_socket(client_socket, server_side=True)
        
        handle_client(ssl_client_socket)
        
        # Optionally close the server after a single client connection
        print("Closing server after handling one connection.")
        break  # Remove this line if you want the server to keep accepting connections

    server.close()

if __name__ == "__main__":
    start_server()
