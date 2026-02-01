import socket
import threading
import tkinter as tk
from tkinter import messagebox

class UnifiedMessenger:
    def __init__(self, ui_callback):
        self.socket = None
        self.client_socket = None
        self.running = True
        self.ui_callback = ui_callback  # Function to update the UI
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
        """Internal helper to wait for connection in background"""
        try:
            client_socket, client_address = self.socket.accept()
            self.client_socket = client_socket
            self.ui_callback(f"[CONNECTED] {client_address[0]} connected")
            
            # Start receive thread
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
            
            # Start receive thread
            self.start_receive_thread()
            
        except Exception as e:
            self.ui_callback(f"[ERROR] Connection failed: {e}")
            self.cleanup()

    def start_receive_thread(self):
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

    def send_message(self, message):
        """Sends a single message"""
        if not self.client_socket:
            self.ui_callback("[ERROR] Not connected.")
            return

        try:
            self.client_socket.send(message.encode('utf-8'))
        except Exception as e:
            self.ui_callback(f"[ERROR] Failed to send: {e}")
            self.cleanup()

    def receive_messages(self):
        """Continuously receive messages"""
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
        """Clean up resources"""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except: pass
        if self.socket:
            try:
                self.socket.close()
            except: pass
        self.client_socket = None
        self.socket = None

class ChatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Unified Message App")
        self.root.geometry("450x550")

        self.root.bind("<Escape>", self.exit_fullscreen)
        self.messenger = UnifiedMessenger(ui_callback=self.log_message)
        config_frame = tk.LabelFrame(root, text="Connection Setup")
        config_frame.pack(padx=10, pady=5, fill="x")

        # IP Entry
        tk.Label(config_frame, text="Target IP:").grid(row=0, column=0, padx=5)
        self.ip_entry = tk.Entry(config_frame)
        self.ip_entry.insert(0, "192.168.1.X") # Placeholder
        self.ip_entry.grid(row=0, column=1, padx=5)

        # Port Entry
        tk.Label(config_frame, text="Port:").grid(row=0, column=2, padx=5)
        self.port_entry = tk.Entry(config_frame, width=6)
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=0, column=3, padx=5)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        
        self.btn_server = tk.Button(btn_frame, text="Start Server (Listen)", command=self.start_server_mode)
        self.btn_server.pack(side=tk.LEFT, padx=10)

        self.btn_client = tk.Button(btn_frame, text="Connect (Client)", command=self.start_client_mode)
        self.btn_client.pack(side=tk.LEFT, padx=10)

        self.chat_display = tk.Text(root, state='disabled', height=15, bg="#f0f0f0")
        self.chat_display.pack(padx=10, pady=5, fill="both", expand=True)

        input_frame = tk.Frame(root)
        input_frame.pack(pady=10, fill="x", padx=10)

        self.msg_entry = tk.Entry(input_frame)
        self.msg_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", self.send_msg)

        self.btn_send = tk.Button(input_frame, text="Send", command=self.send_msg)
        self.btn_send.pack(side=tk.LEFT)

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log_message(self, message):
        """Updates chat window and triggers Fullscreen on incoming messages"""
        def _update():
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, message + "\n")
            self.chat_display.see(tk.END) # Auto-scroll
            self.chat_display.config(state='disabled')
            
            if message.startswith("Friend:"):
                self.root.deiconify() # Un-minimize
                self.root.lift()      # Bring to front
                self.root.focus_force() 
                self.root.attributes("-fullscreen", True) # Maximize

        self.root.after(0, _update)

    def exit_fullscreen(self, event=None):
        """Allows user to press ESC to leave full screen"""
        self.root.attributes("-fullscreen", False)

    def start_server_mode(self):
        port = int(self.port_entry.get())
        self.lock_setup()
        self.messenger.start_server(port)

    def start_client_mode(self):
        host = self.ip_entry.get()
        port = int(self.port_entry.get())
        self.lock_setup()
        self.messenger.start_client(host, port)

    def lock_setup(self):
        self.btn_server.config(state='disabled')
        self.btn_client.config(state='disabled')
        self.ip_entry.config(state='disabled')
        self.port_entry.config(state='disabled')

    def send_msg(self, event=None):
        msg = self.msg_entry.get()
        if msg:
            self.messenger.send_message(msg)
            self.log_message(f"You: {msg}")
            self.msg_entry.delete(0, tk.END)

    def on_close(self):
        self.messenger.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatUI(root)
    root.mainloop()