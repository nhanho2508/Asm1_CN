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
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        hostInfoPath = os.path.join(self.db_path,"hostInfo.json")
        hostFileListsPath = os.path.join(self.db_path,"hostFileLists.json")
        
        if not os.path.exists(hostInfoPath):
            with open(hostInfoPath, "w") as f0:
                json.dump({},f0)
            f0.close()
        if not os.path.exists(hostFileListsPath):
            with open(hostFileListsPath, "w") as f1:
                json.dump({},f1)
            f1.close()

        with open(hostInfoPath, "r") as f0:
            Server.setOfHostInfo = json.load(f0)
        f0.close()
        with open(hostFileListsPath, "r") as f1:
            Server.setOfHostFileLists = json.load(f1)
        f1.close()

    def __init__(self, host='localhost', port=SERVER_PORT, is_GUI = False,max_connect=5):
        self.host = host
        #--- DEBUG ONLY ---#
        if not is_GUI:
            self.port = int(input('Enter port: '))
        else: 
            self.port = port
        #------------------# 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.sock.bind((self.host, self.port))
        self.lst_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lst_sock.bind((self.host, self.port + 1))
        self.semaphore = threading.Semaphore(max_connect)
        # self.has_connect = False
        self.max_connect = max_connect 
        self.lst_sock.listen(self.max_connect)
        self.db_path = os.path.join(DATABASE_PATH, str(self.port))
        self.init_db()
        print("[*] Server address:", self.host, ", port", self.port)
        print("[*] Server started listening on host:", self.host, ", port", self.port+1)
        ##############HELPER ATTRIBUTE FOR GUI##################
        self.is_GUI = is_GUI
        self.info = f"[*] Server address: {self.host}, port {self.port}\n [*] Server started listening on host: {self.host} , port {self.port+1}"
        self.error = ""
        self.command_line = ""
        self.info_renew = False
        self.error_renew = False

    
    def updateHostInfo(self):
        hostInfoPath = os.path.join(self.db_path,"hostInfo.json")
        with open(hostInfoPath, "w") as f:
            json.dump(Server.setOfHostInfo,f)
        f.close()

    def updateHostFileLists(self):
        hostFileListsPath = os.path.join(self.db_path,"hostFileLists.json")
        with open(hostFileListsPath, "w") as f:
            json.dump(Server.setOfHostFileLists,f)
        f.close()

    #--- REQUEST HANDLING HELPER ---#

    def send_receive(self, message, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.bind((self.host, self.port))
        sock.connect((host,port))
        sock.send(pickle.dumps(message))            # send some data
        
        result = pickle.loads(sock.recv(BUFFER))    # receive the response
        sock.close()
        return result

    #--- COMMAND HANDLING ---#

    def send_command(self):
        while True:
            try:
                if(not self.is_GUI):
                    command_line = input('>> ')
                else: 
                    command_line = self.command_line
                if command_line == "":
                    continue
                parsed_string = command_line.split()
                self.command_line=""
                if (parsed_string[0] == "ping"):
                    username = parsed_string[1]
                    if len(parsed_string) > 2:
                        ping_times = int(parsed_string[2])
                    else:
                        ping_times = 1
                    receive = 0
                    is_online = Server.setOfHostInfo.get(username)[3]
                    if is_online == 0:
                        print("[*] The client isn't online.")
                        self.error = "[*] The client isn't online."
                        self.error_renew = True
                        continue
                    for i in range(ping_times):
                        self.semaphore.acquire()
                        start_time = time.time()
                        ping_status = self.ping(username)
                        end_time = time.time()
                        self.semaphore.release()
                        if ping_status is None or not ping_status[1]:
                            print("[*] PING failed!")
                            self.error = "[*] PING failed!"
                            self.error_renew = True
                        else:
                            print(f"[*] PING successfully. ({end_time - start_time:.6f} s)")
                            self.info = f"[*] PING successfully. ({end_time - start_time:.6f} s)"
                            self.info_renew = True
                            if self.is_GUI: time.sleep (0.1)
                            receive += 1
                    if self.is_GUI: time.sleep (0.1)
                    print(f"[*] Ping statistics: Send = {ping_times}, Receive = {receive}, Lost = {ping_times - receive}")
                    self.info = f"[*] Ping statistics: Send = {ping_times}, Receive = {receive}, Lost = {ping_times - receive}"
                    self.info_renew = True
                    

                elif (parsed_string[0] == "discover"):
                    username = parsed_string[1]
                    self.semaphore.acquire()
                    result = Server.setOfHostFileLists.get(username)
                    print(f"[*] User {username}'s files: ",result)
                    self.info = f"[*] User {username}'s files: {result}"
                    self.info_renew = True
                    self.semaphore.release()

                elif (parsed_string[0] == "show"):
                    self.semaphore.acquire()
                    print(Server.setOfHostInfo)
                    self.info = f"{Server.setOfHostInfo}"
                    self.info_renew = True
                    self.semaphore.release()
                else:
                    print("Error: Invalid command!")
                    self.error = "Error: Invalid command!"
                    self.error_renew = True
            except Exception as e:
                # print(e)
                print("[*] Error: REQUEST failed!")
                self.error = "[*] Error: REQUEST failed!"
                self.error_renew = True

    def accept_connect(self):
        while True:
            try:
                (conn, addr) = self.lst_sock.accept()  
                print("[*] Got a connection from ", addr[0], ":", addr[1])
                self.info=f"[*] Got a connection from {addr[0]}: {addr[1]}"
                self.info_renew=True
                self.has_connect = True
                listen_thread = threading.Thread(target=self.listen, args=(conn, addr))
                listen_thread.start()
            except socket.error as e:
                print("Error accepting connection:", e)
                self.error=f"Error accepting connection: {e}"
                self.error_renew= True
    def listen(self,conn,addr):
        while True:
            try:
                data = conn.recv(BUFFER)
                if not data:
                    break
                request = pickle.loads(data)
                print("[*] Request after unwrap: ", request)
                self.info = f"[*] Request after unwrap: {request}"
                self.info_renew = True

                if request[0] == REGISTER:
                    username = request[1]
                    password = request[2]
                    self.semaphore.acquire()
                    controller.register(conn, Server.setOfHostFileLists, Server.setOfHostInfo, username, password, addr[0], addr[1])
                    # conn.send(pickle.dumps(register_status))
                    self.updateHostInfo()
                    self.updateHostFileLists()
                    self.semaphore.release()

                elif request[0] == LOGIN:
                    username = request[1]
                    password = request[2]
                    self.semaphore.acquire()
                    controller.login(conn, Server.setOfHostInfo, username, password, addr[1])
                    self.updateHostInfo()
                    # conn.send(pickle.dumps(login_status))
                    self.semaphore.release()

                elif request[0] == LOGOUT:
                    username = request[1]
                    self.semaphore.acquire()
                    controller.logout(conn, Server.setOfHostInfo, username)
                    self.updateHostInfo()
                    self.semaphore.release()

                elif request[0] == CHANGEPWD:
                    username = request[1]
                    old_password = request[2]
                    new_password = request[3]
                    self.semaphore.acquire()
                    controller.change_password(conn, Server.setOfHostInfo, username, old_password, new_password)
                    self.updateHostInfo()
                    self.semaphore.release()

                elif request[0] == SEARCH:
                    fname = request[1]
                    username = request[2]
                    self.semaphore.acquire()
                    # found_boolean, file_object = controller.search(request[1], Server.setOfHostFileLists)
                    controller.search(conn, fname, username, Server.setOfHostFileLists, Server.setOfHostInfo)
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
                
                elif request[0] == DELETE:
                    username = request[1]
                    filename = request[2]
                    self.semaphore.acquire()
                    controller.delete(conn, Server.setOfHostFileLists, username, filename)
                    # conn.send(pickle.dumps(publish_status))
                    # print("Filename")
                    self.updateHostFileLists()
                    self.semaphore.release()
                
                # elif request[0] == GET_INFO:
                #     username = request[1]
                #     self.semaphore.acquire()
                #     controller.get_info(conn, Server.setOfHostInfo, username)
                #     self.semaphore.release()
            
            except ConnectionResetError:
                conn.close()
                for key in Server.setOfHostInfo:
                    if Server.setOfHostInfo.get(key)[0] == addr[0] and Server.setOfHostInfo.get(key)[1] == addr[1]:
                        Server.setOfHostInfo.get(key)[3] = 0
                        self.updateHostInfo()
                        break
                print(f'[*] Client at address {addr[0]}:{addr[1]} was forcibly closed without valid disconnection!')
                self.error = f'[*] Client at address {addr[0]}:{addr[1]} was forcibly closed without valid disconnection!'
                self.error_renew = True
                break


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
        try:
            host = Server.setOfHostInfo.get(username)[0]
            port = Server.setOfHostInfo.get(username)[1] + 1
            result = self.send_receive([PING], host, port)
            return result
        except Exception as e:
            return None
        # assert self.list_id is None
        # host = Server.setOfHostInfo.get(username)[0]
        # port = Server.setOfHostInfo.get(username)[1] + 1
        # #ping_request = controller.create_snmp_request()
        # #count_byte = len(ping_request)
        # #print(count_byte, "byte")
        # #result = self.send_receive([PING], host, port)
        # receive = 0;
        # RTT_sum = 0;
        # for i in range (5):  
        #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     #sock.bind((self.host, self.port))
        #     sock.settimeout(5)
        #     try:
        #         sock.connect((host, port))
        #         time_start = time.time()
        #         sock.send(pickle.dumps([PING]))
        #         result = pickle.loads(sock.recv(BUFFER))
        #         time_end = time.time()  # receive the response
        #         print(f"Ping Successful. RTT = {time_end - time_start:.5f}")
        #         self.info=f"Ping Successful. RTT = {time_end - time_start:.5f}"
        #         self.info_renew = True
        #         receive = receive + 1
        #         RTT_sum = RTT_sum + time_end - time_start
        #         sock.close()
        #     except (socket.timeout, WindowsError):
        #         print("Request time out")
        #         self.info="Request time out"
        #         self.info_renew = True
        #         sock.close()
        #     if self.is_GUI: time.sleep(0.5)
        # print(f"Ping statistic: Send = 5, Receive = {receive}, Lost = {5 - receive}")
        # self.info = f"Ping statistic: Send = 5, Receive = {receive}, Lost = {5 - receive}"
        # self.info_renew=True
        # if self.is_GUI: time.sleep(0.5)
        # if receive!=0:
        #     print(f"RTT average {(RTT_sum/receive):.5f}")
        #     self.info = f"RTT average {(RTT_sum/receive):.5f}"
        #     self.info_renew=True

           