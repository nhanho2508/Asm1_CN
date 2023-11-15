import pickle
import struct
import time
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