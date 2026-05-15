# Secure Mobile AI Assistant Gateway Using Client-Server Networking

**Course:** CSCI-4345 Computer Networks  
**Project Type:** Custom computer networks implementation  
**Student:** Josue Raudy  
**Date:** May 14, 2026

---

## 1. Explanation of the Project

For my final course project, I built a **Secure Mobile AI Assistant Gateway**. The goal of the project was to create a small networked system where a mobile client, specifically my iPhone, could access an AI assistant service running through a server on my MacBook. The MacBook acted as the local network server, while the iPhone acted as the remote client on the same Wi-Fi network.

The project demonstrates several computer networking concepts from the course, including client-server architecture, IP addressing, TCP ports, HTTP communication, and packet analysis using Wireshark. The AI part of the project is the application running on top of the network. The main focus of the project is the network communication path that allows a separate device to reach a local service over the LAN.

In the final version, the iPhone connects to the MacBook server using the MacBook's private LAN IP address and TCP port `8080`. The MacBook runs a Python FastAPI server that exposes a browser-based chat page and a `/ask` API endpoint. When the iPhone sends a message, the MacBook receives the request over HTTP, forwards the prompt to Anthropic's Claude API over HTTPS, receives the AI response, and sends the result back to the iPhone as JSON.

### Motivation

I chose this project because I have been interested in the idea of being able to access an AI assistant or agent from anywhere. A real-world version of this system could be used as a private AI gateway for a home network, small office, or school lab. Instead of every device needing to directly connect to an AI provider, a central gateway server can manage requests, authentication, logging, and API access.

This kind of system is useful because it shows how modern applications are often built as network services. Phones, laptops, and other clients do not need to run all the logic themselves. They can send requests to a server, and the server can process the request, call other services, and return a response. This is similar to how many real applications work, such as web apps, cloud APIs, chatbots, and remote management tools.

The project also helped me better understand what is happening underneath a simple browser request. From the user's perspective, it looks like pressing a button on a webpage. From a networking perspective, the client creates a TCP connection, sends an HTTP request to a specific IP address and port, receives an HTTP response, and then closes or reuses the connection.

---

## 2. Breakdown of the Implementation

### Network Topology

The project used a physical local network setup instead of virtual machines. The devices were connected to the same Wi-Fi network.

The main devices were:

1. **MacBook Pro** — acted as the local AI gateway server.
2. **iPhone** — acted as the mobile client.
3. **Wi-Fi router/access point** — connected the iPhone and MacBook on the same LAN.
4. **Anthropic API** — external AI backend reached by the MacBook over the internet.

The MacBook's LAN IP address was:

```text
192.168.0.193
```

The iPhone's LAN IP address was:

```text
192.168.0.153
```

The FastAPI server listened on TCP port:

```text
8080
```

The iPhone accessed the gateway using:

```text
http://192.168.0.193:8080/chat
```

### Network Diagram

```text
+----------------------+        Wi-Fi LAN / HTTP over TCP        +--------------------------+
|                      |                                         |                          |
| iPhone Client        |  http://192.168.0.193:8080/chat         | MacBook Pro Server       |
| IP: 192.168.0.153    | ------------------------------------->  | IP: 192.168.0.193        |
| Safari Browser       |        Destination TCP Port: 8080       | FastAPI Gateway          |
|                      | <-------------------------------------  | Port: 8080               |
+----------------------+        HTTP/JSON Response               +------------+-------------+
                                                                           |
                                                                           |
                                                                           | HTTPS over TCP 443
                                                                           v
                                                            +-----------------------------+
                                                            | Anthropic Claude API        |
                                                            | External AI Backend         |
                                                            +-----------------------------+
```

