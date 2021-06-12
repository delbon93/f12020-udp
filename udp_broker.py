import socket
import json

IN_PORT = 20778
DEFAULT_PORT = 20777
CONFIG_FILE = 'config.json'

def address_to_target(address_str: str):
    if ":" in t:
        address = t.split(":")[0]
        port = int(t.split(":")[1])
    else:
        address = t
        port = DEFAULT_PORT
    return (address, port)

# load targets
targets = []

with open(CONFIG_FILE, 'r') as config_file:
    data = config_file.read()

json_obj: dict = json.loads(data)

if not "broker" in json_obj.keys():
    print("error: no configuration 'broker' in config file '%s'" % CONFIG_FILE)
    exit(1)

if not "targets" in json_obj["broker"].keys():
    print("no targets defined")
    exit(0)

for t in json_obj["broker"]["targets"]:
    targets.append(address_to_target(t))

if not "source" in json_obj["broker"].keys():
    print("no source defined, using default 'localhost:20777'")
    source = ("localhost", 20777)
else:
    source = address_to_target(json_obj["broker"]["source"])

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(source)

out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    try:
        # Read UDP packet
        data, addr = s.recvfrom(4096)
        if not data:
            break

        for target in targets:
            out_socket.sendto(data, target)

    except Exception as error:
        print(error.with_traceback())
        exit(1)