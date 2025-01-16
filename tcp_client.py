import socket
import ssl
import time

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Create SSLContext without loading certificates (no client certificates needed)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_NONE  # Disable server certificate verification (for self-signed cert)

    # Wrap the client socket with SSL
    ssl_client = context.wrap_socket(client, server_hostname="127.0.0.1")
    
    # Connect to the server
    ssl_client.connect(("127.0.0.1", 4444))
    
    print("Sending data to server...")
    start_time = time.time()  # Record start time
    ssl_client.send(b"Hello TCP Server")
    
    response = ssl_client.recv(4096)
    end_time = time.time()  # Record end time
    
    print(f"Received response: {response.decode()}")
    print(f"Request-response round trip time: {end_time - start_time} seconds")

    ssl_client.close()

if __name__ == "__main__":
    main()
