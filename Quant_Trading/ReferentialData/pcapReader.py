#%%
from scapy.all import *
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import TCP,IP
import argparse
import os
import sys
try:
    packets = rdpcap(r"C:\Users\raymo\OneDrive\Desktop\20250106_1_021.pcap")
except FileNotFoundError:
    print("Error: pcap file not found.")
except Exception as e:
        print(f"An error occurred: {e}")
packets

# %%
pcap_file = r'C:\Users\raymo\OneDrive\Desktop\20250106_1_021.pcap'
output_file = r'C:\Users\raymo\OneDrive\Desktop\20250106_1_021.txt'
output_file_2 = r'C:\Users\raymo\OneDrive\Desktop\20250106_1_021_2.txt'
import time

def printable_timestamp(ts, resol):
    ts_sec = ts // resol
    ts_subsec = ts % resol
    ts_sec_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts_sec))
    return '{}.{}'.format(ts_sec_str, ts_subsec)

#---
#%%

def jpExchangeDecoder(line: str):
    payloadExtract = line.split('t')[1:]
    # payloadExtract = line[26:]
    end = len(payloadExtract)
    start = 0
    res = []
    while start < end:
        print(payloadExtract[start:start+1])
        print(payloadExtract[start:start+1].decode('ascii'))
        buffer_length = int(payloadExtract[start:start+1].decode('ascii'), 2)
        res.append(payloadExtract[start+1:start+1+buffer_length].decode('ascii'))
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

test_pcap(pcap_file, output_file)
#%%
def process_pcap(in_file, out_file):
    f = open(out_file, "w+")
    count = 0
    first_timestamp = 0
    line_list = []
    # Looping through all the packets in the PCAP
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
        line = ether_pkt[Raw].load
        # print(line.decode("ascii"))
        line_list.append(line.decode("utf-8") + '\n')
        # if count > 100:
        #     break
    
    f.writelines(line_list)
    f.close()

# process_pcap(pcap_file, output_file_2)
# %%


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='PCAP reader')
    # parser.add_argument('--pcap', metavar='<pcap file name>',
    #                     help='pcap file to parse', required=True)
    # args = parser.parse_args()

    
    file_name = pcap_file#args.pcap
    if not os.path.isfile(file_name):
        print('"{}" does not exist'.format(file_name), file=sys.stderr)
        sys.exit(-1)

    test_pcap(pcap_file, output_file)
    sys.exit(0)