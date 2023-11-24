
import socket
from constants import *
import pickle

class ObjectInfo:
    def __init__(self, host, port, list_id=None):  # -
        self.host = host  # address of server hosting lists        #-
        self.port = int(port)  # the port it will be listening to       #-
        self.list_id = list_id  # the list for which this stub is meant  #-

    def send_receive(self, message):
        sock = socket.socket()  # create a socket
        print(self.host, self.port)
        sock.connect((self.host, self.port))  # connect to server
        sock.send(pickle.dumps(message))  # send some data
        result = pickle.loads(sock.recv(1024))  # receive the response
        sock.close()  # close the connection
        return result

    
    def register(self, hostname):
        assert self.list_id is None 
        result = self.send_receive([REGISTER, hostname])
        self.list_id, registered_successfully = result[0], result[1]
        return registered_successfully
    def publish(self, hostname, filename):
        result = self.send_receive([PUBLISH, hostname, filename])
        self.list_id, publish_successfully = result[0], result[1]
        return publish_successfully