import socket
import re
import threading

# Define the address and port for the proxy server
#HOST = '192.168.0.111'  # IP address home
HOST = '10.241.247.252' # IP address school
PORT = 8080

# Define keywords to be replaced
KEYWORD_MAPPING = {
    b'Smiley': b'Trolly',
    b' Stockholm': b' Linkoping',
    b'./smiley.jpg': b'./trolly.jpg'
}

def handle_client(client_socket):
    server_socket = None
    
    try:
        # Receive data from the client
        request_data = client_socket.recv(4096)

        print("[*] Received request from client:")
        print(request_data.decode('utf-8'))  # Print received data for debugging

        # Extract the URL from the HTTP request
        url_match = re.search(b'Host: (.*?)\r\n', request_data)
        if url_match:
            hostname = url_match.group(1).decode('utf-8')
        else:
            client_socket.close()
            return

        # Connect to the web server using the extracted hostname
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((hostname, 80))

        # Forward the client's request to the server
        server_socket.send(request_data)

        # Receive data from the server
        server_response = b''
        while True:
            chunk = server_socket.recv(4096)
            if not chunk:
                break
            server_response += chunk

        print("[*] Received response from server:")

        # Replace keywords in the response
        modified_response = server_response
        for keyword, replacement in KEYWORD_MAPPING.items():
            modified_response = modified_response.replace(keyword, replacement)

        # Send the modified content to the browser
        client_socket.sendall(modified_response)

        print("[*] Sent response to client.")

    except Exception as e:
        print("[!] Error handling client request:", e)

    finally:
        # Close the sockets
        client_socket.close()
        if server_socket:
            server_socket.close()

def main():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    server_socket.bind((HOST, PORT))

    # Start listening for incoming connections
    server_socket.listen(5)
    print(f'[*] Listening on {HOST}:{PORT}')

    try:
        while True:
            # Accept incoming client connection
            client_socket, addr = server_socket.accept()
            print(f'[*] Accepted connection from {addr[0]}:{addr[1]}')

            # Create a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()

    except KeyboardInterrupt:
        print("[*] Shutting down the proxy server.")
        server_socket.close()

if __name__ == "__main__":
    main()