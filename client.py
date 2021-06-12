import socket
import f1decode
from f1enums import PacketIDs
import math
import json
from f1session import F1SessionManager, F1Session, session_query

PORT = 20777

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("localhost", PORT))

session_manager = F1SessionManager()

while True:
    # Read UDP packet
    data, addr = s.recvfrom(4096)
    if not data:
        break

    data = bytearray(data)
    
    # Decode the packet
    packet = f1decode.decode_packet(data)

    session_manager.dispatch_packet(packet)

    # session_uid = packet["header"]["m_sessionUID"]

    # if packet["header"]["m_packetId"] != PacketIDs.CAR_TELEMETRY_DATA:
    #     continue

    # player_name = session_query(session_manager.sessions[session_uid], 0, 
    #     PacketIDs.CAR_TELEMETRY_DATA, 
    #     "content/m_carTelemetryData[@]/m_surfaceType"
    # )
    # print(player_name)

    print("\n --<[ Sessions ]>--")
    for session_uid in session_manager.sessions.keys():
        #print("session %d: %d total packets" % (session, session_manager.sessions[session].total_packets_reveived))
        session: F1Session = session_manager.sessions[session_uid]
        active_str = "inactive"
        if session.is_session_active():
            active_str = "active"
        print("  > %d: %s session" % (session_uid, active_str))
    
