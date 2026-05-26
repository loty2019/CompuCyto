import argparse
import socket
import time

from zeroconf import ServiceInfo, Zeroconf


def parse_args():
    parser = argparse.ArgumentParser(description="Advertise CytoCore over mDNS.")
    parser.add_argument("--hostname", default="cytocore.local.")
    parser.add_argument("--service-name", default="CytoCore._http._tcp.local.")
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--address", action="append", default=[])
    return parser.parse_args()


def to_bytes(addresses):
    packed = []
    for address in addresses:
        try:
            packed.append(socket.inet_aton(address))
        except OSError:
            print(f"Skipping invalid IPv4 address: {address}", flush=True)
    return packed


def main():
    args = parse_args()
    addresses = to_bytes(args.address)

    if not addresses:
        raise SystemExit("No usable IPv4 addresses were provided for mDNS.")

    info = ServiceInfo(
        "_http._tcp.local.",
        args.service_name,
        addresses=addresses,
        port=args.port,
        properties={"path": "/"},
        server=args.hostname,
    )

    zeroconf = Zeroconf()
    try:
        zeroconf.register_service(info, allow_name_change=True)
        print(
            f"Advertising {args.hostname} on {', '.join(args.address)}:{args.port}",
            flush=True,
        )
        while True:
            time.sleep(60)
    finally:
        zeroconf.unregister_service(info)
        zeroconf.close()


if __name__ == "__main__":
    main()
