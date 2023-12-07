# from socket import * 
import psutil
import socket
from server.server import *

def get_wifi_ip_address():
    target_interface = "Wi-Fi 2"  # Thay thế bằng tên của giao diện WiFi bạn quan tâm
    interfaces = psutil.net_if_addrs()
    for interface, addresses in interfaces.items():
        if interface == target_interface:
            for address in addresses:
                if address.family == socket.AF_INET:
                    return address.address
    return None
if __name__ == '__main__':
    # host = socket.gethostbyname(socket.gethostname())
    host = get_wifi_ip_address()
    if host is None: host = socket.gethostbyname(socket.gethostname())
    port = "8080"
    server = Server(host, int(port))
    
    server.run()
    