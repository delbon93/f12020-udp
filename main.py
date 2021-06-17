import client
import time
import f1decode
import f1session
import f1database
import f1enumstrings
import os
import json
import config
import traceback
from logging import log
from f1enums import PacketIDs

CHECKING_INTERVAL = config.CONFIG.get("/client/checkingInterval", 1.0)
PRINT_INCOMING_BEST_TIMES = config.CONFIG.get("/logging/printIncomingBestTimes", False)
UDP_PORT = config.CONFIG.get("/client/udpPort", 20777)
session_manager = f1session.F1SessionManager()
current_best_times = {}
pending_db_transactions = []

db_connection = None
if not config.CONFIG.get("/db/offline", False):
    log("Connecting to database...")
    db_connection = f1database.connect()
    log("Connected")
else:
    log("Connection to database skipped (offline mode)")


def register_best_time(session_uid, player_name, last_time, data):
    """
    Register a current 'last lap time' if it is faster than the previous best time.
    Times are registered per player, and players are registered per session.
    """

    global current_best_times

    new_best = False

    if not session_uid in current_best_times.keys():
        current_best_times[session_uid] = {}
    if not player_name in current_best_times[session_uid].keys():
        current_best_times[session_uid][player_name] = (last_time, data, False)
        new_best = True
    else:
        saved_time = current_best_times[session_uid][player_name][0]
        if last_time < saved_time:
            new_best = True
            current_best_times[session_uid][player_name] = (last_time, data, False)
    
    if new_best and PRINT_INCOMING_BEST_TIMES:
        track_str = f1enumstrings.TrackIDs[data[1]]
        session_type_str = f1enumstrings.SessionTypes[data[2]]
        team_str = f1enumstrings.TeamIDs[data[3]]
        tyre_str = f1enumstrings.VisualTyreCompound[data[4]]
        time_str = f1decode.format_lap_time(last_time)
        log("New best time in session %d: %s" % (
            session_uid, str((player_name, track_str, session_type_str, team_str, tyre_str, time_str))
        ))


def prepare_db_transactions():
    global current_best_times, session_manager, pending_db_transactions

    for session_uid in current_best_times.keys():
        if not session_manager.sessions[session_uid].is_active():
            best_times_data = current_best_times[session_uid]
            for player in best_times_data.keys():
                if best_times_data[player][2]:
                    continue

                db_data = best_times_data[player][1]
                pending_db_transactions.append(db_data)
                current_best_times[session_uid][player] = (
                    best_times_data[player][0], best_times_data[player][1], True
                )


def process_db_transactions_batch():
    global pending_db_transactions

    if not db_connection or len(pending_db_transactions) == 0:
        return

    count = len(pending_db_transactions)

    sql = ""
    for data_entry in pending_db_transactions:
        sql += f1database.generate_best_lap_data_sql_statement(data_entry) + "\n"
    pending_db_transactions = []
    f1database.transaction(db_connection, sql)


def udp_packet_handler_callback(packet):
    """
    Packet handler for the UDP thread
    """
    
    session_manager.dispatch_packet(packet)

log("Starting UDP client on port %d..." % UDP_PORT)
udp_thread = client.UDPThread(UDP_PORT, packet_decoder=f1decode.decode_packet, packet_handler=udp_packet_handler_callback)
udp_thread.start()
log("Started")

try:
    log("READY")
    while True:
        # Iterate over all sessions and query last lap times for each player. These times and associated
        # data is then inserted into current_best_times if that player beat their prevous best time in
        # their respective session
        for session_uid in list(session_manager.sessions.keys()):
            session = session_manager.sessions[session_uid]

            if not session.has_best_lap_data():
                continue

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
                    register_best_time(session.session_uid, player_name, lap_time,
                        (player_name, track_id, session_type, team_id, tyre_id, lap_time))
        
        
        if len(current_best_times.keys()) > 0:
            prepare_db_transactions()
        if len(pending_db_transactions) > 0:
            log("Processing %d pending database transaction(s)..." % len(pending_db_transactions))
            process_db_transactions_batch()
            log("Database transactions committed")
        time.sleep(CHECKING_INTERVAL)

except KeyboardInterrupt:
    log("Keyboard Interrupt: Shutting down")
except Exception as err:
    print("Main Loop Error:", err)
    traceback.print_exc()

finally:
    log("Shutting down UDP client...")
    udp_thread.stop()
    log("Disconnecting from database...")
    f1database.disconnect(db_connection)
    log("Disconnected")
