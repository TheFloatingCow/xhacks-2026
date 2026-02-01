"""
Message Sender/Client Application
Sends messages to another computer running the receiver
"""

import socket
import sys
import time

class MessageSender:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        """Connect to the message receiver"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"[CONNECTED] Connected to {self.host}:{self.port}\n")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to {self.host}:{self.port}")
            print(f"[ERROR] {e}\n")
            return False
    
    def send_message(self, message):
        """Send a message to the receiver"""
        try:
            self.socket.send(message.encode('utf-8'))
            
            # Wait for acknowledgment
            response = self.socket.recv(4096).decode('utf-8')
            print(f"[ACKNOWLEDGMENT] {response}\n")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}\n")
            return False
    
    def disconnect(self):
        """Disconnect from the receiver"""
        if self.socket:
            self.socket.close()
        print("[DISCONNECTED] Connection closed")
    
    def interactive_mode(self):
        """Interactive mode for sending multiple messages"""
        print("=== Interactive Mode ===")
        print("Type 'quit' or 'exit' to disconnect\n")
        
        while True:
            try:
                message = input("Enter message: ").strip()
                
                if message.lower() in ['quit', 'exit']:
                    break
                
                if not message:
                    print("Message cannot be empty\n")
                    continue
                
                if self.send_message(message):
                    print(f"[SENT] {message}")
                else:
                    print("[ERROR] Failed to send message. Disconnecting...")
                    break
                    
            except KeyboardInterrupt:
                print("\n[USER] Interrupted by user")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                break

def main():
    """Main entry point"""
    print("=== Message Sender (Client) ===\n")
    
    # Get receiver's host and port
    host = 'localhost'
    port = 5000
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port number. Using default port 5000")
    
    sender = MessageSender(host=host, port=port)
    
    # Try to connect
    if not sender.connect():
        return
    
    # If a message is provided as argument, send it once
    if len(sys.argv) > 3:
        message = ' '.join(sys.argv[3:])
        print(f"[SENDING] {message}")
        sender.send_message(message)
        sender.disconnect()
    else:
        # Enter interactive mode
        try:
            sender.interactive_mode()
        except KeyboardInterrupt:
            print("\n[USER] Interrupted")
        finally:
            sender.disconnect()

if __name__ == "__main__":
    main()
