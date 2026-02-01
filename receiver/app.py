"""
Message Receiver/Server Application
Listens for incoming messages from other computers
"""

import socket
import threading
import sys

class MessageReceiver:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
    def start(self):
        """Start the message receiver server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"[SERVER] Listening on {self.host}:{self.port}")
            print("[SERVER] Waiting for incoming messages...\n")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    if self.running:
                        print(f"[ERROR] {e}")
                    
        except Exception as e:
            print(f"[ERROR] Failed to start server: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_address):
        """Handle incoming messages from a client"""
        print(f"[CONNECTED] {client_address[0]}:{client_address[1]} connected")
        
        try:
            while True:
                message = client_socket.recv(4096).decode('utf-8')
                if not message:
                    break
                    
                print(f"[MESSAGE from {client_address[0]}]: {message}")
                
                # Send acknowledgment back
                response = "Message received"
                client_socket.send(response.encode('utf-8'))
                
        except Exception as e:
            print(f"[ERROR] Communication error with {client_address[0]}: {e}")
        finally:
            client_socket.close()
            print(f"[DISCONNECTED] {client_address[0]}:{client_address[1]} disconnected\n")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("\n[SERVER] Shutdown complete")

def main():
    """Main entry point"""
    print("=== Message Receiver (Server) ===\n")
    
    # Allow custom port via command line
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number. Using default port 5000")
    
    receiver = MessageReceiver(port=port)
    
    try:
        receiver.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
        receiver.stop()

if __name__ == "__main__":
    main()
