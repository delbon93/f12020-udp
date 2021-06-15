import socket
import config

IN_PORT = 20778
DEFAULT_PORT = 20777

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
    print("no targets defined")
    exit(0)

for t in target_strings:
    targets.append(address_to_target(t))

source = config.CONFIG.get("/broker/source", "localhost:20777")

in_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
in_socket.bind(source)

out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        # Read UDP packet
        data, addr = in_socket.recvfrom(4096)
        if not data:
            break

        for target in targets:
            out_socket.sendto(data, target)

except Exception as error:
    print(error)
    exit(1)
finally:
    in_socket.close()
    out_socket.close()
