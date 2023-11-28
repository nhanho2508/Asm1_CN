import pickle
import socket
import struct
import time
from constants import *
# import os

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
    try:
        print("[**] Sending file...")
        # repo_path = os.path.join(os.getcwd(), 'repo')
        # downloads_path = os.path.join(os.getcwd(), 'downloads')
        file_path = os.path.join(REPO_PATH, file_name)
        # print("File path:", file_path)
        # print("Repo path:", repo_path)
        with open(file_path, 'rb') as f:
            for data in f:
                conn.sendall(data)
        f.close()
        conn.close()            
        print('[*] SEND successfully.')
        return True
    except Exception as e:
        return False

def respond_ping(conn, addr, start_time):
    print(f'[*] Received ping from {addr[0]} : {addr[1]}')
    request_id = 1
    conn.send(pickle.dumps([PING_STATUS, create_snmp_response("public", request_id, start_time), addr[0]]))

def make_publish_copy(lname_path, fname):
    fname_path = os.path.join(REPO_PATH, fname)
    if os.path.exists(fname_path):
        print("[*] The file already exists in the repo.")
        return
    os.chmod(lname_path, 0o400) #get permission
    with open(lname_path, 'rb') as source_file:
        with open(fname_path, 'wb+') as destination_file:
            chunk_size = 8192
            while True:
                chunk = source_file.read(chunk_size)
                if not chunk:
                    break
                destination_file.write(chunk)
    # print("success make copy to repo")

# def create_manage_repo(repo_path):
#     manage_repo_name = "manage.repo"
#     create_file_path = os.path.join(repo_path, manage_repo_name)
#     if not os.path.exists(create_file_path):
#         with open(create_file_path, 'w'):
#             pass
#     else:
#         print("already create manage repo")
#         return create_file_path
#     os.system(f'attrib +h "{create_file_path}"') #hide repo file
#     print(f'success create manage repo at "{create_file_path}"')

def create_repo():
    # current_folder = os.path.dirname(os.path.abspath(__file__))
    # current_folder = os.getcwd()
    # folder_name = "repo"
    # create_folder_path = os.path.join(current_folder, folder_name)
    if not os.path.exists(REPO_PATH):
        os.makedirs(REPO_PATH)
    # print(repo_path)