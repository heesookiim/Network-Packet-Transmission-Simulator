# Network-Packet-Transmission-Simulator

This project simulates the transmission of packets over a network, focusing on packet formatting, sending, receiving, error handling, and logging. It serves as an educational resource on the principles of network communication, error management, and socket programming in Python.

## Project Structure
```emulator.py```: Simulates a network environment including latency, packet dropping, and reordering based on predefined settings.  
```monitor.py```: A utility used by the sender and receiver for network communication, packet formatting, and logging.  
```receiver.py```: Manages the reception of packets, verifying packet integrity, and writing the received data to a file.  
```sender.py```: Handles data division into packets, checksum calculations, and packet sending.  
```sender_stop_and_go.py```: Implements a simple stop-and-go (or stop-and-wait) protocol for packet transmission.
```receiver_stop_and_go.py```: Complements sender_stop_and_go.py by handling packet reception according to the stop-and-go protocol.  

## Setup Instructions
Python Environment: Verify that Python 3.x is installed. This project relies solely on the Python standard library.
Configure Network Settings: Edit the config.ini file to suit your simulation requirements. Sample configurations are provided within the file.

## Running the Simulator

Start the network emulator, sender, and receiver in separate terminal sessions:

### Network Emulator:

```console
python3 emulator.py <config_file_path> 
```
Ensure the configuration file path is specified correctly.
### Sender or Stop-and-Go Sender:
For the basic sender:
```console
python3 sender.py <config_file_path>
```
For the stop-and-go protocol sender:
```console
python3 sender_stop_and_go.py <config_file_path>
```

### Receiver or Stop-and-Go Receiver:
For the basic receiver:
```console
python3 receiver.py <config_file_path>
```
For the stop-and-go protocol receiver:
```console
python3 receiver_stop_and_go.py <config_file_path>
```
Replace <config_file_path> with the path to your configuration file, ensuring consistency across all components.

## Results
Sender log:
```
Id:1 | Starting monitor on ('localhost', 8004).

File Size                  : 578317 bytes
Total Bytes Transmitted    : 684324 bytes
Overhead                   : 106007 bytes
Number of Packets sent     : 677
Total Time                 : 38.01 secs
Goodput                    : 15213.17 bytes/sec
```
Receiver log:
```
Id:2 | Starting monitor on ('localhost', 8005).

File transmission correct    : True
Number of Packets Received   : 665
Total Bytes Transmitted      : 672153
Total Time                   : 37.8 secs
```

**Goodput**: the rate at which useful data is transmitted over a network.  
**Overhead**: all the additional data — such as protocol headers, metadata, acknowledgements, and retransmissions — that must be sent alongside the actual payload data for the network to function correctly

## License

This project, including all source code files and documentation, was developed as part of the coursework for ECE 50863 at Purdue University. The project is provided for educational purposes only and is not licensed for external use or distribution. Unauthorized use, reproduction, or distribution of this project, or any portion of it, may violate university policies and could be subject to penalties. Use of this project outside of its intended context and repository is strictly prohibited.
