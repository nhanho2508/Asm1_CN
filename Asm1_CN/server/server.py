
from socket import *
from server.controller import *
from threading import *
import pickle
from constants import*
import threading #LAPTOP-VJDK2ECL
import select

class Server:
    def __init__(self, port, host, max_connect=5):
        self.host = host 
        self.port = int(port) 
        self.sock = socket.socket() 
        self.sock.bind((self.host, self.port))   
        self.semaphore = Semaphore(max_connect)  
        self.sock.listen(max_connect) 
        self.setOfHostName = {}
        self.setOfListsOfInfoFile = dict()
        print("Server started listening on host ", self.host, ", port ", self.port)
    def send(self):
        while True:
            command_line = input()
            parsed_string = command_line.split()
            if (parsed_string[0] == "ping"):
                host_name = parsed_string[1]
                self.semaphore.acquire()
                host = self.setOfHostName[host_name]
                ping(host)
                self.semaphore.release()
            if (parsed_string[0] == "discover"):
                host_name = parsed_string[1]
                self.semaphore.acquire()
                print(self.setOfListsOfInfoFile.get(host_name))
                self.semaphore.release()
    def receive(self):
        while True:
            (conn, addr) = self.sock.accept()
            print("[*] Got a connection from ", addr[0], ":", addr[1])
            data = conn.recv(1024)
            request = pickle.loads(data)  
            print("[*] Request after unwrap", request)
            if request[0] == REGISTER:
                hostname = request[1]
                host = request[2]
                self.semaphore.acquire()
                register(conn, self.setOfListsOfInfoFile, self.setOfHostName, hostname, host)
                self.semaphore.release()
            if request[0] == PUBLISH:
                print(100)
                hostname = request[1]
                filename = request[2]
                list_id = request[3]
                self.semaphore.acquire()
                publish(conn, self.setOfListsOfInfoFile, self.setOfHostName, hostname, filename, list_id)
                print("Filename")
                
                self.semaphore.release()
                print(self.setOfListsOfInfoFile)
                print(self.setOfHostName)
                
                
            
    def run(self):
        #(conn, addr) = self.sock.accept()  
        #print("[*] Got a connection from ", addr[0], ":", addr[1])
        receive_thread = threading.Thread(target=self.receive, args=())
        send_thread = threading.Thread(target=self.send, args=())

        # Start both threads
        receive_thread.start()
        send_thread.start()

        #print(self.setOfHostName) #For debug

        

