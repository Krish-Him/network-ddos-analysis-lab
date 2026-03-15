# Network DDoS Analysis Lab

A **beginner-friendly cybersecurity lab project** that simulates DDoS-like
traffic patterns in a controlled environment so you can study them with
Wireshark.  Designed for university networking and cybersecurity assignments.

> **⚠️ Legal & Ethical Disclaimer**  
> These scripts are strictly for **educational use in an isolated lab
> environment**.  Run them only against machines you own (e.g., a local VM,
> loopback interface, or a dedicated lab subnet).  Sending flood traffic to
> systems you do not own is **illegal** and **unethical**.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Objective](#2-objective)
3. [Repository Structure](#3-repository-structure)
4. [Setup Instructions](#4-setup-instructions)
5. [How to Run the Scripts](#5-how-to-run-the-scripts)
   - 5.1 [SYN Flood Simulation](#51-syn-flood-simulation)
   - 5.2 [HTTP Flood Simulation](#52-http-flood-simulation)
6. [Capturing Traffic with Wireshark](#6-capturing-traffic-with-wireshark)
7. [Wireshark Filters for Analysis](#7-wireshark-filters-for-analysis)
8. [Observations & Conclusion](#8-observations--conclusion)
9. [Dependencies](#9-dependencies)

---

## 1. Project Overview

Distributed Denial-of-Service (DDoS) attacks overwhelm a target server by
flooding it with more traffic than it can handle.  Two of the most common
low-level patterns are:

| Attack type  | Mechanism |
|---|---|
| **SYN Flood** | Sends a high volume of TCP SYN packets with spoofed source IPs, exhausting the server's half-open connection table. |
| **HTTP Flood** | Sends a rapid stream of legitimate-looking HTTP GET requests, exhausting application-layer resources (threads, DB connections, etc.). |

This lab generates both patterns in a safe, local environment and shows you
how to detect and analyse them in Wireshark.

---

## 2. Objective

- Understand how SYN flood and HTTP flood traffic looks "on the wire".
- Practice applying Wireshark display filters and statistics tools.
- Relate captured evidence to real-world DDoS mitigation strategies.
- Document findings in a structured cybersecurity report.

---

## 3. Repository Structure

```
network-ddos-analysis-lab/
│
├── code/
│   ├── syn_flood_simulation.py    # TCP SYN flood generator (Scapy)
│   └── http_flood_simulation.py   # HTTP GET flood generator (requests)
│
├── wireshark-captures/            # Store .pcapng capture files here
│   └── README.md
│
├── screenshots/                   # Store Wireshark screenshots here
│   └── README.md
│
├── report/                        # Store the PDF analysis report here
│   └── README.md
│
├── requirements.txt               # Python dependencies
├── .gitignore                     # Python project ignore rules
└── README.md                      # This file
```

---

## 4. Setup Instructions

### Prerequisites

| Tool | Purpose | Download |
|---|---|---|
| Python 3.8+ | Run the simulation scripts | https://python.org |
| Scapy 2.5+ | Craft raw TCP packets | `pip install scapy` |
| requests 2.28+ | Send HTTP requests | `pip install requests` |
| Wireshark 4.x | Capture & analyse traffic | https://wireshark.org |
| npcap (Windows) / libpcap (Linux/macOS) | Packet capture driver | Bundled with Wireshark installer |

### Step-by-step setup

```bash
# 1. Clone the repository
git clone https://github.com/Krish-Him/network-ddos-analysis-lab.git
cd network-ddos-analysis-lab

# 2. (Recommended) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # macOS / Linux
# .\venv\Scripts\Activate.ps1    # Windows PowerShell

# 3. Install Python dependencies
pip install -r requirements.txt
```

### Lab topology (recommended)

```
┌─────────────────────┐          ┌──────────────────────┐
│  Attacker VM        │──────────│  Victim VM / Service │
│  (run the scripts)  │  Host-only│  (e.g. Apache/nginx) │
│  192.168.56.101     │  Network │  192.168.56.100       │
└─────────────────────┘          └──────────────────────┘
         ↑
  Wireshark captures on
  the attacker's interface
```

You can also use the loopback address (`127.0.0.1`) if you only have one
machine and run a simple HTTP server with `python3 -m http.server 8080`.

---

## 5. How to Run the Scripts

### 5.1 SYN Flood Simulation

> Requires **root / administrator** privileges because it crafts raw IP
> packets.

```bash
# Basic usage – 500 SYN packets to 192.168.56.100 on port 80
sudo python3 code/syn_flood_simulation.py \
    --target 192.168.56.100 \
    --port   80 \
    --count  500 \
    --interval 0.01

# Against localhost (safe, no root required on most systems with loopback)
sudo python3 code/syn_flood_simulation.py \
    --target 127.0.0.1 --port 8080 --count 200
```

**Options**

| Flag | Default | Description |
|---|---|---|
| `--target` | *(required)* | Destination IP address |
| `--port` | `80` | Destination TCP port |
| `--count` | `100` | Number of SYN packets to send |
| `--interval` | `0.01` | Seconds between packets |

### 5.2 HTTP Flood Simulation

```bash
# Start a local HTTP server to receive traffic (in a separate terminal)
python3 -m http.server 8080

# Run the HTTP flood (another terminal)
python3 code/http_flood_simulation.py \
    --url      http://127.0.0.1:8080 \
    --count    200 \
    --interval 0.02 \
    --threads  3
```

**Options**

| Flag | Default | Description |
|---|---|---|
| `--url` | *(required)* | Target URL |
| `--count` | `100` | Requests per thread |
| `--interval` | `0.05` | Seconds between requests in each thread |
| `--threads` | `1` | Number of concurrent worker threads |
| `--timeout` | `5` | HTTP request timeout (seconds) |

---

## 6. Capturing Traffic with Wireshark

1. Open Wireshark and select the correct network interface (e.g., `eth0`,
   `Ethernet`, or `Loopback: lo`).
2. Start a capture **before** running the simulation script.
3. Run the simulation.
4. Stop the capture once the script finishes.
5. Save the capture: **File → Save As** → choose `wireshark-captures/` folder,
   save as `.pcapng`.

---

## 7. Wireshark Filters for Analysis

### SYN Flood Filters

```wireshark
# Show only SYN packets (no ACK) – the flood traffic itself
tcp.flags.syn == 1 && tcp.flags.ack == 0

# Show SYN packets to a specific destination port
tcp.flags.syn == 1 && tcp.flags.ack == 0 && tcp.dstport == 80

# Highlight multiple source IPs (spoofing indicator)
tcp.flags.syn == 1 && tcp.flags.ack == 0 && ip.dst == 192.168.56.100

# Compare SYN vs SYN-ACK ratio (high SYN with few SYN-ACKs = flood)
tcp.flags.syn == 1
tcp.flags.syn == 1 && tcp.flags.ack == 1
```

### HTTP Flood Filters

```wireshark
# Show all HTTP GET requests
http.request.method == "GET"

# Show HTTP requests to a specific host
http.host == "192.168.56.100"

# Show HTTP traffic on a non-standard port
tcp.port == 8080 && http

# Show response codes (look for 200 OK vs 503 Service Unavailable)
http.response.code == 200
http.response.code == 503
```

### General Traffic Analysis

```wireshark
# Filter by source IP
ip.src == 192.168.56.101

# Filter by destination IP
ip.dst == 192.168.56.100

# Show TCP connections and resets
tcp.flags.reset == 1

# Statistics → I/O Graphs → set Y-axis to "Packets/s" for rate view
```

---

## 8. Observations & Conclusion

### Expected Observations

#### SYN Flood
- **High packet rate**: Hundreds of SYN packets per second visible in the I/O graph.
- **Diverse source IPs**: Each packet appears to come from a different (spoofed) source IP.
- **No corresponding ACK**: SYN packets are not completed into full three-way handshakes.
- **Server-side**: The victim's `netstat` or `ss` output shows many `SYN_RECV` connections.

#### HTTP Flood
- **Repeated identical GET requests**: The same path is requested many times from the same source IP.
- **Rapid succession**: Requests arrive with very short inter-arrival times (< 100 ms).
- **Legitimate-looking**: Packets look like normal HTTP traffic, making them harder to block at the network layer alone.
- **Potential 503 responses**: Under heavy load the server may start returning Service Unavailable.

### Mitigation Strategies

| Attack | Mitigation |
|---|---|
| SYN Flood | SYN cookies, rate-limiting inbound SYNs, firewall rules |
| HTTP Flood | Rate-limiting per IP, CAPTCHA, WAF rules, CDN protection |

### Conclusion

This lab demonstrated how both network-layer (SYN flood) and application-layer
(HTTP flood) DDoS patterns can be generated and studied safely in a local
environment.  Wireshark's display filters and statistics tools provide clear
visual evidence of the abnormal traffic patterns that defenders look for in
real incidents.  Understanding how these attacks work is a critical first step
in designing effective defences.

---

## 9. Dependencies

| Package | Version | Purpose |
|---|---|---|
| [scapy](https://scapy.net/) | ≥ 2.5.0 | Raw packet crafting (SYN flood) |
| [requests](https://requests.readthedocs.io/) | ≥ 2.28.0 | HTTP requests (HTTP flood) |

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

*Project created for educational purposes as part of a university cybersecurity
networking assignment.*