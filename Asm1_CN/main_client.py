import socket 
from server.server import *
from peer.peer import *
if __name__ == '__main__':
    host = gethostbyname(gethostname())
    port = "8081"
    PORT = "8080"
    HOST = host
    peer = Peer(int(port), host, int(PORT), HOST)
    # create peer to test
    # peer1=Peer(int(port), '172.20.11.122', int(PORT), HOST)
    # peer2=Peer(int(port), '172.20.11.123', int(PORT), HOST)
    """
    #Test for ping
    while True:
        peer.respond_ping()
    """
    peer.run()
    
    
         


         

