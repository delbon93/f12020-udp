import client
import time
import f1decode
import f1session
import os
import json
import config
from f1enums import PacketIDs

CHECKING_INTERVAL = config.CONFIG.get("/client/checkingInterval", 1.0)
USE_STDOUT = config.CONFIG.get("/client/stdout", False)
session_manager = f1session.F1SessionManager()
current_best_times = {}

def register_time(session_uid, player_name, last_time, data):
    """
    Register a current 'last lap time' if it is faster than the previous best time.
    Times are registered per player, and players are registered per session.
    """

    global current_best_times
    if not session_uid in current_best_times.keys():
        current_best_times[session_uid] = {}
    if not player_name in current_best_times[session_uid].keys():
        current_best_times[session_uid][player_name] = (last_time, data)
    else:
        saved_time = current_best_times[session_uid][player_name][0]
        if last_time < saved_time:
            current_best_times[session_uid][player_name] = (last_time, data)


def callback(packet):
    """
    Packet handler for the UDP thread
    """
    
    session_manager.dispatch_packet(packet)


udp_thread = client.UDPThread(20777, packet_decoder=f1decode.decode_packet, packet_handler=callback)
udp_thread.start()

while True:
    # Iterate over all sessions and query last lap times for each player. These times and associated
    # data is then inserted into current_best_times if that player beat their prevous best time in
    # their respective session
    for session in session_manager.sessions.values():
        current_times = session.query(0, PacketIDs.LAP_DATA,
            "content/m_lapData[+]/m_lastLapTime")

        track_id = session.query(0, PacketIDs.SESSION_DATA,
            "content/m_trackId")
        session_type = session.query(0, PacketIDs.SESSION_DATA,
            "content/m_sessionType")
        
        
        for current_time in current_times:
            player_name = current_time[0]["data"]["m_name"]
            car_id = current_time[0]["carIndex"]
            lap_time = current_time[1]
            lap_time_pretty = f1decode.format_lap_time(current_time[1])
            team_id = session.query(car_id, PacketIDs.PARTICIPANTS_DATA,
                "content/m_participants[@]/m_teamId")
            tyre_id = session.query(car_id, PacketIDs.CAR_STATUS_DATA,
                "content/m_carStatusData[@]/m_visualTyreCompound")

            # If no lap has been completed yet, the last lap time will be 0. Therefore we have
            # to check for reasonable times
            if lap_time > 10.0:
                register_time(session.session_uid, player_name, lap_time,
                    (player_name, track_id, session_type, team_id, tyre_id, lap_time))
    
    # If stdout is enabled, print the current best times data structure
    if USE_STDOUT:
        os.system('clear')
        print("current_best_times =", json.dumps(current_best_times, indent=2))
    time.sleep(CHECKING_INTERVAL)


udp_thread.stop()
