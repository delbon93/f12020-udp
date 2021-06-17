import socket
import threading
import traceback

class UDPThread:
    """
    Owns a thread that receives udp packets. Handling of these packets can be adjusted
    by providing handler functions:
        
    """

    def __init__(self, port, packet_decoder=None, packet_handler=None):
        """
        Initializes the thread wrapper.
            port: the port on which the udp socket will listen for incoming packets

            packet_decoder: the raw binary data packet is passed to this function and then
                        replaced by its return value.
                        If not provided: keep raw binary data

            packet_handler: the decoded packet (or raw binary data if no decoder was provided)
                        is passed to the packet handler. This is where the packet leaves
                        the UDPThread packet pipeline.
                        If not provided: the packet will be dropped
        """

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(1.0)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._should_end = False
        self._packet_decoder = packet_decoder
        self._packet_handler = packet_handler
        self._thread = threading.Thread(target=self._run, args=(port,))
        self._thread.daemon = True


    def _run(self, port):
        self._socket.bind(("", port))

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
        """
        Starts the thread and beginns receiving packets
        """
        self._thread.start()
    
    def stop(self):
        """
        Ends the thread (indirectly). Waits for the threads loop to
        come to an end. This can take time, since the socket might
        have to time out before the loop can end.
        """
        self._should_end = True
        self._thread.join()
