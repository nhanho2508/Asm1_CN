import socket
import server.controller as controller
import threading
import pickle
import time
from constants import *
import json

class Server:
    setOfHostInfo = {}              # {username: [ip,port,password]}
    setOfHostFileLists = {}         # {username: [**files]}

    def init_db(self):
        with open("hostInfo.json", "r") as f0:
            Server.setOfHostInfo = json.load(f0)
        f0.close()
        with open("hostFileLists.json", "r") as f1:
            Server.setOfHostFileLists = json.load(f1)
        f1.close()

    def __init__(self, host='localhost', port=SERVER_PORT, max_connect=5):
        self.host = host
        #--- DEBUG ONLY ---#
        self.port = int(input('Enter port: '))
        #------------------# 
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        # self.sock.bind((self.host, self.port))
        self.lst_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lst_sock.bind((self.host, self.port + 1))
        self.semaphore = threading.Semaphore(max_connect)
        self.has_connect = False
        self.max_connect = max_connect 
        self.lst_sock.listen(self.max_connect)
        self.init_db()
        print("[*] Server address:", self.host, ", port", self.port)
        print("[*] Server started listening on host:", self.host, ", port", self.port+1)

    
    def updateHostInfo(self):
        with open("hostInfo.json", "w") as f:
            json.dump(Server.setOfHostInfo,f)
        f.close()

    def updateHostFileLists(self):
        with open("hostFileLists.json", "w") as f:
            json.dump(Server.setOfHostFileLists,f)
        f.close()

    #--- REQUEST HANDLING HELPER ---#

    def send_receive(self, message, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.connect((host,port))
        sock.send(pickle.dumps(message))            # send some data
        
        result = pickle.loads(sock.recv(BUFFER))    # receive the response
        sock.close()
        return result

    #--- COMMAND HANDLING ---#

    def send_command(self):
        while True:
            command_line = input('>> ')
            parsed_string = command_line.split()
            if (parsed_string[0] == "ping"):
                host_name = parsed_string[1]
                self.semaphore.acquire()
                ping_status = self.ping(host_name)
                #print("Ping response:")
                #TODO: handle ping_status
                self.semaphore.release()

            elif (parsed_string[0] == "discover"):
                username = parsed_string[1]
                self.semaphore.acquire()
                result = Server.setOfHostFileLists.get(username)
                print(f"User {username}'s files: ",result)
                self.semaphore.release()

            elif (parsed_string[0] == "host_info"):
                self.semaphore.acquire()
                print(Server.setOfHostInfo)
                self.semaphore.release()

    def accept_connect(self):
        while True:
            try:
                (conn, addr) = self.lst_sock.accept()  
                print("[*] Got a connection from ", addr[0], ":", addr[1])
                self.has_connect = True
                listen_thread = threading.Thread(target=self.listen, args=(conn, addr))
                listen_thread.start()
            except socket.error as e:
                print("Error accepting connection:", e)
    def listen(self,conn,addr):
        while True:
            data = conn.recv(BUFFER)  
            request = pickle.loads(data)
            print("[*] Request after unwrap: ", request)

            if request[0] == REGISTER:
                username = request[1]
                password = request[2]
                self.semaphore.acquire()
                controller.register(conn, Server.setOfHostFileLists, Server.setOfHostInfo, username, password, addr[0], addr[1])
                # conn.send(pickle.dumps(register_status))
                self.updateHostInfo()
                self.semaphore.release()

            elif request[0] == LOGIN:
                username = request[1]
                password = request[2]
                self.semaphore.acquire()
                controller.login(conn, Server.setOfHostInfo, username, password)
                # conn.send(pickle.dumps(login_status))
                self.semaphore.release()

            elif request[0] == FETCH:
                fname = request[1]
                self.semaphore.acquire()
                # found_boolean, file_object = controller.search(request[1], Server.setOfHostFileLists)
                controller.fetch(conn, fname, Server.setOfHostFileLists, Server.setOfHostInfo)
                # conn.send(pickle.dumps([found_boolean, file_object]))
                self.updateHostFileLists()
                self.semaphore.release()
            
            elif request[0] == PUBLISH:
                username = request[1]
                filename = request[2]
                self.semaphore.acquire()
                controller.publish(conn, Server.setOfHostFileLists, username, filename)
                # conn.send(pickle.dumps(publish_status))
                # print("Filename")
                self.updateHostFileLists()
                self.semaphore.release()
            
            elif request[0] == GET_INFO:
                username = request[1]
                self.semaphore.acquire()
                controller.get_info(conn, Server.setOfHostInfo, username)
                self.semaphore.release()


    def run(self):
        accept_thread = threading.Thread(target=self.accept_connect, args=())
        send_thread = threading.Thread(target=self.send_command, args=())

        # Start both threads
        accept_thread.start()
        send_thread.start()
        accept_thread.join()
        send_thread.join()
    #--- LIST OF COMMAND FUNCTION ---#
    
    def ping(self, username):
        # assert self.list_id is None
        host = Server.setOfHostInfo.get(username)[0]
        port = Server.setOfHostInfo.get(username)[1] + 1
        #ping_request = controller.create_snmp_request()
        #count_byte = len(ping_request)
        #print(count_byte, "byte")
        #result = self.send_receive([PING], host, port)
        receive = 0;
        RTT_sum = 0;
        for i in range (5):  
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #sock.bind((self.host, self.port))
            sock.settimeout(5)
            try:
                sock.connect((host, port))
                time_start = time.time()
                sock.send(pickle.dumps([PING]))
                result = pickle.loads(sock.recv(BUFFER))
                time_end = time.time()  # receive the response
                print(f"Ping Successful. RTT = {time_end - time_start:.5f}")
                receive = receive + 1
                RTT_sum = RTT_sum + time_end - time_start
                sock.close()
            except (socket.timeout, WindowsError):
                print("Request time out")
                sock.close()
                   
        print(f"Ping statistic: Send = 5, Receive = {receive}, Lost = {5 - receive}")
        # print(f"RTT average {(RTT_sum/receive):.5f}")
           