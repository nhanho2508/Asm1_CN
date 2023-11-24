from socket import *
from server.controller import *
from threading import *
import pickle
from constants import *

class Server:
    def __init__(self, port, host, max_connect=5):
        self.host = host 
        self.port = int(port) 
        self.sock = socket.socket() 
        self.sock.bind((self.host, self.port))   
        self.semaphore = Semaphore(max_connect)  
        self.sock.listen(max_connect) 
        self.setOfHostName = {}
        self.setOfInfoFileLists = {} 
        print("Server started listening on host ", self.host, ", port ", self.port)

    def request(self):
        while True:
            command_line = input()
            parsed_string = command_line.split()
            if (parsed_string[0] == "ping"):
                host_name = parsed_string[1]
                self.semaphore.acquire()
                ping(host_name)
                self.semaphore.release()    

    @staticmethod
    def search_peer_port(self, peer_host):
        pass

    def run(self):
        while True:
            (conn, addr) = self.sock.accept()  
            print("[*] Got a connection from ", addr[0], ":", addr[1])
            data = conn.recv(1024)  
            request = pickle.loads(data)
            print("[*] Request after unwrap", request)

            if request[0] == REGISTER:
                hostname = request[1]
                self.semaphore.acquire()
                register(conn, self.setOfInfoFileLists, self.setOfHostName, hostname)
                self.semaphore.release()

            elif request[0] == FETCH:
                self.semaphore.acquire()
                found_boolean, file_object = search(request[1], self.setOfInfoFileLists)
                conn.send(pickle.dumps([found_boolean, file_object]))
                self.semaphore.release()
            #print(self.setOfHostName) #For debug
        