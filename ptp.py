"""
Unified Message Application
Allows bidirectional communication - both sending and receiving messages
Can run as a server (listening) or client (connecting)
"""

import socket
import threading
import sys
import time

class UnifiedMessenger:
    def __init__(self, mode='server', host='0.0.0.0', port=5000, remote_host=None, remote_port=5000):
        self.mode = mode  # 'server' or 'client'
        self.host = host
        self.port = port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.socket = None
        self.client_socket = None
        self.running = True
        
    def start_server(self):
        """Start as a server (listening for connections)"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            
            print(f"[SERVER] Listening on port {self.port}")
            print("[SERVER] Waiting for incoming connection...\n")
            
            client_socket, client_address = self.socket.accept()
            self.client_socket = client_socket
            
            print(f"[CONNECTED] {client_address[0]}:{client_address[1]} connected\n")
            
            # Start receive thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Send messages from user input
            self.send_user_messages()
            
        except Exception as e:
            print(f"[ERROR] Server error: {e}")
        finally:
            self.cleanup()
    
    def start_client(self):
        """Start as a client (connecting to a server)"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.remote_host, self.remote_port))
            self.client_socket = self.socket
            
            print(f"[CONNECTED] Connected to {self.remote_host}:{self.remote_port}\n")
            
            # Start receive thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Send messages from user input
            self.send_user_messages()
            
        except Exception as e:
            print(f"[ERROR] Failed to connect to {self.remote_host}:{self.remote_port}")
            print(f"[ERROR] {e}")
        finally:
            self.cleanup()
    
    def send_user_messages(self):
        """Handle sending messages from user input"""
        print("=== Type your messages (type 'quit' or 'exit' to disconnect) ===\n")
        
        try:
            while self.running:
                try:
                    message = input("You: ").strip()
                    
                    if message.lower() in ['quit', 'exit']:
                        print("[USER] Disconnecting...")
                        break
                    
                    if not message:
                        continue
                    
                    if self.client_socket:
                        try:
                            self.client_socket.send(message.encode('utf-8'))
                        except Exception as e:
                            print(f"[ERROR] Failed to send message: {e}")
                            break
                            
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\n[USER] Interrupted")
                    break
                except Exception as e:
                    print(f"[ERROR] Send error: {e}")
                    break
                    
        finally:
            self.running = False
    
    def receive_messages(self):
        """Continuously receive messages from the other end"""
        try:
            while self.running:
                if self.client_socket:
                    try:
                        message = self.client_socket.recv(4096).decode('utf-8')
                        
                        if not message:
                            print("\n[DISCONNECTED] Remote host closed connection")
                            self.running = False
                            break
                        
                        print(f"\nRemote: {message}")
                        print("You: ", end='', flush=True)
                    except Exception as e:
                        print(f"\n[ERROR] Receive error: {e}")
                        self.running = False
                        break
                    
        except Exception as e:
            if self.running:
                print(f"\n[ERROR] Receive thread error: {e}")
            self.running = False
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("\n[DISCONNECTED] Connection closed")

def main():
    """Main entry point"""
    print("=== Unified Message Application ===\n")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Server mode:  python unified_app.py server [port]")
        print("  Client mode:  python unified_app.py client <host> [port]\n")
        print("Examples:")
        print("  python unified_app.py server 5000")
        print("  python unified_app.py client 192.168.1.100 5000")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == 'server':
        port = 5000
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print("Invalid port number. Using default port 5000")
        
        messenger = UnifiedMessenger(mode='server', port=port)
        messenger.start_server()
        
    elif mode == 'client':
        if len(sys.argv) < 3:
            print("Client mode requires a host address")
            print("Usage: python unified_app.py client <host> [port]")
            return
        
        remote_host = sys.argv[2]
        remote_port = 5000
        
        if len(sys.argv) > 3:
            try:
                remote_port = int(sys.argv[3])
            except ValueError:
                print("Invalid port number. Using default port 5000")
        
        messenger = UnifiedMessenger(mode='client', remote_host=remote_host, remote_port=remote_port)
        messenger.start_client()
        
    else:
        print(f"Unknown mode: {mode}")
        print("Use 'server' or 'client'")

if __name__ == "__main__":
    main()
