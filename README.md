# Secure Mobile AI Assistant Gateway

Computer Networks final project.

## Project summary

This project implements a mobile-accessible AI assistant gateway. A MacBook runs a Python FastAPI server on TCP port 8080. A client, such as an iPhone browser or Python CLI client, sends an HTTP request to the gateway. The gateway forwards the prompt to Anthropic's API over HTTPS and returns the answer.

The main networking concepts demonstrated are:

- Client-server architecture
- HTTP as an application-layer protocol
- TCP ports
- LAN IP addressing
- Mobile device to local server communication
- API gateway behavior
- Basic bearer-token authentication
- Wireshark packet capture and traffic analysis

## Network topology

```text
+---------------------+      HTTP over TCP :8080       +----------------------------+
| iPhone / CLI Client | -----------------------------> | MacBook FastAPI Gateway    |
| Browser or Python   |                                | 0.0.0.0:8080               |
+---------------------+                                +-------------+--------------+
                                                                      |
                                                                      | HTTPS over TCP :443
                                                                      v
                                                       +----------------------------+
                                                       | Anthropic Claude API       |
                                                       +----------------------------+
```

## Setup

```bash
cd "/Users/jraudy/Files/Spring 2026 /Computer Networks/remote-ai-network-gateway"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and paste your Anthropic API key:

```text
ANTHROPIC_API_KEY=your_real_key_here
AI_GATEWAY_TOKEN=class-demo-token
```

## Run the server

```bash
source .venv/bin/activate
uvicorn server.app:app --host 0.0.0.0 --port 8080
```

Open on the Mac:

```text
http://127.0.0.1:8080/chat
```

Open on an iPhone on the same Wi-Fi:

```text
http://<MAC_LAN_IP>:8080/chat
```

Find the Mac LAN IP with:

```bash
ipconfig getifaddr en0
```

## CLI demo

```bash
python client/ask.py --message "Explain NAT in simple terms."
```

## API demo with curl

```bash
curl -X POST http://127.0.0.1:8080/ask \
  -H "Authorization: Bearer class-demo-token" \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain TCP in two sentences."}'
```

## Wireshark demo notes

Capture on the Wi-Fi interface while the iPhone sends a request to the Mac. Useful display filters:

```text
tcp.port == 8080
http
ip.addr == <IPHONE_IP> || ip.addr == <MAC_IP>
```

The local iPhone-to-Mac leg is HTTP over TCP port 8080. The Mac-to-Anthropic leg uses HTTPS over TCP port 443.
