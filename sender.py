#!/usr/bin/env python3
from monitor import Monitor
import sys
import configparser
from socket import timeout
import hashlib
import time

def generate_checksum(data):
    return hashlib.sha256(data).hexdigest()

def split_and_send_file(info):
    send_monitor = info['send_monitor']
    file_path = info['file_to_send']
    max_packet_size = info['max_packet_size']
    receiver_id = info['receiver_id']
    window_size = info['window_size']
    send_monitor.socketfd.settimeout(3)  # Set a timeout for the socket operations

    base_packet_size = max_packet_size - 4 - 64 - 2 - 10
    next_seq_num = 0
    last_ack_received = -1
    window_packets = {}
    eof = False

    with open(file_path, 'rb') as file:
        while last_ack_received < next_seq_num or next_seq_num == 0:
            # Send packets as long as we have space in the window
            while next_seq_num < last_ack_received + window_size and not eof:
                chunk = file.read(base_packet_size)
                if not chunk:
                    # End of file reached
                    send_monitor.send(receiver_id, b"END_OF_TRANSMISSION")
                    print(f'{ack_num} has been received')
                    eof = True
                    break
                checksum = generate_checksum(chunk)
                packet = f'{next_seq_num}|{checksum}|'.encode() + chunk
                window_packets[next_seq_num] = packet
                send_monitor.send(receiver_id, packet)
                # print(f'{next_seq_num}|{checksum} has been sent')
                next_seq_num += 1

            # Receive ACKs
            try:
                addr, ack = send_monitor.recv(max_packet_size)
                if ack == b"END_ACK":
                    print("Transmission successfully completed.")
                    return
                ack_num = int(ack.decode())
                # print(f'{ack_num} has been received')
                if ack_num > last_ack_received:
                    last_ack_received = ack_num
                    # Remove all acknowledged packets from the window
                    for seq in list(window_packets):
                        if seq <= ack_num:
                            del window_packets[seq]
            except timeout:
                # Resend all packets in the window
                for packet in window_packets.values():
                    send_monitor.send(receiver_id, packet)

if __name__ == '__main__':
    print("Sender starting up!")
    config_path = sys.argv[1]

    # Initialize sender monitor
    send_monitor = Monitor(config_path, 'sender')

    # Parse config file
    cfg = configparser.RawConfigParser(allow_no_value=True)
    cfg.read(config_path)
    receiver_id = int(cfg.get('receiver', 'id'))
    # file_to_send = cfg.get('nodes', 'file_to_send')
    file_to_send = "./to_send_large.txt"
    max_packet_size = int(cfg.get('network', 'MAX_PACKET_SIZE'))

    # 1. divide sending data into frames
    info = {
        'send_monitor': send_monitor,
        'file_to_send': file_to_send,
        'max_packet_size': max_packet_size,
        'receiver_id': receiver_id,
        'window_size': 10
    }
    split_and_send_file(info)

    # Exit! Make sure the receiver ends before the sender. send_end will stop the emulator.
    send_monitor.send_end(receiver_id)