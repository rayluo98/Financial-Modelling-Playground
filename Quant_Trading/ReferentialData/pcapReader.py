from scapy.all import *
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import TCP,IP
import argparse
import os
import sys
import numba as nb
from numba import njit
# try:
#     packets = rdpcap(r"C:\Users\raymo\OneDrive\Desktop\20250205_2_057.pcap\20250205_2_057.pcap")
# except FileNotFoundError:
#     print("Error: pcap file not found.")
# except Exception as e:
#         print(f"An error occurred: {e}")
# packets

pcap_file = r'C:\Users\raymo\OneDrive\Desktop\20250205_2_057.pcap\20250205_2_057.pcap'
output_file = r'C:\Users\raymo\OneDrive\Desktop\20250205_2_057.txt'
output_file_2 = r'C:\Users\raymo\OneDrive\Desktop\20250205_2_057.txt'
import time

def printable_timestamp(ts, resol):
    ts_sec = ts // resol
    ts_subsec = ts % resol
    ts_sec_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts_sec))
    return '{}.{}'.format(ts_sec_str, ts_subsec)

#---



TAG_LENGTH = {
    'A':26,
    'T':5,
    'O':18,
    'K':46,
    'E':20,
    'C':29,
    'D':11,
    'R':2,
    'L':3,
    '||':125,
    'BP':68,
    'MG':16
}

TAG_CONVERSION ={
    'T':"L",
    'O':"LB2sBBq",
    'L':'BB',
    'K':'LcL2xL2xQLQQ',
    'A':'LLcL2xQBB',
    'E':'LLcL2xL',
    'C':'LLcL2xLQB',
    'D':'LLcB',
    'R':'B',
    '||':'',
    'BP':'',
    'MG':''
}
import struct

def decode_big_endian(data, format_string):
  """
  Decodes big-endian data using a specified format string.

  Args:
    data: The byte string to decode.
    format_string: The format string specifying the data structure.

  Returns:
    A tuple containing the decoded values.
  """
  return struct.unpack(">" + format_string, data)

@njit(parallel=True)
@nb.vectorize()
def jpExchangeDecoder(line: str):
    payloadExtract = line
    end = len(payloadExtract)
    start = 0
    res = []
    while start < end:
        tag = payloadExtract[start:start+1].decode('ascii')
        buffer_length = TAG_LENGTH[tag]
        if tag in TAG_CONVERSION:
            res.append(decode_big_endian(payloadExtract[start+1:start+buffer_length], 
                                         TAG_CONVERSION[tag]))
        else:
            print('what do...')
        start += (1+buffer_length)
    return res
import base64
def test_pcap(in_file, out_file):
    f = open(out_file, "w+")
    count = 0
    first_timestamp = 0
    line_list = []

    packets = rdpcap(in_file)
    # Filter for TCP packets
    tcp_packets = [pkt for pkt in packets if pkt.haslayer("TCP")]
    
    # Filter for packets with a specific IP address
    ip_packets = [pkt for pkt in packets if pkt.haslayer("IP") and (pkt["IP"].src == "10.17.11.58" \
                                                                    or pkt["IP"].dst == "224.0.220.21")]
    
    # Print the filtered packets
    for packet in tcp_packets:
        print(jpExchangeDecoder(packet.payload.original))
        # line_list.append(base64.b64decode(packet[Raw].load) + '\n')
    for packet in ip_packets:
        print(jpExchangeDecoder(packet.payload.original))
        # line_list.append(base64.b64decode(packet[Raw].load) + '\n')
    # f.writelines(line_list)
    f.close()

def process_pcap(in_file, out_file):
    f = open(out_file, "w+")
    count = 0
    first_timestamp = 0
    line_list = []
    # Looping through all the packets in the PCAP
    pcap_flow = rdpcap(in_file)
    sessions = pcap_flow.sessions()
    pcap_dump = {}
    for session in sessions:
        for packet in sessions[session]:
            try:
                if packet[TCP].dport == 80:
                    payload = bytes(packet[TCP].payload)
                    url = get_url_from_payload(payload)
                    urls_output.write(url.encode())
            except Exception as e:
                pass
    for (pkt_data, pkt_metadata,) in RawPcapReader(in_file):
        ether_pkt = Ether(pkt_data)
        ip_pkt = ether_pkt[IP]
        src = ip_pkt.src # Get the source IP
        dst = ip_pkt.dst # Get the destination IP
        
        # # Calculate the relative timestamp of packets compared to the first packet
        # timestamp = pkt_metadata.sec + (pkt_metadata.usec)/1000000
        # if count == 0:
        #     first_timestamp = timestamp
        #     relative_timestamp = 0.0
        # else:
        #     relative_timestamp = timestamp - first_timestamp
        
        # pkt_size = pkt_metadata.caplen # Get packet size
        count += 1
        # line = src + " " + dst + " " + str(round(relative_timestamp, 6)) + " " + str(pkt_size) + " " + str(ip_pkt.proto) + " " + str(ip_pkt.sport) + " " + str(ip_pkt.dport) + "\n"
        line = ether_pkt[Raw].load[27:]
        # if count > 50:
        #     print(jpExchangeDecoder(line))
        # print(line.decode("ascii"))
        line_list.append(jpExchangeDecoder(line))
        # if count > 100:
        #     break
    
    f.writelines(line_list)
    f.close()

# process_pcap(pcap_file, output_file_2)

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='PCAP reader')
    # parser.add_argument('--pcap', metavar='<pcap file name>',
    #                     help='pcap file to parse', required=True)
    # args = parser.parse_args()

    
    file_name = pcap_file#args.pcap
    if not os.path.isfile(file_name):
        print('"{}" does not exist'.format(file_name), file=sys.stderr)
        sys.exit(-1)

    process_pcap(pcap_file, output_file)
    sys.exit(0)
