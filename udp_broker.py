import socket
import config
import client
import f1decode
import traceback
import time
from logging import log
import f1structs
import f1enums

DEFAULT_PORT = 20777
STEAM_ID = config.CONFIG.get("/broker/steamID")

packet_count = 0

if not STEAM_ID:
    log("Fatal: No SteamID provided in config file(s)!")
    exit(1)

def address_to_target(address_str: str):
    if ":" in address_str:
        address = address_str.split(":")[0]
        port = int(address_str.split(":")[1])
    else:
        address = address_str
        port = DEFAULT_PORT
    return (address, port)

# load targets
targets = []
target_strings = config.CONFIG.get("/broker/targets")

if not target_strings:
    log("No targets defined, shutting down")
    exit(0)

for t in target_strings:
    targets.append(address_to_target(t))


def udp_packet_handler_callback(packet):
    global packet_count
    
    packet_count += 1

    if not packet["header"]["m_packetId"] in f1structs.packet_ids.keys():
        return

    if packet["header"]["m_packetId"] == f1enums.PacketIDs.PARTICIPANTS_DATA:
        car_id = packet["header"]["m_playerCarIndex"]
        prev_name = packet["content"]["m_participants"][car_id]["m_name"]
        packet["content"]["m_participants"][car_id]["m_name"] = STEAM_ID
        log("Replaced '%s' with '%s'" % (prev_name, STEAM_ID))

    recoded = f1decode.encode_packet(packet)

    for target in targets:
        out_socket.sendto(recoded, target)



source = address_to_target(config.CONFIG.get("/broker/source", ":20777"))
log("Starting UDP client on port %d..." % source[1])
udp_thread = client.UDPThread(source[1], packet_decoder=f1decode.decode_packet, packet_handler=udp_packet_handler_callback)
udp_thread.start()
log("Started")

out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

log("READY")
try:
    while True:
        time.sleep(1.0)
        # log("Received %d packets last second" % packet_count)
        packet_count = 0

except KeyboardInterrupt:
    log("Keyboard Interrupt: Shutting down...")
except Exception as error:
    print("UDP Broker Error:", error)
    traceback.print_exc()
    exit(1)
finally:
    log("Closing outgoing socket...")
    out_socket.close()
    log("Shutting down UDP client...")
    udp_thread.stop()
