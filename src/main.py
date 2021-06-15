import client
import time
import f1decode
import f1session
import os
import json
from f1enums import PacketIDs

session_manager = f1session.F1SessionManager()
current_best_times = {}

def register_time(session_uid, player_name, last_time, data):
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
    session_manager.dispatch_packet(packet)


udp_thread = client.UDPThread(20777, packet_decoder=f1decode.decode_packet, packet_handler=callback)
udp_thread.start()

while True:
    for session in session_manager.sessions.values():
        current_times = f1session.session_query(session, 0, PacketIDs.LAP_DATA,
            "content/m_lapData[+]/m_lastLapTime")

        track_id = f1session.session_query(session, 0, PacketIDs.SESSION_DATA,
            "content/m_trackId")
        session_type = f1session.session_query(session, 0, PacketIDs.SESSION_DATA,
            "content/m_sessionType")
        
        
        for current_time in current_times:
            player_name = current_time[0]["data"]["m_name"]
            car_id = current_time[0]["carIndex"]
            lap_time = current_time[1]
            lap_time_pretty = f1decode.format_lap_time(current_time[1])
            team_id = f1session.session_query(session, car_id, PacketIDs.PARTICIPANTS_DATA,
                "content/m_participants[@]/m_teamId")
            tyre_id = f1session.session_query(session, car_id, PacketIDs.CAR_STATUS_DATA,
                "content/m_carStatusData[@]/m_visualTyreCompound")

            if lap_time > 10.0:
                register_time(session.session_uid, player_name, lap_time,
                    (player_name, track_id, session_type, team_id, tyre_id, lap_time))
    
    os.system('clear')
    print("current_best_times =", json.dumps(current_best_times, indent=2))
    time.sleep(0.5)


udp_thread.stop()