# from atexit import register
import socket
# import os
from constants import *
import peer.helper as helper
from server.server import Server
import threading
import pickle
import time
import shlex

class Peer:
    def __init__(self, host='localhost', port=PEER_PORT, server_host=0, server_port=SERVER_PORT, max_connect = 5):
        self.username = ''
        self.host = host
        #--- DEBUG ONLY ---#
        if(port!=8081):
            self.port = port
        else:
            self.port = int(input('Enter port: '))
        #------------------#
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.sock.bind((self.host, self.port))
        # self.sock.listen(max_connect)
        self.semaphore = threading.Semaphore(max_connect)
        self.server_host = server_host
        self.server_port = server_port
        self.start_time = time.time()
        self.is_online = False
        self.max_connect = max_connect
        ###########HELPING ATTRIBUTE FOR GUI############
        self.error_message = ""
        self.success_message = f"[*] Client is ready on host address {self.host}, port {self.port}"
        self.command_line = ""
        self.is_multi_peer= False
        self.is_GUI = False
        print("[*] Client is ready on host address ", self.host, ", port", self.port)
        self.sender_username = ""
        self.list_peer = None
        self.wait = True

    
    #--- REQUEST HANDLING HELPER ---#

    # def respond_ping(self):
    #     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_address = (self.host, 12000)
    #     client_socket.bind(client_address)
    #     client_socket.listen(1)

    #     print('[*] Client is ready to receive pings.')

    #     while True:
    #         data, server_address = client_socket.recv(1024)
    #         request = pickle.loads(data)
    #         request_type = request[2]
    #         print(request_type)
    #         request_id = request[3]
    #         print(f'[*] Received ping from {server_address}')
    #         if request_type == 0xA0:
    #             client_socket.sendto(helper.create_snmp_response("public", request_id, self.start_time), server_address)
    ###############################################################################
    def set_GUI (self):
        self.is_GUI=True
    def get_info (self):
        return self.success_message
    def get_error(self):
        return self.error_message
    def reset_info (self):
        self.success_message = ""
    def reset_error (self):
        self.error_message = ""
    def set_command (self, command_line):
        self.command_line = command_line
    def get_multi_peer(self):
        return self.is_multi_peer
    def get_list_peer (self):
        return self.list_peer
    ###############################################################################

    def send_receive(self, message, host, port):
        # print(host, port)
        result = None
        if host == self.server_host and port == self.server_port:
            # print('Sock:',self.sock)
            # print('Message:',message)
            self.sock.send(pickle.dumps(message))            # send some data
            result = pickle.loads(self.sock.recv(BUFFER))    # receive the response
        else:
            new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_sock.bind((self.host,self.port))
            new_sock.connect((host,port))
            new_sock.send(pickle.dumps(message))                # send some data
            result = pickle.loads(new_sock.recv(BUFFER))        # receive the response
            new_sock.close()
        return result
  
    #--- FETCH HELPER ---#

    def download_file(self, host_info, fname):
        try:
            # result = self.send_receive([GET_INFO, username], self.server_host, self.server_port)
            sender_host = host_info[0]
            sender_port = host_info[1] + 1

            new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_sock.connect((sender_host, sender_port))
            new_sock.send(pickle.dumps([SEND,fname]))
            print("[**] Downloading file...")
            self.success_message = "[**] Downloading file..."
            file_path = os.path.join(REPO_PATH, fname)
            with open(file_path, 'wb') as f:
                while True:
                    data = new_sock.recv(BUFFER)
                    if not data:
                        break
                    f.write(data)
                f.close()
            # print('[*] DOWNLOAD successfully.')
            new_sock.close()
            return True
        except Exception as e:
            return False

    #--- COMMAND HANDLING ---#
    def handle_listen(self, conn, addr):
        request = pickle.loads(conn.recv(BUFFER))  # unwrap the request
        if request[0] == SEND:
                fname = request[1]
                self.semaphore.acquire()
                helper.send_file(conn, fname)
                self.semaphore.release()
        if request[0] == PING:
                helper.respond_ping(conn, addr)
    def listen(self):
        self.lst_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lst_sock.bind((self.host, self.port + 1))
        self.lst_sock.listen(self.max_connect)
        while True:
            (conn, addr) = self.lst_sock.accept()
            # print("[*] Got a connection from ", addr[0], ":", addr[1])
            thread = threading.Thread(target=self.handle_listen, args = (conn, addr))
            thread.start()
            # thread.join()
        

    def send_command(self):
        while True:
			if(self.is_GUI): 
                time.sleep(0.5)
                self.wait = True
            if self.command_line =="": 
                if( not self.is_GUI):
                    self.command_line = input('>> ')
                else:
                    continue
            parsed_string = shlex.split(self.command_line)
            self.command_line = ""            # parsed_string = command_line.split()
            if (parsed_string[0] == "connect"):
                server_ip = parsed_string[1]
                self.server_host = server_ip
                #--- DEBUG ONLY ---#
                server_port = int(parsed_string[2])
                self.server_port = server_port
                #------------------#
                self.sock.connect((server_ip, server_port))
                print("[*] Client address:", self.host, ":", self.port)
                print("[*] Client connected with server at:", server_ip, ":", server_port)
                self.success_message = f"[*] Client address: {self.host}:{self.port}\n[*] Client connected with server at: {self.server_host}:{self.server_port}"
                self.wait=False
            elif (parsed_string[0] == "register"):
                username = parsed_string[1]
                password = parsed_string[2]
                self.semaphore.acquire()
                register_status = self.register(username, password)
                if register_status[1] and register_status[2] == 1:
                    self.is_online = 1
                    self.username = username
                    self.password = password
                    print("[*] REGISTER successfully.")
                    self.success_message = "[*] REGISTER successfully."
                elif register_status[1] and register_status[2] == 0:
                    print("[*] The username already exists.")
                    self.error_message = "[*] The username already exists."
                else:
                    print("[*] Error: REGISTER failed!")
                    self.error_message = "[*] Error: REGISTER failed!"

                # print("[*] Congratulations you have been registered successfully.\n[*] You will now be put to the listening state.")
                self.semaphore.release()
                self.wait = False

            elif (parsed_string[0] == "login"):
                username = parsed_string[1]
                password = parsed_string[2]
                self.semaphore.acquire()
                login_status = self.login(username, password)
                if login_status[1] and login_status[2] == 1:
                    self.is_online = 1
                    self.username = username
                    self.password = password
                    print("[*] LOGIN successfully.")
                    self.success_message="[*] LOGIN successfully."
                elif login_status[1] and login_status[2] == 0:
                    print("[*] Invalid password.")
                    self.error_message= "[*] Invalid password."
                elif login_status[1] and login_status[2] == -1:
                    print("[*] The username doesn't exist.")
                    self.error_message= "[*] The username doesn't exist."
                else:
                    print("[*] Error: LOGIN failed!")
                    self.error_message ="[*] LOGIN failed!"
                self.semaphore.release()
                self.wait = False

            elif (parsed_string[0] == "fetch"):
                fname = parsed_string[1]
                self.semaphore.acquire()
                fetch_status = self.fetch(fname)
                self.semaphore.release()
                sender_username = None
                if fetch_status[1] and fetch_status[2]:
                    list_peers = fetch_status[3]
                    if len(list_peers) == 1:
                        self.is_multi_peer = False
                        for key in list_peers:
                            sender_username = key
                    elif len(list_peers) > 1:
                        if(not self.is_GUI):
                            print('[**] List of peers:')
                            for key in list_peers:
                                print(key)
                            sender_username = input('Which peer do you want to choose the file from: ')
                        else:
                            self.success_message = "Please enter the peer you want to choose the file from"
                            self.list_peer = list_peers
                            self.is_multi_peer = True
                            self.wait = False
                            while self.sender_username == "":
                                time.sleep(0.5)
                                self.wait = True
                            sender_username = self.sender_username
                            self.sender_username = ""
                    download_status = self.download_file(list_peers[sender_username], fname)
                    update_status = self.send_receive([PUBLISH, self.username, fname], self.server_host, self.server_port)
                    if download_status and update_status[1]:
                        print("[*] DOWNLOAD succesfully.")
                        self.success_message = "[*] DOWNLOAD succesfully."
                    else:
                        print("[*] Error: DOWNLOAD failed!")
                        self.error_message = "[*] Error: DOWNLOAD failed!"
                elif fetch_status[1] and not fetch_status[2]:
                    print('[*] No such file in any client!')
                    self.error_message = '[*] No such file in any client!'
                else:
                    print('[*] Error: FETCH failed!')
                    self.error_message = '[*] Error: FETCH failed!'
                self.wait = False

            elif (parsed_string[0] == "publish"):
                # repo_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"repo_test")
                # create_manage_repo(repo_path)
                lname_path = parsed_string[1]
                f_name = parsed_string[2]
                self.semaphore.acquire()
                publish_status = self.publish(lname_path, f_name)
                # print("success" if(publish_successfully) else "fail")
                if publish_status is None or publish_status is False:
                    print("[*] Error: PUBLISH failed! You already publish this file name, please choose another name if you want publish it.")
                elif publish_status[1]:
                    print("[*] PUBLISH successfully.")
                    self.success_message = "[*] PUBLISH successfully."
                    self.wait = False
                else:
                    print("[*] Error: PUBLISH failed!")
                    self.error_message = "[*] Error: PUBLISH failed!"
                    self.wait = False
                self.semaphore.release()
                self.wait = False

    def run(self):
        listen_thread = threading.Thread(target=self.listen, args=())
        send_thread = threading.Thread(target=self.send_command, args=())

        # Start both threads
        listen_thread.start()
        send_thread.start()
        listen_thread.join()
        send_thread.join()    
    #--- LIST OF COMMAND FUNCTION ---#
    
    def register(self, username, password):
        # assert self.list_id is None 
        result = self.send_receive([REGISTER, username, password], self.server_host, self.server_port)
        return result

    def login(self, username, password):
        # assert self.list_id is None 
        result = self.send_receive([LOGIN, username, password], self.server_host, self.server_port)
        return result

    def fetch(self, fname):
        result = self.send_receive([FETCH, fname], self.server_host, self.server_port)
        return result
    
    def publish(self, lname, fname):
        helper.create_repo()
		check_existed_fname=helper.make_publish_copy(lname,fname)
        if(not check_existed_fname  ):
        	self.error_message="The file is already exist in repo"
            return False
        print('publish peer')        result = self.send_receive([PUBLISH, self.username, fname], self.server_host, self.server_port)
        return result

            
