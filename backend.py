"""
Backend logic for Morse code messaging
Handles message conversion, AWS Bedrock integration, and socket communication
"""

import socket
import threading
import os
import configparser
import boto3

# Morse code dictionary (fallback if Bedrock fails)
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..',
    "'": '.----.', '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
    '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.',
    '-': '-....-', '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.',
    ' ': '/'
}

# Load AWS credentials from project file
def load_aws_credentials():
    """Load AWS credentials from aws_credentials.ini in project directory"""
    try:
        config = configparser.ConfigParser()
        creds_path = os.path.join(os.path.dirname(__file__), 'aws_credentials.ini')
        config.read(creds_path)
        
        return {
            'aws_access_key_id': config['default']['aws_access_key_id'],
            'aws_secret_access_key': config['default']['aws_secret_access_key'],
            'region_name': config['default'].get('region', 'us-east-1')
        }
    except Exception as e:
        print(f"[WARNING] Could not load credentials from aws_credentials.ini: {e}")
        return {'region_name': 'us-east-1'}

# Initialize Bedrock client with credentials
creds = load_aws_credentials()
bedrock_client = boto3.client('bedrock-runtime', **creds)

def text_to_morse(text):
    """Convert text to Morse code using Amazon Bedrock or fallback dictionary"""
    # List of models to try (comment out to disable Bedrock and avoid billing)
    model_ids = [
        #'anthropic.claude-3-haiku-20240307-v1:0',
        #'anthropic.claude-3-sonnet-20240229-v1:0',
        #'meta.llama3-8b-instruct-v1:0',
        #'amazon.titan-text-express-v1'
    ]
    
    for model_id in model_ids:
        try:
            # Call model through Bedrock
            message = bedrock_client.converse(
                modelId=model_id,
                messages=[
                    {
                        'role': 'user',
                        'content': [
                            {
                                'text': f'Convert this text to Morse code. Only return the Morse code, nothing else: "{text}"'
                            }
                        ]
                    }
                ]
            )
                
            morse_code = message['output']['message']['content'][0]['text'].strip()
            print(f"[BEDROCK] Successfully using {model_id}")
            return morse_code
                
        except Exception as e:
            continue
    
    # Bedrock failed or disabled, use fallback dictionary
    print(f"[INFO] Bedrock unavailable. Using local dictionary.")
    morse_code = []
    for char in text.upper():
        if char in MORSE_CODE_DICT:
            morse_code.append(MORSE_CODE_DICT[char])
        else:
            morse_code.append('?')
    return ' '.join(morse_code)


class UnifiedMessenger:
    """Handles socket communication for sending/receiving messages"""
    
    def __init__(self, ui_callback=None):
        self.socket = None
        self.client_socket = None
        self.running = True
        self.ui_callback = ui_callback if ui_callback else print
        self.mode = None

    def start_server(self, port=5000):
        """Start as a server (listening for connections)"""
        try:
            self.mode = 'server'
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', port))
            self.socket.listen(1)
            self.ui_callback(f"[SERVER] Listening on port {port}...")
            threading.Thread(target=self._accept_connection, daemon=True).start()
        except Exception as e:
            self.ui_callback(f"[ERROR] Server error: {e}")
            self.cleanup()

    def _accept_connection(self):
        """Internal method to accept incoming connection"""
        try:
            client_socket, client_address = self.socket.accept()
            self.client_socket = client_socket
            self.ui_callback(f"[CONNECTED] {client_address[0]} connected")
            self.start_receive_thread()
        except Exception as e:
            if self.running:
                self.ui_callback(f"[ERROR] Accept error: {e}")

    def start_client(self, remote_host, remote_port=5000):
        """Start as a client (connecting to a server)"""
        try:
            self.mode = 'client'
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((remote_host, remote_port))
            self.client_socket = self.socket
            self.ui_callback(f"[CONNECTED] Connected to {remote_host}:{remote_port}")
            self.start_receive_thread()
        except Exception as e:
            self.ui_callback(f"[ERROR] Connection failed: {e}")
            self.cleanup()

    def start_receive_thread(self):
        """Start thread to continuously receive messages"""
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, message):
        """Send a message through the socket"""
        if not self.client_socket:
            self.ui_callback("[ERROR] Not connected.")
            return
        try:
            self.client_socket.send(message.encode('utf-8'))
        except Exception as e:
            self.ui_callback(f"[ERROR] Failed to send: {e}")
            self.cleanup()

    def receive_messages(self):
        """Continuously receive messages from the other end"""
        try:
            while self.running:
                if self.client_socket:
                    try:
                        message = self.client_socket.recv(4096).decode('utf-8')
                        if not message:
                            self.ui_callback("[DISCONNECTED] Remote closed connection")
                            self.cleanup()
                            break
                        self.ui_callback(f"Friend: {message}")
                    except OSError:
                        break
                    except Exception as e:
                        self.ui_callback(f"[ERROR] Receive error: {e}")
                        break
        except Exception as e:
            if self.running:
                self.ui_callback(f"[ERROR] Thread error: {e}")

    def cleanup(self):
        """Clean up socket resources"""
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
        self.client_socket = None
        self.socket = None
