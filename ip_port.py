import ipaddress
import subprocess
import argparse
import socket
import concurrent.futures

def ping(ip, timeout=1):
    """
    Ping an IP address to check if it is online.
    
    Args:
        ip (str): The IP address to ping.
        timeout (int): The timeout for the ping command.
    
    Returns:
        bool: True if the host is online, False otherwise.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), ip],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        return False

def scan_network(cidr):
    """
    Scan a network to find live hosts.
    
    Args:
        cidr (str): The CIDR notation for the network to scan.
    
    Returns:
        list: A list of IP addresses of live hosts.
    """
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        live_hosts = []
        print(f"Scanning network: {cidr}")
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = {executor.submit(ping, str(ip)): str(ip) for ip in network.hosts()}
            for future in concurrent.futures.as_completed(results):
                ip = results[future]
                if future.result():
                    print(f"Host {ip} is online")
                    live_hosts.append(ip)
                else:
                    print(f"Host {ip} is offline")
        
        print(f"\nTotal Online Hosts: {len(live_hosts)}")
        return live_hosts
    except ValueError as e:
        print(f"Invalid CIDR notation: {e}")
        return []

def scan_ports(ip, ports, timeout=1):
    """
    Scan a host for open ports.
    
    Args:
        ip (str): The IP address of the host to scan.
        ports (list): A list of ports to scan.
        timeout (int): The timeout for each port scan.
    
    Returns:
        list: A list of open ports.
    """
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                if sock.connect_ex((ip, port)) == 0:
                    open_ports.append(port)
        except Exception as e:
            print(f"Error scanning {ip}:{port} - {e}")
    return open_ports

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network Scanner with Port Scanning")
    parser.add_argument("cidr", help="CIDR notation for network scan (Ex, 192.168.1.0/24)")
    parser.add_argument("-p", nargs='*', type=int, help="Scan open ports on live hosts (Ex, -p 22 80 443)")
    
    args = parser.parse_args()
    live_hosts = scan_network(args.cidr)
    
    if args.p:
        print("\nScanning for open ports")
        for ip in live_hosts:
            open_ports = scan_ports(ip, args.p)
            if open_ports:
                print(f"{ip} has open ports: {', '.join(map(str, open_ports))}")