**[Insert Figure 1 here: MacBook LAN IP screenshot — `Screenshot 2026-05-14 at 9.11.03 PM.png`. Caption: The MacBook server's Wi-Fi IP address was verified using `ipconfig getifaddr en0`, showing `192.168.0.193`.]**

**[Insert Figure 2 here: iPhone Wi-Fi settings screenshot. Caption: The iPhone client's Wi-Fi settings show its IPv4 address as `192.168.0.153`.]**

### Configuration Details

The server was written in Python using FastAPI. FastAPI was used to create HTTP endpoints that the browser and command-line clients could access. Uvicorn was used as the ASGI server to run the FastAPI application.

The server was started with the following command:

```bash
python -m uvicorn server.app:app --host 0.0.0.0 --port 8080
```

The `--host 0.0.0.0` option was important because it allowed the server to listen on all network interfaces, including the MacBook's Wi-Fi interface. If the server only listened on `127.0.0.1`, then only the MacBook itself would be able to access it. By using `0.0.0.0`, the iPhone could connect to the MacBook using the MacBook's LAN IP address.

The project used the following main endpoints:

| Endpoint | Method | Purpose |
|---|---:|---|
| `/` | GET | Basic status page for the API |
| `/health` | GET | Health check endpoint |
| `/chat` | GET | Browser-based mobile chat interface |
| `/ask` | POST | API endpoint that receives a message and returns an AI response |
| `/history` | GET | Shows recent request metadata |

The local gateway used a simple bearer token for access control. The token was included in the browser request as an HTTP `Authorization` header:

```text
Authorization: Bearer class-demo-token
```

The Anthropic API key was stored in a local `.env` file and excluded from GitHub using `.gitignore`. This prevented the API key from being hardcoded in the source code.

The AI model configured for the project was:

```text
claude-haiku-4-5
```

### Tools and Technologies

The project used the following tools and technologies:

- **Python 3** — programming language used for the server and client scripts.
- **FastAPI** — Python framework used to build the HTTP API server.
- **Uvicorn** — server used to run the FastAPI application.
- **Anthropic Python SDK** — used to send prompts from the gateway to Claude.
- **iPhone Safari** — used as the mobile client.
- **Wireshark** — used to capture and inspect network traffic.
- **macOS Terminal** — used to run the server and check IP addresses.
- **GitHub** — intended for storing the source code and README.

### Communication Flow

The communication flow for the project was:

1. The FastAPI server starts on the MacBook and listens on `0.0.0.0:8080`.
2. The MacBook's Wi-Fi IP address is identified as `192.168.0.193`.
3. The iPhone connects to the same Wi-Fi network and receives IP address `192.168.0.153`.
4. The iPhone opens Safari and visits `http://192.168.0.193:8080/chat`.
5. The MacBook server receives a `GET /chat` request and returns the chat webpage.
6. The user enters a prompt on the iPhone and taps **Send to AI Gateway**.
7. The iPhone sends an HTTP `POST /ask` request to the MacBook on TCP port `8080`.
8. The FastAPI server checks the bearer token.
9. The MacBook sends the prompt to Anthropic's Claude API over HTTPS using TCP port `443`.
10. Anthropic returns the AI-generated response to the MacBook.
11. The MacBook returns a JSON response to the iPhone.
12. The iPhone displays the response in the browser.

The server response included network metadata, such as the detected client IP address and the path of the request:

```json
{
  "client_ip": "192.168.0.153",
  "network_path": "client -> HTTP/TCP port 8080 -> FastAPI gateway -> HTTPS/TCP 443 -> Anthropic API"
}
```

---

## 3. Demonstration

### Local Mac Test

Before testing from the iPhone, I first tested the gateway locally on the MacBook using the loopback address:

```text
http://127.0.0.1:8080/chat
```

The local test confirmed that the FastAPI server was working and that the Anthropic integration returned a response. In this test, the response showed the client IP as `127.0.0.1`, which means the request came from the same machine.

**[Insert Figure 3 here: Local Mac browser response screenshot — `Screenshot 2026-05-14 at 9.08.55 PM.png`. Caption: Local browser test using `127.0.0.1`, showing a successful AI response and `client_ip` of `127.0.0.1`.]**

### iPhone Mobile Client Test

After the local test worked, I tested the project from my iPhone. The iPhone was connected to the same Wi-Fi network as the MacBook. In Safari, I opened:

```text
http://192.168.0.193:8080/chat
```

The iPhone successfully loaded the chat interface from the MacBook server. Then I sent a prompt from the iPhone to the gateway. The response appeared on the iPhone, proving that the mobile client could communicate with the server over the local network.

**[Insert Figure 4 here: iPhone page loaded screenshot — `IMG_5205.PNG`. Caption: The iPhone accessed the MacBook gateway at `192.168.0.193`, showing the mobile chat interface.]**

**[Insert Figure 5 here: iPhone successful response screenshot — `IMG_5206.PNG`. Caption: The iPhone received a JSON response from the AI gateway. The response metadata shows `client_ip` as `192.168.0.153`.]**

### Server Log Evidence

The server logs confirmed that the iPhone reached the MacBook server. The logs showed requests from `192.168.0.153`, which was the iPhone's IP address.

Example server log lines:

```text
192.168.0.153 - "GET /chat HTTP/1.1" 200 OK
192.168.0.153 - "POST /ask HTTP/1.1" 200 OK
```

This confirmed that the request was not just coming from the MacBook itself. It was coming from a separate client device on the LAN.

**[Insert Figure 6 here: Server logs screenshot — `Screenshot 2026-05-14 at 9.10.20 PM.png`. Caption: Uvicorn server logs showing successful `GET /chat` and `POST /ask` requests from the iPhone IP address `192.168.0.153`.]**

### Wireshark Packet Capture

To verify the actual network traffic, I captured packets in Wireshark on the MacBook's Wi-Fi interface. I used the display filter:

```text
tcp.port == 8080
```

The capture showed traffic between the iPhone and MacBook:

```text
Source:      192.168.0.153
Destination: 192.168.0.193
Port:        8080
```

The Wireshark capture showed the TCP connection setup and HTTP request/response. In particular, it showed:

- A TCP `SYN` packet from the iPhone to the MacBook.
- A TCP `SYN, ACK` packet from the MacBook back to the iPhone.
- A TCP `ACK` packet completing the connection setup.
- An HTTP/JSON `POST /ask HTTP/1.1` request.
- An HTTP `200 OK` response from the server.

This demonstrates both transport-layer and application-layer communication. TCP handled the reliable connection, and HTTP carried the application data.

**[Insert Figure 7 here: Wireshark screenshot — `Screenshot 2026-05-14 at 9.15.37 PM.png`. Caption: Wireshark capture filtered by `tcp.port == 8080`, showing TCP and HTTP/JSON traffic between iPhone `192.168.0.153` and MacBook `192.168.0.193`.]**

### Sample Data Transfer

The project transferred user prompt data from the iPhone to the MacBook server. One sample prompt sent from the iPhone was:

```text
Why is UTRGV in Edinburg Texas a good option?
```

The server forwarded the prompt to Claude through the Anthropic API and returned the generated answer to the iPhone as JSON. The response also included the network metadata showing the client IP address, timestamp, and network path.

This sample data transfer shows that the project was not just serving a static webpage. It was accepting data from a network client, processing the data, forwarding it to an external API, and returning the result back to the original client.

---

## 4. Challenges and Debugging

One issue I ran into during the project was an invalid Anthropic model name. The local network server was working, but the request to the Anthropic API failed with a `404` error because the configured model ID was not available. This helped separate the problem into two parts: the local networking path and the external AI backend path.

The server logs showed that the browser successfully reached the FastAPI server, so the issue was not the local HTTP connection. The error came from the Anthropic API call. After updating the model configuration to a currently supported model ID, the request succeeded.

Another useful networking detail was the difference between `127.0.0.1` and the MacBook's LAN IP address. The loopback address `127.0.0.1` only works from the MacBook itself. To allow the iPhone to connect, the server had to bind to `0.0.0.0`, and the iPhone had to connect to the MacBook's LAN IP address `192.168.0.193`.

---

## 5. GitHub Repository

The project code can be stored in a GitHub repository with the following files:

```text
remote-ai-network-gateway/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── client/
│   └── ask.py
├── server/
│   ├── app.py
│   └── anthropic_client.py
└── report/
    └── final-report.md
```

The `.env` file containing the Anthropic API key is intentionally excluded from GitHub.

**GitHub Repository Link:**  
https://github.com/joshh61/remote-ai-network-gateway

---

## 6. Conclusion

This project implemented a working mobile-accessible AI gateway using computer networking concepts. The iPhone successfully acted as a client and connected to the MacBook server over Wi-Fi using the MacBook's LAN IP address and TCP port `8080`. The MacBook server accepted HTTP requests, forwarded prompts to Anthropic over HTTPS, and returned JSON responses to the iPhone.

The project demonstrated client-server architecture, IP addressing, TCP ports, HTTP requests, API gateway behavior, and packet inspection with Wireshark. The Wireshark capture confirmed that the iPhone and MacBook exchanged TCP and HTTP/JSON traffic over port `8080`. Overall, the project showed how a network service can expose AI functionality to a mobile device while still keeping the networking concepts visible and testable.

---

## 7. Citations

Anthropic. (2026). *Claude API documentation*. https://docs.anthropic.com/

FastAPI. (2026). *FastAPI documentation*. https://fastapi.tiangolo.com/

Python Software Foundation. (2026). *Python 3 documentation*. https://docs.python.org/3/

Uvicorn. (2026). *Uvicorn documentation*. https://www.uvicorn.org/

Wireshark Foundation. (2026). *Wireshark user documentation*. https://www.wireshark.org/docs/
