from atexit import register
import socket
from socket import AF_INET, SOCK_DGRAM
from peer.helper import *
from threading import *
import time
from object_info import *
class Peer:
    def __init__(self, port, host, server_port, server_host, max_connect = 5):
        self.host = host 
        self.port = port  
        self.sock = socket.socket()  
        self.sock.bind((self.host, self.port))  
        self.sock.listen(max_connect)  
        self.semaphore = Semaphore(max_connect) 
        self.server_host = server_host
        self.server_port = server_port
        self.start_time = time.time()
        self.object_info = ObjectInfo(server_host, server_port)
    def send(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_address = (self.host, 12000)
        client_socket.bind(client_address)

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
        
    def receive(self):
        while True:
            command_line = input()
            parsed_string = command_line.split()
            if (parsed_string[0] == "register"):
                host_name = parsed_string[1]
                self.semaphore.acquire()
                REGISTERED_SUCCESSFULLY = self.object_info.register(host_name)
                create_repo()
                print("Congratulations you have been registered successfully.\n[*] You will now be put to the listening state.\n")
                self.semaphore.release()
            if (parsed_string[0] == "publish"):
                repo_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"repo_test")
                #create_manage_repo(repo_path)
                host_name = parsed_string[1]
                lname_path = parsed_string[2]
                f_name = parsed_string[3]
                make_publish_copy(lname_path,f_name,repo_path)
                self.semaphore.acquire()
                PUBLISH_SUCCESS = self.object_info.publish(host_name, f_name)
                print("success" if(PUBLISH_SUCCESS) else "fail")
                
                self.semaphore.release()
            
            
    def run(self):
        receive_thread = Thread(target=self.receive, args=())
        send_thread = Thread(target=self.send, args=())

        # Start both threads
        receive_thread.start()
        send_thread.start()
        
        

            
