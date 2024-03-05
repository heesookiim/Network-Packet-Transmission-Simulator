#!/usr/bin/env python3
from monitor import Monitor
import sys
import configparser
import hashlib
import os

def calc_total_packets(file_path, max_packet_size):
    file_size = os.path.getsize(file_path)
    if max_packet_size == 0: raise ValueError("max_packet_size cannot be 0")
    total_packets = (file_size // (max_packet_size - 4 - 64 - 2 - 10)) + 1
    return total_packets

def generate_checksum(data):
    return hashlib.sha256(data).hexdigest()

def receive_chunks(info):
    recv_monitor = info['recv_monitor']
    write_location = info['write_location']
    max_packet_size = info['max_packet_size']
    file_path = info['file_to_send']

    total_packets = calc_total_packets(file_path, max_packet_size)
    received_packets = {}
    expected_seq_num = 0

    with open(write_location, 'wb') as file:
        while expected_seq_num < total_packets:
            addr, packet = recv_monitor.recv(max_packet_size)
            if packet == b"END_OF_TRANSMISSION":
                print(f'{expected_seq_num - 1} ACK sent')
                recv_monitor.send(addr, b"END_ACK")
                break
            received_packet_number, checksum, data = packet.split(b'|', 2)
            received_packet_number = int(received_packet_number)
            calculated_checksum = generate_checksum(data).encode()
            if checksum == calculated_checksum:
                if received_packet_number == expected_seq_num:
                    # Write the in-order packet and send ACK
                    file.write(data)
                    expected_seq_num += 1
                    while expected_seq_num in received_packets:
                        # Write any buffered packets that are now in order
                        file.write(received_packets.pop(expected_seq_num))
                        expected_seq_num += 1
                elif received_packet_number > expected_seq_num:
                    # Buffer out-of-order packets
                    received_packets[received_packet_number] = data
                # Send ACK for the highest in-order packet
                recv_monitor.send(addr, str(expected_seq_num - 1).encode())
                # print(f'{expected_seq_num - 1} ACK sent')

if __name__ == '__main__':
    print("Receiver starting up!")
    config_path = sys.argv[1]
    recv_monitor = Monitor(config_path, 'receiver')
    cfg = configparser.RawConfigParser(allow_no_value=True)
    cfg.read(config_path)
    sender_id = int(cfg.get('sender', 'id'))
    # file_to_send = cfg.get('nodes', 'file_to_send')
    file_to_send = "./to_send_large.txt"
    max_packet_size = int(cfg.get('network', 'MAX_PACKET_SIZE'))
    write_location = 'received'

    info = {
        'recv_monitor': recv_monitor,
        'write_location': write_location,
        'max_packet_size': max_packet_size,
        'file_to_send': file_to_send,
        'write_location': write_location
    }
    receive_chunks(info)
    
	# Send final ACK
    recv_monitor.send(sender_id, b'END_ACK')

	# Exit! Make sure the receiver ends before the sender. send_end will stop the emulator.
    recv_monitor.recv_end(write_location, sender_id)