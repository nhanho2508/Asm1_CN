from asyncio.windows_events import NULL
import pickle
import socket
import struct
import time
from constants import *
# import os

def create_snmp_response():
    version = 0x00 
    community = "public"
    request_type = 0xA0
    request_id = 0
    error_status = 0
    error_index = 0 
    PDU_type = 0
    name = "IP"
    value = NULL
    snmp_packet = pickle.dumps([version, community, PDU_type, request_type, request_id, error_status, error_index, name, value])
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

def respond_ping(conn, addr):
    print(f'[*] Received ping from {addr[0]} : {addr[1]}')
    conn.send(pickle.dumps([PING_STATUS, addr[0]]))

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