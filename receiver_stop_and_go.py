#!/usr/bin/env python3
from monitor import Monitor
import sys
import configparser
import hashlib
import os

def calc_total_packets(file_path, max_packet_size):
	file_size = os.path.getsize(file_path)
	if max_packet_size == 0: raise ValueError("max_packet_size cannot be 0")
	total_packets = round(file_size / (max_packet_size - 4 - 64 - 2 - 10))
	return total_packets

def generate_checksum(data):
	return hashlib.sha256(data).hexdigest()

def receive_chunks(info):
	recv_monitor = info['recv_monitor']
	write_location = info['write_location']
	max_packet_size = info['max_packet_size']
	prop_delay = info['prop_delay']
	file_path = info['file_to_send']

	# First calcualtes the minimum number of packets needed for completion
	total_packets = calc_total_packets(file_path, max_packet_size)
	current_packet_number = 0	# NOT SURE IF WE NEED THIS

	with open(write_location, 'wb') as file:
		while True:
			addr, packet = recv_monitor.recv(max_packet_size)
			if packet == b"END_OF_TRANSMISSION":
				return
			
			# split received packet into checksum and data
			received_packet_number, checksum, data = packet.split(b'|', 2)
			# print(len(packet))
			received_packet_number = int(received_packet_number)

			# Verify checksum
			calculated_checksum = generate_checksum(data).encode()
			if received_packet_number == current_packet_number:
				if checksum == calculated_checksum:
					file.write(data)
					current_packet_number = received_packet_number
					recv_monitor.send(sender_id, str(current_packet_number).encode())
					# print(f'{current_packet_number} ACK sent')
					current_packet_number += 1
			elif received_packet_number < current_packet_number:
				if checksum == calculated_checksum:
					current_packet_number = received_packet_number
					recv_monitor.send(sender_id, str(current_packet_number).encode())
					# print(f'{current_packet_number} ACK sent')
					current_packet_number += 1

if __name__ == '__main__':#
	print("Receivier starting up!")
	config_path = sys.argv[1]

	# Initialize sender monitor
	recv_monitor = Monitor(config_path, 'receiver')
	
	# Parse config file
	cfg = configparser.RawConfigParser(allow_no_value=True)
	cfg.read(config_path)
	sender_id = int(cfg.get('sender', 'id'))
	# file_to_send = cfg.get('nodes', 'file_to_send')
	file_to_send = "./to_send_large.txt"
	max_packet_size = int(cfg.get('network', 'MAX_PACKET_SIZE'))
	prop_delay = float(cfg.get('network', 'PROP_DELAY'))
	write_location = 'received'

	# 1. Listen for incoming chunks
	info = {
		'recv_monitor': recv_monitor,
		'write_location': write_location,
		'max_packet_size': max_packet_size,
		'prop_delay': prop_delay,
		'file_to_send': file_to_send
	}
	receive_chunks(info)
	
	# Send final ACK
	recv_monitor.send(sender_id, b'END_ACK')

	# Exit! Make sure the receiver ends before the sender. send_end will stop the emulator.
	recv_monitor.recv_end(write_location, sender_id)