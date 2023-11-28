# from socket import * 
from server.server import *
if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    port = "8080"
    server = Server(host, int(port))
    
    server.run()
    