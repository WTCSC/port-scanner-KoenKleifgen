import ipaddress
import subprocess

def ping(ip):
    try:
        result = subprocess.run([
            "ping", "-c", "1", "-i", "0.1", ip
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        return False

def scan_network(cidr):
    """Scan all valid hosts in the given CIDR network."""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        live_hosts = []
        offline_hosts = 0
        print(f"Scanning network: {cidr}")
        
        for ip in network.hosts():
            if ping(str(ip)):
                print(f"Host {ip} is online")
                live_hosts.append(str(ip))
            else:
                print(f"Host {ip} is offline")
                offline_hosts += 1
        
        print(f"\nTotal Online Hosts: {len(live_hosts)}")
        print(f"Total Offline Hosts: {offline_hosts}")
        return live_hosts
    except ValueError as e:
        print(f"Invalid CIDR notation: {e}")
        return []

if __name__ == "__main__":
    cidr_input = input("Enter CIDR notation (EX... 192.168.1.0/24): ")
    online_hosts = scan_network(cidr_input)
    print("\nLive hosts:")
    print("\n".join(online_hosts) if online_hosts else "None found")

    # print("4 live hosts")
    # print("250 offline hosts")
