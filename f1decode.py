import struct
import math
from f1structs import *

# Supported C datatypes and their corresponding format string
# Format strings start with < to indicate that all data is little-endian
datatypes = {
    "uint8":  (1, "<B"),
    "uint16": (2, "<H"),
    "uint32": (4, "<I"),
    "uint64": (8, "<Q"),
    "int8":   (1, "<b"),
    "int16":  (2, "<h"),
    "int32":  (4, "<i"),
    "int64":  (8, "<q"),
    "float":  (4, "<f"),
    "double": (8, "<d"),
}


def extract_struct(bytestream, structname):
    """
    Extracts one structure as dict from given bytestream.
    structname is a string containing the name of one of the structures
    defined above.

    Returns: a tuple containing the decoded struct and the number of
    bytes read
    """

    struct_data = {}
    total_bytes = 0
    for attr in eval(structname):
        value, bytes_read = extract_field(bytestream, attr[0])
        bytestream = bytestream[bytes_read:]
        total_bytes += bytes_read
        struct_data[attr[1]] = value
    return struct_data, total_bytes


def read_string_from_stream(bytestream, datatype):
    char_count = int(datatype.split("*")[1])
    format_string = "<%ds" % char_count
    string = bytestream[:char_count].decode()
    string_length = 0
    while string[string_length] not in "\u0000\u2026":
        string_length += 1
    return string[:string_length], char_count


def extract_field(bytestream, datatype):
    """
    Extracts a single field from given bytestream. The datatype must
    match one of those in the datatypes list above. If a struct name
    is given, it will extract the entire struct.

    Returns: a tuple containing the decoded field and the number of
    bytes read
    """

    # Determine if the field is an array and if so, how many values
    # need to be read

    if "char*" in datatype:
         return read_string_from_stream(bytestream, datatype)

    n = 1
    if "*" in datatype:
        split = datatype.split("*")
        datatype = split[0]
        n = int(split[1])


    value = 0
    bytes_read = 0

    # If the datatype is one of the structs defined above, read the struct
    if "struct" in datatype:
        if n > 1:
            # Read array of structs
            value = []
            for i in range(n):
                v, struct_size = extract_struct(bytestream, datatype)
                bytestream = bytestream[struct_size:]
                value.append(v)
        else:
            # Read singular struct
            value, bytes_read = extract_struct(bytestream, datatype)
    # If the datatype is an integral type, read that value
    else:
        word_size, format_string = datatypes.get(datatype, (0, None))
        if format_string:
            if n > 1:
                # Read array of integral data
                value = []
                offset = 0
                for i in range(n):
                    offset = i * word_size
                    second_index = offset + word_size
                    value.append(struct.unpack(format_string, bytestream[offset:second_index])[0])
                bytes_read = offset + word_size
            else:
                # Read singular integral value
                value = struct.unpack(format_string, bytestream[:word_size])[0]
                bytes_read = word_size
    return value, bytes_read


def decode_packet(bytestream):
    """
    Decode an entire UDP package. Returns a dict which contains
    header and content data.

    Returns: a dictionary containing the package header and content data
    """

    # Read the packet header
    header, bytes_read = extract_struct(bytestream, "struct_PacketHeader")
    bytestream = bytestream[bytes_read:]

    # Check if that struct type exists / is implemented
    packet_data = None
    toplevel_struct_type = packet_ids.get(header["m_packetId"], None)
    if toplevel_struct_type:
        packet_data, bytes_read = extract_struct(bytestream, toplevel_struct_type)

    return {
        "header": header,
        "content": packet_data
    }


def _encode_field_to_bytestream(field_data, datatype, bytestream):
    if datatype.startswith("struct"):
        _encode_struct_to_bytestream(field_data, datatype, bytestream)
    else:
        binary_data = struct.pack(datatypes[datatype][1], field_data)
        bytestream += binary_data


def _encode_struct_to_bytestream(packet, structtype, bytestream):
    for field in eval(structtype):
        (datatype, member_name) = field

        field_data = packet[member_name]

        if "*" in datatype:
            pure_datatype = datatype.split("*")[0]
            if pure_datatype == "char":
                pure_datatype = "uint8"
                field_data = field_data.encode('utf-8')
            count = int(datatype.split("*")[1])
            for i in range(count):
                if datatype.startswith("char"):
                    if i >= len(field_data):
                        value = 0
                    else:
                        value = field_data[i]
                else:
                    value = field_data[i]

                _encode_field_to_bytestream(value, pure_datatype, bytestream)
        else:
            _encode_field_to_bytestream(field_data, datatype, bytestream)


def encode_packet(packet):
    bytestream = bytearray()

    _encode_struct_to_bytestream(packet["header"], "struct_PacketHeader", bytestream)
    content_structtype = packet_ids[packet["header"]["m_packetId"]]
    _encode_struct_to_bytestream(packet["content"], content_structtype, bytestream)
    
    return bytes(bytestream)


def format_lap_time(lap_time_seconds: float) -> str:
    """
    Converts times from seconds in floating point format to strings that
    represent times like in-game, e.g. 86.12345 -> '01:26.123'
    """

    return "%s:%s.%s" % (
        str(int(lap_time_seconds / 60)).rjust(2, '0'),
        str(int(lap_time_seconds % 60)).rjust(2, '0'),
        str(int(1000 * (lap_time_seconds - math.floor(lap_time_seconds)))).rjust(3, '0')
    )
