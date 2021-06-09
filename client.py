import socket
import decode_f12020 as f1decode

PORT = 20777

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("localhost", PORT))
while True:
    # Read UDP packet
    data, addr = s.recvfrom(4096)
    if not data:
        break

    data = bytearray(data)
    
    # Decode the packet
    packet = f1decode.decode_packet(data)

    # DEBUG: print header and content if the packet is Session Data
    if packet["content"] and packet["header"]["m_packetId"] == 1:
        print("Header = ", packet["header"], "\n\n", "Content = ", packet["content"], "\n\n")
