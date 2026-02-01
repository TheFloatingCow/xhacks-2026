# xhacks-2026
XHacks project 2026

## Message Sender/Receiver App

A simple Python application that allows sending and receiving messages between computers over a network using sockets.

### Project Structure

- **receiver/app.py** - Receiver/Server that listens for incoming messages
- **sender/app.py** - Sender/Client that sends messages to a receiver

### Features

- **Multi-threaded server** - Handles multiple clients simultaneously
- **Interactive mode** - Send multiple messages in an interactive session
- **Command-line mode** - Send a single message and exit
- **Network communication** - Uses TCP sockets for reliable message delivery
- **Cross-platform** - Works on Windows, macOS, and Linux

### Setup

Ensure you have Python 3.7+ installed, then the application is ready to use (uses only standard library).

### Usage

#### Starting the Receiver (Server)

In the `receiver/` directory:

```bash
python app.py [port]
```

**Examples:**
```bash
python app.py                 # Listens on port 5000 (default)
python app.py 8080           # Listens on port 8080
```

The server will display:
```
=== Message Receiver (Server) ===

[SERVER] Listening on 0.0.0.0:5000
[SERVER] Waiting for incoming messages...
```

#### Starting the Sender (Client)

In the `sender/` directory:

**Option 1: Interactive Mode**
```bash
python app.py [host] [port]
```

**Examples:**
```bash
python app.py                           # Connect to localhost:5000
python app.py 192.168.1.100            # Connect to specific IP on port 5000
python app.py 192.168.1.100 8080       # Connect to specific IP and port
```

Then type messages and press Enter to send them. Type `quit` or `exit` to disconnect.

**Option 2: Single Message Mode**
```bash
python app.py [host] [port] [message]
```

**Examples:**
```bash
python app.py localhost 5000 "Hello from sender!"
python app.py 192.168.1.100 8080 "This is a test message"
```

### Example Workflow

**Terminal 1 - Start the Receiver:**
```bash
cd receiver
python app.py
```

**Terminal 2 - Send Messages:**
```bash
cd sender
python app.py
# Type: Hello!
# Type: How are you?
# Type: quit
```

### Network Setup

To send messages between different computers:

1. Find the receiver's IP address:
   - Windows: `ipconfig`
   - macOS/Linux: `ifconfig` or `ip addr`

2. On receiver machine: `python app.py`

3. On sender machine: `python app.py [receiver_ip_address] 5000`

### Default Settings

- **Default Host:** localhost
- **Default Port:** 5000
- **Buffer Size:** 4096 bytes per message

### Troubleshooting

- **Connection refused**: Ensure the receiver is running and the port number matches
- **Connection timeout**: Check firewall settings or use localhost for local testing
- **Message not received**: Ensure both machines are on the same network
