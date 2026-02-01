"""
Graphical User Interface for Morse Flash Messenger
Uses backend.py for messaging logic and Morse code conversion
"""

import tkinter as tk
from backend import UnifiedMessenger, text_to_morse


class ChatUI:
    """Main UI class for the Morse Flash Messenger application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Morssenger")
        self.root.geometry("450x600")

        self.messenger = UnifiedMessenger(ui_callback=self.log_message)

        # Connection Setup Frame
        config_frame = tk.LabelFrame(root, text="Connection Setup")
        config_frame.pack(padx=10, pady=5, fill="x")

        tk.Label(config_frame, text="Target IP:").grid(row=0, column=0, padx=5)
        self.ip_entry = tk.Entry(config_frame)
        self.ip_entry.insert(0, "192.168.1.X")
        self.ip_entry.grid(row=0, column=1, padx=5)

        tk.Label(config_frame, text="Port:").grid(row=0, column=2, padx=5)
        self.port_entry = tk.Entry(config_frame, width=6)
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=0, column=3, padx=5)

        tk.Label(config_frame, text="Flash Color:").grid(row=1, column=0, padx=5, pady=5)
        self.color_var = tk.StringVar(value="white")
        color_menu = tk.OptionMenu(config_frame, self.color_var, "white", "red", "green", "blue", "yellow", "cyan", "magenta", "orange")
        color_menu.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        tk.Label(config_frame, text="AI Model:").grid(row=2, column=0, padx=5, pady=5)
        self.model_var = tk.StringVar(value="None (Local Dictionary)")
        model_menu = tk.OptionMenu(config_frame, self.model_var, 
            "None (Local Dictionary)",
            "Claude 3 Haiku",
            "Claude 3 Sonnet",
            "Llama 3 8B",
            "Titan Text Express")
        model_menu.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='w')

        # Connection Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        
        self.btn_server = tk.Button(btn_frame, text="Start Server (Listen)", command=self.start_server_mode)
        self.btn_server.pack(side=tk.LEFT, padx=10)

        self.btn_client = tk.Button(btn_frame, text="Connect (Client)", command=self.start_client_mode)
        self.btn_client.pack(side=tk.LEFT, padx=10)

        self.btn_disconnect = tk.Button(btn_frame, text="Disconnect", command=self.disconnect, state='disabled')
        self.btn_disconnect.pack(side=tk.LEFT, padx=10)

        # Chat Display
        self.chat_display = tk.Text(root, state='disabled', height=20, bg="#f0f0f0")
        self.chat_display.pack(padx=10, pady=5, fill="both", expand=True)

        # Message Input Frame
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10, fill="x", padx=10)

        self.msg_entry = tk.Entry(input_frame)
        self.msg_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", self.send_msg)

        self.btn_send = tk.Button(input_frame, text="Send", command=self.send_msg)
        self.btn_send.pack(side=tk.LEFT)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def play_morse_sequence(self, window, sequence, index=0):
        """
        Recursively processes the sequence list to flash the screen.
        sequence item format: ('color', duration_ms)
        """
        if index >= len(sequence):
            # End of sequence: Close the flash window
            window.destroy()
            return

        color, duration = sequence[index]
        
        # Set the window color
        window.configure(bg=color)
        
        # Schedule the next step
        self.root.after(duration, lambda: self.play_morse_sequence(window, sequence, index + 1))

    def trigger_morse_flash(self, morse_text):
        """Parses Morse text into a timeline of flashes and starts the show."""
        
        flash_win = tk.Toplevel(self.root)
        flash_win.attributes("-fullscreen", True)
        flash_win.attributes("-topmost", True)
        flash_win.configure(bg="black")
        flash_win.bind("<Escape>", lambda e: flash_win.destroy())

        # Define Timing (Speed in milliseconds)
        UNIT = 200  # Length of a dot
        
        sequence = []
        
        sequence.append(('black', 1000))

        flash_color = self.color_var.get()

        for char in morse_text:
            if char == '.':
                sequence.append((flash_color, UNIT))        # Light On (Dot)
                sequence.append(('black', UNIT))            # Light Off (Gap)
            elif char == '-':
                sequence.append((flash_color, UNIT * 5))    # Light On (Dash)
                sequence.append(('black', UNIT))            # Light Off (Gap)
            elif char == ' ':
                sequence.append(('black', UNIT * 5))        # Gap between letters (Total 3 units)
            elif char == '/':
                sequence.append(('black', UNIT * 5))        # Gap between words (Total 7 units)

        self.play_morse_sequence(flash_win, sequence)

    def log_message(self, message):
        """Updates chat window and triggers Flash on incoming messages"""
        def _update():
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, message + "\n")
            self.chat_display.see(tk.END)
            self.chat_display.config(state='disabled')
            
            # Trigger morse flash for incoming messages
            if message.startswith("Friend:"):
                raw_morse = message.replace("Friend: ", "").strip()
                self.trigger_morse_flash(raw_morse)

        self.root.after(0, _update)

    def start_server_mode(self):
        """Start in server mode (listening for connections)"""
        port = int(self.port_entry.get())
        self.lock_setup()
        self.messenger.start_server(port)

    def start_client_mode(self):
        """Start in client mode (connecting to a server)"""
        host = self.ip_entry.get()
        port = int(self.port_entry.get())
        self.lock_setup()
        self.messenger.start_client(host, port)

    def lock_setup(self):
        """Disable connection setup controls after connecting"""
        self.btn_server.config(state='disabled')
        self.btn_client.config(state='disabled')
        self.ip_entry.config(state='disabled')
        self.port_entry.config(state='disabled')
        self.btn_disconnect.config(state='normal')

    def unlock_setup(self):
        """Re-enable connection setup controls after disconnecting"""
        self.btn_server.config(state='normal')
        self.btn_client.config(state='normal')
        self.ip_entry.config(state='normal')
        self.port_entry.config(state='normal')
        self.btn_disconnect.config(state='disabled')

    def disconnect(self):
        """Disconnect from current connection"""
        self.messenger.cleanup()
        self.log_message("[DISCONNECTED] Connection closed by user")
        self.unlock_setup()

    def send_msg(self, event=None):
        """Send a message (converts to Morse code)"""
        raw_msg = self.msg_entry.get()
        if raw_msg:
            morse_msg = text_to_morse(raw_msg, self.model_var.get())
            self.messenger.send_message(morse_msg)
            self.log_message(f"You: {raw_msg}\n -> {morse_msg}")
            self.msg_entry.delete(0, tk.END)

    def on_close(self):
        """Clean up on window close"""
        self.messenger.cleanup()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatUI(root)
    root.mainloop()
