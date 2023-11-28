from server.server import *
from peer.peer import *
if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    port = "8081"
    PORT = "8080"
    HOST = host
    peer = Peer(host, int(port), HOST, int(PORT))
    """
    #Test for ping
    while True:
        peer.respond_ping()
    """
    peer.run()
    
    
         


         

