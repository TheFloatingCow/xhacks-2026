# PTP - Peer-to-Peer Message Application

A simple bidirectional message communication application that allows two computers to send and receive messages simultaneously over a network.

## Features

- **Bidirectional Communication**: Both parties can send and receive messages at the same time
- **Server/Client Architecture**: One instance runs as a server, the other as a client
- **Local & Remote**: Works on the same computer (`localhost`) or across different computers on a network
- **Real-time Messaging**: Messages are delivered instantly with threaded receive handling
- **Easy to Use**: Simple command-line interface

## Installation

No external dependencies required. Uses only Python's built-in `socket` and `threading` modules.

**Requirements:**
- Python 3.6+

## Usage

### Server Mode (Listening)

Start the server on the computer that will **receive** the connection:

```bash
python ptp.py server [port]
```

**Default port**: 5000

**Examples:**
```bash
python ptp.py server 5000
python ptp.py server 8080
```

### Client Mode (Connecting)

Connect from the computer that will **initiate** the connection:

```bash
python ptp.py client <host> [port]
```

**Parameters:**
- `<host>` - IP address or hostname of the server computer (required)
- `[port]` - Port number (default: 5000)

**Examples:**
```bash
python ptp.py client localhost 5000
python ptp.py client 127.0.0.1 5000
python ptp.py client 192.168.1.100 5000
```

## Quick Start

### Testing on the Same Computer

**Terminal 1 (Server):**
```bash
python ptp.py server 5000
```

**Terminal 2 (Client):**
```bash
python ptp.py client localhost 5000
```

### Connecting Between Two Computers

**On Computer A (Server):**
```bash
python ptp.py server 5000
```

**On Computer B (Client):**
Get Computer A's IP address first (e.g., `192.168.1.100`), then:
```bash
python ptp.py client 192.168.1.100 5000
```

## How to Find Your Computer's IP Address

### Windows
Open PowerShell and run:
```powershell
ipconfig
```
Look for "IPv4 Address" (typically starts with `192.168.` or `10.`)

### macOS/Linux
Open Terminal and run:
```bash
ifconfig
```
or
```bash
hostname -I
```

## Commands

Once connected, you can:

- **Send a message**: Type your message and press Enter
- **Receive messages**: They appear automatically from the other party
- **Disconnect**: Type `quit` or `exit`

## Example Session

```
=== Unified Message Application ===

[SERVER] Listening on port 5000
[SERVER] Waiting for incoming connection...

[CONNECTED] 127.0.0.1:54321 connected

=== Type your messages (type 'quit' or 'exit' to disconnect) ===

You: Hello!
Remote: Hi there!
You: How are you?
Remote: I'm good, thanks!
You: quit
[USER] Disconnecting...

[DISCONNECTED] Connection closed
```

## Troubleshooting

### Connection Failed
- Ensure the server is running on the correct computer
- Verify the correct IP address is being used
- Check that the port is not blocked by a firewall
- Try using a different port if 5000 is in use

### Messages Not Received
- Ensure both applications are connected
- Check the terminal output for error messages
- Verify network connectivity between the two computers

### Port Already in Use
- Use a different port: `python ptp.py server 8080`
- Or wait a few seconds for the previous connection to fully close

## Limitations

- Only supports one connection at a time
- Messages are plain text (no encryption)
- No message history - messages are not saved
- No authentication - anyone on the network can connect if they know the port

## Future Enhancements

- Support multiple simultaneous connections
- Message encryption
- Message logging/history
- Username/authentication system
- File transfer capabilities
