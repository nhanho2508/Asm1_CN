import pickle
import socket
from socket import AF_INET, SOCK_DGRAM
import struct
import time
def create_snmp_request(community):
    version = 0x00  # SNMPv1
    request_type = 0xA0  # GET PDU
    request_id = 1
    error_status = 0
    error_index = 0
    null_byte = 0
    PDU_type = 0
   
    snmp_packet = pickle.dumps([version, community, request_type, request_id, error_status, error_index, null_byte, PDU_type])

    return snmp_packet
def parse_snmp_response(snmp_response):
    if snmp_response:
        response = pickle.loads(snmp_response)
        
        pdu_type = response[7]
        error_status = response[4]
        print("error", error_status)
        if error_status == 0:
            return True
    return False
def ping(host_name):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_address = (socket.gethostbyname(host_name), 12000)
    server_socket.settimeout(2.0)
    for i in range(5):  
        start_time = time.time()
        snmp_request = create_snmp_request("public")
        try:
            server_socket.sendto(snmp_request, client_address)
            response, _ = server_socket.recvfrom(1024)

            end_time = time.time()
            elapsed_time = end_time - start_time
            if parse_snmp_response(response):
                print("SNMP Ping Successful")
            else:
                print("SNMP Ping Unsuccessful")
            print(f'Received response:  in {elapsed_time:.4f} seconds')
        except (socket.timeout, WindowsError):
            print(f'Ping {i + 1} unsuccessful. Timeout reached.')

        time.sleep(1)

    server_socket.close()
def register(conn, set_of_lists, set_of_host_name, host_name):  
    list_id = len(set_of_lists) + 1 
    set_of_host_name[list_id] = host_name
    set_of_lists[list_id] = None  
    conn.send(pickle.dumps([list_id, True]))  
    
def search(filename, setOfInfoFileLists):
    found = False
    return_file = {}
    for key in setOfInfoFileLists:
        print(setOfInfoFileLists.get(key))
        if filename in setOfInfoFileLists.get(key):
            if not found:
                found = True
            return_file[key] = setOfInfoFileLists.get(key)
    return found, return_file