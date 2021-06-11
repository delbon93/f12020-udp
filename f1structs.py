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

# Structures for packet ID 4: Participants
struct_ParticipantData = [
    ("uint8", "m_aiControlled"),
    ("uint8", "m_driverId"),
    ("uint8", "m_teamId"),
    ("uint8", "m_raceNumber"),
    ("uint8", "m_nationality"),
    ("char*48", "m_name"),
    ("uint8", "m_yourTelemetry"),
]

struct_PacketParticipantsData = [
    ("uint8", "m_numActiveCars"),
    ("struct_ParticipantData*22", "m_participants"),
]

# Structures for packet ID 5: Car Setups
struct_CarSetupData = [
    ("uint8", "m_frontWing"),
    ("uint8", "m_rearWing"),
    ("uint8", "m_onThrottle"),
    ("uint8", "m_offThrottle"),
    ("float", "m_frontCamber"),
    ("float", "m_rearCamber"),
    ("float", "m_frontToe"),
    ("float", "m_rearToe"),
    ("uint8", "m_frontSuspension"),
    ("uint8", "m_rearSuspension"),
    ("uint8", "m_frontAntiRollBar"),
    ("uint8", "m_rearAntiRollBar"),
    ("uint8", "m_frontSuspensionHeight"),
    ("uint8", "m_rearSuspensionHeight"),
    ("uint8", "m_brakePressure"),
    ("uint8", "m_brakeBias"),
    ("float", "m_rearLeftTyrePressure"),
    ("float", "m_rearRightTyrePressure"),
    ("float", "m_frontLeftTyrePressure"),
    ("float", "m_frontRightTyrePressure"),
    ("uint8", "m_ballast"),
    ("float", "m_fuelLoad"),
]

struct_PacketCarSetupData = [
    ("struct_CarSetupData*22", "m_carSetups"),
]

# Structures for packet ID 6: Car Telemetry
struct_CarTelemetryData = [
    ("uint16", "m_speed"),
    ("float", "m_throttle"),
    ("float", "m_steer"),
    ("float", "m_brake"),
    ("uint8", "m_clutch"),
    ("int8", "m_gear"),
    ("uint16", "m_engineRPM"),
    ("uint8", "m_drs"),
    ("uint8", "m_revLightsPercent"),
    ("uint16*4", "m_brakesTemperature"),
    ("uint8*4", "m_tyresSurfaceTemperature"),
    ("uint8*4", "m_tyresInnerTemperature"),
    ("uint16", "m_engineTemperature"),
    ("float*4", "m_tyresPressure"),
    ("uint8*4", "m_surfaceType"),
]

struct_PacketCarTelemetryData = [
    ("struct_CarTelemetryData*22", "m_carTelemetryData"),
    ("uint32", "m_buttonStatus"),
    ("uint8", "m_mfdPanelIndex"),
    ("uint8", "m_mfdPanelIndexSecondaryPlayer"),
    ("int8", "m_suggestedGear"),
]

# Structures for packet ID 7: Car Status
struct_CarStatusData = [
    ("uint8", "m_tractionControl"),
    ("uint8", "m_antiLockBrakes"),
    ("uint8", "m_fuelMix"),
    ("uint8", "m_frontBrakeBias"),
    ("uint8", "m_pitLimiterStatus"),
    ("float", "m_fuelInTank"),
    ("float", "m_fuelCapacity"),
    ("float", "m_fuelRemainingLaps"),
    ("uint16", "m_maxRPM"),
    ("uint16", "m_idleRPM"),
    ("uint8", "m_maxGears"),
    ("uint8", "m_drsAllowed"),

    ("uint16", "m_drsActivationDistance"),

    ("uint8*4", "m_tyresWear"),
    ("uint8", "m_actualTyreCompound"),

    ("uint8", "m_visualTyreCompund"),

    ("uint8", "m_tyreAgeLaps"),
    ("uint8*4", "m_tyresDamage"),
    ("uint8", "m_frontLeftWingDamage"),
    ("uint8", "m_frontRightWingDamage"),
    ("uint8", "m_rearWingDamage"),

    ("uint8", "m_drsFault"),

    ("uint8", "m_engineDamage"),
    ("uint8", "m_gearBoxDamage"),
    ("int8", "m_vehicleFiaFlags"),

    ("float", "m_ersStoreEnergy"),
    ("uint8", "m_ersDeployMode"),

    ("float", "m_ersHarvestedThisLapMGUK"),
    ("float", "m_ersHarvestedThisLapMGUK"),
    ("float", "m_ersDeployedThisLap"),
]

struct_PacketCarStatusData = [
    ("struct_CarStatusData*22", "m_carStatusData"),
]

# Structures for packet ID 8: Final Classification
struct_FinalClassificationData = [
    ("uint8", "m_position"),
    ("uint8", "m_numLaps"),
    ("uint8", "m_gridPosition"),
    ("uint8", "m_points"),
    ("uint8", "m_numPitStops"),
    ("uint8", "m_resultStatus"),

    ("float", "m_bestLapTime"),
    ("double", "m_totalRaceTime"),
    ("uint8", "m_penaltiesTime"),
    ("uint8", "m_numPenalties"),
    ("uint8", "m_numTyreStints"),
    ("uint8*8", "m_tyreStintsActual"),
    ("uint8*8", "m_tyreStintsVisual"),
]

struct_PacketFinalClassificationData = [
    ("uint8", "m_numCars"),
    ("struct_FinalClassificationData*22", "m_classificationData"),
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
    4: "struct_PacketParticipantsData",
    5: "struct_PacketCarSetupData",
    6: "struct_PacketCarTelemetryData",
    7: "struct_PacketCarStatusData",
    8: "struct_PacketFinalClassificationData",
    9: "struct_PacketLobbyInfoData",
}
