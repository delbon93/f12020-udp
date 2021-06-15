import socket
import threading
import traceback

class UDPThread:

    def __init__(self, port, packet_decoder=None, packet_handler=None):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(1.0)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._should_end = False
        self._packet_decoder = packet_decoder
        self._packet_handler = packet_handler
        self._thread = threading.Thread(target=self._run, args=(port,))
        self._thread.daemon = True


    def _run(self, port):
        self._socket.bind(("localhost", port))

        while not self._should_end:
            try:
                # Read UDP packet
                packet, addr = self._socket.recvfrom(4096)
                if not packet:
                    break
                
                if self._packet_decoder:
                    # Decode the packet
                    packet = self._packet_decoder(bytearray(packet))
                    

                if self._packet_handler:
                    self._packet_handler(packet)
                
            except socket.timeout as timeout_err:
                continue
            except Exception as err:
                print("UDPThread Error:", err)
                traceback.print_exc()
                break

    def start(self):
        self._thread.start()
    
    def stop(self):
        self._should_end = True
        self._thread.join()
