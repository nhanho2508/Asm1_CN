import pickle
import socket
import struct
import time
from constants import *
import os

def create_snmp_response(community, request_id, start_time):
    version = 0x00  # SNMPv1
    request_type = 0xA0  # GET PDU
    error_status = 0
    error_index = 0 
    null_byte = 0
    PDU_type = 0
   
    end_time = time.time()
    snmp_packet = pickle.dumps([version, community, request_type, request_id, error_status, error_index, null_byte, PDU_type, end_time - start_time])

    return snmp_packet

def send_file(conn, file_name):
    print("[**] Sending file...")
    storage_path = os.path.join(os.getcwd(), 'storage')
    # downloads_path = os.path.join(os.getcwd(), 'downloads')
    file_path = os.path.join(storage_path, file_name)
    with open(file_path, 'rb') as f:
        for data in f:
            conn.sendall(data)
    conn.close()            
    print('SEND successfully.')
    return 1

def receive_file(self, conn, filename):
    print("[**] Downloading file...")
    # storage_path = os.path.join(os.getcwd(), 'storage')
    downloads_path = os.path.join(os.getcwd(), 'downloads')
    file_path = os.path.join(downloads_path, filename)
    with open(file_path, 'wb') as f:
        while True:
            data = conn.recv(BUFFER)
            if not data:
                break
            f.write(data)
        f.close()
    print('DOWNLOAD successfully.')
    conn.close()
    return 1