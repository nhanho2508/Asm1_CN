from atexit import register
import socket
from socket import AF_INET, SOCK_DGRAM
from peer.helper import *
from server.server import Server
from threading import *
import time
from object_info import *

class Peer:
    def __init__(self, port, host, server_port, server_host, max_connect = 5):
        self.host = host 
        self.port = port  
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.sock.bind((self.host, self.port))  
        self.sock.listen(max_connect)  
        self.semaphore = Semaphore(max_connect) 
        self.server_host = server_host
        self.server_port = server_port
        self.start_time = time.time()
        self.object_info = ObjectInfo(server_host, server_port)
        self.max_connect = max_connect
        
    def respond_ping(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_address = (self.host, 12000)
        client_socket.bind(client_address)
        client_socket.listen(1)

        print('Client is ready to receive pings.')

        while True:
            data, server_address = client_socket.recvfrom(1024)
            request = pickle.loads(data)
            request_type = request[2]
            print(request_type)
            request_id = request[3]
            print(f'Received ping from {server_address}')
            if request_type == 0xA0:
                client_socket.sendto(create_snmp_response("public", request_id, self.start_time), server_address)
    
    def send_receive(self, request, host, port):
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_socket.bind((self.host, 12000))
        self.sock.connect((host, port))

        self.sock.send(pickle.dumps(request))
        result = pickle.loads(self.sock.recv(BUFFER))
        self.sock.close()
        return result

    def receive_file(self, request, sender_host, sender_port):
        self.sock.connect((sender_host, sender_port))
        self.sock.send(pickle.dumps(request))
        # storage_path = os.path.join(os.getcwd(), 'storage')
        downloads_path = os.path.join(os.getcwd(), 'downloads')
        file_path = os.path.join(downloads_path, request[1])
        with open(file_path, 'wb') as f:
            while True:
                data = self.sock.recv(BUFFER)
                if not data:
                    break
                f.write(data)
            f.close()
        print('DOWNLOAD successfully.')
        self.sock.close()

    

    def listen(self, request, sender_host=None, sender_port=None):
        while True:
            (conn, addr) = self.sock.accept()
            print("[*] Got a connection from ", addr[0], ":", addr[1])
            request = pickle.loads(conn.recv(BUFFER))  # unwrap the request
            if request[0] == SEND:
                send_file(conn, request[1])
            
            

    def run(self):
        while True:
            command_line = input()
            parsed_string = command_line.split()
            if (parsed_string[0] == "register"):
                host_name = parsed_string[1]
                self.semaphore.acquire()
                REGISTERED_SUCCESSFULLY = self.object_info.register(host_name)
                print("Congratulations you have been registered successfully.\n[*] You will now be put to the listening state.\n")
                self.semaphore.release()

            if (parsed_string[0] == "fetch"):
                fname = parsed_string[1]
                self.semaphore.acquire()
                is_found, list_files = self.send_receive([FETCH, fname], self.server_host, self.server_port)
                self.semaphore.release()
                peer_host = None
                if is_found:
                    if len(list_files) == 1:
                        for key in list_files:
                            peer_host = key
                    elif len(list_files) > 1:
                        for key in list_files:
                            print(key)
                        peer_host = input('Which peer do you want to choose: ')
                    peer_port = Server.search_peer_port(peer_host)
                    self.receive_file([SEND, fname], peer_host, peer_port)
                    print("FETCH succesfully.")
                else:
                    print('No file in any client!')
                
            
            

            
