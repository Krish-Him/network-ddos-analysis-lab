"""
http_flood_simulation.py
------------------------
Simulates an HTTP flood by sending rapid, repeated GET requests to a target
URL.  Intended for **educational Wireshark analysis in a controlled lab**.

WARNING: Only run against servers you own or have explicit written permission
to test.  Sending floods to real-world websites is illegal and unethical.

Requirements
------------
    pip install requests

Usage
-----
    python3 http_flood_simulation.py --url http://192.168.1.100 \
                                      --count 200 --interval 0.05 \
                                      --threads 5
"""

import argparse
import sys
import time
import threading

try:
    import requests
    from requests.exceptions import RequestException
except ImportError:
    print("[ERROR] 'requests' library is not installed. Run:  pip install requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="HTTP GET flood simulator for educational lab use."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Target URL (e.g. http://192.168.1.100 or http://localhost)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Total number of GET requests per thread (default: 100)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.05,
        help="Delay in seconds between requests within a thread (default: 0.05)",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of concurrent threads (default: 1)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Request timeout in seconds (default: 5)",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

# Thread-safe counters
_lock = threading.Lock()
_sent = 0
_errors = 0


def _increment_sent():
    global _sent
    with _lock:
        _sent += 1


def _increment_errors():
    global _errors
    with _lock:
        _errors += 1


def flood_worker(url: str, count: int, interval: float, timeout: int, thread_id: int) -> None:
    """Send *count* GET requests from a single worker thread."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Educational-Lab-Simulation/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }
    session = requests.Session()

    for i in range(count):
        try:
            response = session.get(url, headers=headers, timeout=timeout)
            _increment_sent()
        except RequestException:
            _increment_errors()

        time.sleep(interval)

    session.close()


def http_flood(url: str, count: int, interval: float, threads: int, timeout: int) -> None:
    """Spawn *threads* worker threads each sending *count* GET requests."""
    print(f"[*] Starting HTTP flood simulation")
    print(f"    Target  : {url}")
    print(f"    Requests: {count} per thread × {threads} thread(s) = {count * threads} total")
    print(f"    Interval: {interval}s per request")
    print(f"    Timeout : {timeout}s")
    print(f"    (Press Ctrl+C to stop early)\n")

    worker_threads = []
    start_time = time.time()

    try:
        for t_id in range(threads):
            t = threading.Thread(
                target=flood_worker,
                args=(url, count, interval, timeout, t_id + 1),
                daemon=True,
            )
            worker_threads.append(t)
            t.start()

        for t in worker_threads:
            t.join()

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")

    elapsed = time.time() - start_time
    print(f"\n[+] HTTP flood simulation complete.")
    print(f"    Requests sent   : {_sent}")
    print(f"    Errors          : {_errors}")
    print(f"    Elapsed time    : {elapsed:.2f}s")
    print("[*] Open Wireshark and apply filter:  http.request.method == \"GET\"")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    http_flood(
        url=args.url,
        count=args.count,
        interval=args.interval,
        threads=args.threads,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    main()
