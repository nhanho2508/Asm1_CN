import pickle
import struct
import time
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
def create_manage_repo(repo_path):
    manage_repo_name = "manage.repo"
    create_file_path = os.path.join(repo_path, manage_repo_name)
    if not os.path.exists(create_file_path):
        with open(create_file_path, 'w'):
            pass
    else:
        print("already create manage repo")
        return create_file_path
    os.system(f'attrib +h "{create_file_path}"') #hide repo file
    print(f'success create manage repo at "{create_file_path}"')
    return create_file_path
def make_publish_copy(lname_path, fname, repo_path):
    fname_path = os.path.join(repo_path, fname)
    if os.path.exists(fname_path):
        print("already existed")
        return
    os.chmod(lname_path, 0o400) #get permission
    with open(lname_path, 'rb') as source_file:
        with open(fname_path, 'wb') as destination_file:
            chunk_size = 8192
            while True:
                chunk = source_file.read(chunk_size)
                if not chunk:
                    break
                destination_file.write(chunk)
    print("success make copy to repo")
def create_repo():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    folder_name = "repo_test"
    create_folder_path = os.path.join(current_folder, folder_name)
    if not os.path.exists(create_folder_path):
        os.makedirs(create_folder_path)
    print(create_folder_path)