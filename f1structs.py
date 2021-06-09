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

# Structures for packet ID 2: Lap Data
struct_LapData = [
    ("float", "m_lastLapTime"),
    ("float", "m_currentLapTime"),

    ("uint16", "m_sector1TimeInMS"),
    ("uint16", "m_sector2TimeInMS"),
    ("float", "m_bestLapTime"),
    ("uint8", "m_bestLapNum"),
    ("uint16", "m_bestLapSector1TimeInMS"),
    ("uint16", "m_bestLapSector2TimeInMS"),
    ("uint16", "m_bestLapSector3TimeInMS"),
    ("uint16", "m_bestOverallSector1TimeInMS"),
    ("uint8", "m_bestOverallSector1LapNum"),
    ("uint16", "m_bestOverallSector2TimeInMS"),
    ("uint8", "m_bestOverallSector2LapNum"),
    ("uint16", "m_bestOverallSector3TimeInMS"),
    ("uint8", "m_bestOverallSector3LapNum"),

    ("float", "m_lapDistance"),

    ("float", "m_totalDistance"),

    ("float", "m_safetyCarDelta"),
    ("uint8", "m_carPosition"),
    ("uint8", "m_currentLapNum"),
    ("uint8", "m_pitStatus"),
    ("uint8", "m_sector"),
    ("uint8", "m_currentLapInvalid"),
    ("uint8", "m_penalties"),
    ("uint8", "m_gridPosition"),
    ("uint8", "m_driverStatus"),

    ("uint8", "m_resultStatus"),
]

struct_PacketLapData = [
    ("struct_LapData*22", "m_lapData"),
]

# Structures for packet ID 9: Lobby Info
struct_LobbyInfoData = [
    ("uint8", "m_aiControlled"),
    ("uint8", "m_teamId"),
    ("uint8", "m_nationality"),
    ("char*48", "m_name"),
    ("uint8", "m_readyStatus"),
]

struct_PacketLobbyInfoData = [
    ("uint8", "m_numPlayers"),
    ("struct_LobbyInfoData*22", "m_lobbyPlayers"),
]


# Top level package structures are linked to their packet IDs here
packet_ids = {
    0: "struct_PacketMotionData",
    1: "struct_PacketSessionData",
    2: "struct_PacketLapData",
    9: "struct_PacketLobbyInfoData"
}
