#!/usr/bin/env python3
from monitor import Monitor
import sys
import configparser
from socket import timeout
import hashlib

def generate_checksum(data):
	return hashlib.sha256(data).hexdigest()

def split_and_send_file(info):
	send_monitor = info['send_monitor']
	file_path = info['file_to_send']
	
	# 64 = size of checksum, 2 = size of '|', 10 = size of packet number
	max_packet_size = info['max_packet_size']
	base_packet_size = max_packet_size - 4 - 64 - 2 - 10
	receiver_id	= info['receiver_id']
	send_monitor.socketfd.settimeout(3)

	packet_number = 0 	# latest received packet number from receiver 
	with open(file_path, 'rb') as file:
		while True:
			chunk = file.read(base_packet_size)
			if not chunk:	# if end of file is reached
				send_monitor.send(receiver_id, b"END_OF_TRANSMISSION")
				break

			checksum = generate_checksum(chunk)
			packet = f'{packet_number}|{checksum}|'.encode() + chunk  # Packet format: packet_num|checksum|data

			# Retransmission logic
			while True:
				try: 
					send_monitor.send(receiver_id, packet)
					# print(f'packet number{packet_number}|{checksum} has been sent')

					addr, ack = send_monitor.recv(max_packet_size)
					ack_sequence = ack.decode()
					ack_number = int(ack_sequence)
					
					# if received packet number is in correct order
					# print(f"ack_number: {ack_number}, packet_number: {packet_number}")
					if ack_number == packet_number:
						packet_number += 1
						break
					# else:
						print(f"Unexpected ACK number. Expected: {packet_number}, received: {ack_number}")
				except timeout:
					# print(f"Packet{packet_number}: ACK not received, retransmitting the chunk")
					# print(packet)
					continue
	
	# Waiting for end-of-transmission ACK
	while True:
		try:
			addr, ack = send_monitor.recv(max_packet_size)
			if ack.decode() == "END_ACK":
				# print("Transmission successfully completed.")
				break
			# else:
			# 	print("Unexpected final ACK.")
		except timeout:
			# print("Final ACK not received, resending end-of-transmission signal.")
			send_monitor.send(receiver_id, b"END_OF_TRANSMISSION")
	# addr, ack = send_monitor.recv(max_packet_size)
	# if ack_sequence == "END_ACK":
	# 	send_monitor.socketfd.settimeout(None)
	# 	print("Transmission successfully completed.")
	# else:
	# 	print("Error in end-of-transmission acknowledgment.")
	# return

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
		'receiver_id': receiver_id
	}
	split_and_send_file(info)

	# Exit! Make sure the receiver ends before the sender. send_end will stop the emulator.
	send_monitor.send_end(receiver_id)