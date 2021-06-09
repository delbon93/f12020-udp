import struct

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
}

# STRUCTS
# These structs are identical to the C structs described in the specification:
# https://forums.codemasters.com/topic/50942-f1-2020-udp-specification/
# The only difference is that they do NOT contain a field for header data. This
# header data is extracted seperately to determine the package type in the first
# place and thereafter provided seperately from these content data structures

# Common packet header
struct_PacketHeader = [
    ("uint16", "m_packetFormat"),
    ("uint8",  "m_gameMajorVersion"),
    ("uint8",  "m_gameMinorVersion"),
    ("uint8",  "m_packetVersion"),
    ("uint8",  "m_packetId"),
    ("uint64", "m_sessionUID"),
    ("float",  "m_sessionTime"),
    ("uint32", "m_frameIdentifier"),
    ("uint8",  "m_playerCarIndex"),
    ("uint8",  "m_secondaryPlayerCarIndex"),
]

# Structures for packet ID 0: Motion Data
struct_CarMotionData = [
    ("float", "m_worldPositionX"),
    ("float", "m_worldPositionY"),
    ("float", "m_worldPositionZ"),
    ("float", "m_worldVelocityX"),
    ("float", "m_worldVelocityY"),
    ("float", "m_worldVelocityZ"),
    ("int16", "m_worldForwardDirX"),
    ("int16", "m_worldForwardDirY"),
    ("int16", "m_worldForwardDirZ"),
    ("int16", "m_worldRightDirX"),
    ("int16", "m_worldRightDirY"),
    ("int16", "m_worldRightDirZ"),
    ("float", "m_gForceLateral"),
    ("float", "m_gForceLongitudinal"),
    ("float", "m_gForceVertical"),
    ("float", "m_yaw"),
    ("float", "m_pitch"),
    ("float", "m_roll"),
]

struct_PacketMotionData = [
    ("struct_CarMotionData*22", "m_carMotionData"),
    ("float*4", "m_suspensionPosition"),
    ("float*4", "m_suspensionVelocity"),
    ("float*4", "m_suspensionAcceleration"),
    ("float*4", "m_wheelSpeed"),
    ("float*4", "m_wheelSlip"),
    ("float", "m_localVelocityX"),
    ("float", "m_localVelocityY"),
    ("float", "m_localVelocityX"),
    ("float", "m_angularVelocityX"),
    ("float", "m_angularVelocityY"),
    ("float", "m_angularVelocityX"),
    ("float", "m_angularAccelerationX"),
    ("float", "m_angularAccelerationY"),
    ("float", "m_angularAccelerationX"),
    ("float", "m_frontWheelsAngle"),
]

# Structures for packet ID 1: Session Data
struct_MarshalZone = [
    ("float", "m_zoneStart"),
    ("int8", "m_zoneFlag"),
]

struct_WeatherForecastSample = [
    ("uint8", "m_sessionType"),
    ("uint8", "m_timeOffset"),
    ("uint8", "m_weather"),
    ("int8", "m_trackTemperature"),
    ("int8", "m_airTemperature"),
]

struct_PacketSessionData = [
    ("uint8", "m_weather"),
    ("int8", "m_trackTemperature"),
    ("int8", "m_airTemperature"),
    ("uint8", "m_totalLaps"),
    ("uint16", "m_trackLength"),
    ("uint8", "m_sessionType"),
    ("int8", "m_trackId"),
    ("uint8", "m_formula"),
    ("uint16", "m_sessionTimeLeft"),
    ("uint16", "m_sessionDuration"),
    ("uint8", "m_pitSpeedLimit"),
    ("uint8", "m_gamePaused"),
    ("uint8", "m_isSpectating"),
    ("uint8", "m_spectatorCarIndex"),
    ("uint8", "m_sliProNativeSupport"),
    ("uint8", "m_numMarshalZones"),
    ("struct_MarshalZone*21", "m_marshalZones"),
    ("uint8", "m_safetyCarStatus"),
    ("uint8", "m_networkGame"),
    ("uint8", "m_numWeatherForecastSamples"),
    ("struct_WeatherForecastSample*20", "m_weatherForecastSamples"),
]

# Top level package structures are linked to their packet IDs here
packet_ids = {
    0: "struct_PacketMotionData",
    1: "struct_PacketSessionData"
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
                for i in range(n):
                    offset = i * word_size
                    value.append(struct.unpack(format_string, bytestream[offset:offset+word_size]))
                bytes_read = offset
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
