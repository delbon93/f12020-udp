import socket
import json

IN_PORT = 20778
DEFAULT_PORT = 20777

# load targets
targets = []

with open('config.json', 'r') as config_file:
    data = config_file.read()

json_obj = json.loads(data)
for t in json_obj["broker"]["targets"]:
    if ":" in t:
        adress = t.split(":")[0]
        port = int(t.split(":")[1])
    else:
        adress = t
        port = DEFAULT_PORT
    targets.append((adress, port))


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", IN_PORT))

# out_sockets = []
# for target in targets:
#     print(target)
#     s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
#     s_out.bind(target)
#     out_sockets.append(s_out)
out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    try:
        # Read UDP packet
        data, addr = s.recvfrom(4096)
        if not data:
            break

        # print("rec from ", addr)

        # for s_out in out_sockets:
        #     s_out.send(data)

        for target in targets:
            # print("sending to", target)
            out_socket.sendto(data, target)

    except Exception as error:
        print(error.with_traceback())
        exit(1)