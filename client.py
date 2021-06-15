import os
import threading
import socket
import math
import f1decode
import f1database
import f1config
import time
import traceback

from f1enums import PacketIDs
from f1session import F1SessionManager, F1Session, session_query

PORT = f1config.CONFIG.get("/client/udpPort", 20777)
CHECK_INACTIVE_SESSIONS_INTERVALL = f1config.CONFIG.get("/client/checkInactiveSessionsIntervall", 1.0)
DATABASE_TRANSACTION_INTERVALL = f1config.CONFIG.get("/client/databaseTransactionIntervall", 60.0)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.settimeout(1.0)
udp_socket.bind(("localhost", PORT))

session_manager = None
end_threads = False
schedule_thread = None
udp_thread = None
pending_db_transactions = []

def udp_loop():
    global end_threads, udp_socket, session_manager, PORT

    while not end_threads:
        try:
            # Read UDP packet
            data, addr = udp_socket.recvfrom(4096)
            if not data:
                print("test")
                break

            # Decode the packet
            packet = f1decode.decode_packet(bytearray(data))

            # Session manager dispatches packet to corresponding session
            session_manager.dispatch_packet(packet)
        except socket.timeout as timeout_err:
            continue
        except Exception as err:
            print("UDP Loop Error:", err)
            traceback.print_exc()
            os._exit(1)


def inactive_session_handler(session: F1Session):
    try:
        if not session.has_best_lap_data():
            return

        track_id = session_query(session, 0, PacketIDs.SESSION_DATA, "content/m_trackId")
        session_type = session_query(session, 0, PacketIDs.SESSION_DATA, "content/m_sessionType")

        players = session._players
        for player_id in players.keys():
            car_index = players[player_id]['carIndex']
            player_name = players[player_id]['data']['m_name']
            team_id = players[player_id]['data']['m_teamId']
            tyre_compound = session_query(session, car_index, PacketIDs.CAR_STATUS_DATA,
                "content/m_carStatusData[@]/m_visualTyreCompound"
            )
            best_lap_time = session_query(session, car_index, PacketIDs.LAP_DATA,
                "content/m_lapData[@]/m_bestLapTime"
            )

            pending_db_transactions.append((
                player_name, track_id, session_type,
                team_id, tyre_compound, best_lap_time
            ))
    except Exception as err:
        print("Inactive Session Handler Error:", err)
        traceback.print_exc()


def event_check_inactive_sessions():
    session_manager.handle_inactive_sessions(inactive_session_handler, pop_on_inactive=True)


def event_database_transaction():
    pass


schedule = [
    [
        time.time() + CHECK_INACTIVE_SESSIONS_INTERVALL,
        event_check_inactive_sessions,
        CHECK_INACTIVE_SESSIONS_INTERVALL
    ],
    [
        time.time() + DATABASE_TRANSACTION_INTERVALL,
        event_database_transaction,
        DATABASE_TRANSACTION_INTERVALL
    ]
]

def schedule_loop():
    while not end_threads:
        try:
            time.sleep(0.5)
            current_time = time.time()
            for event in schedule:
                if event[0] < current_time:
                    event[0] = current_time + event[2]
                    event[1]()


        except Exception as err:
            print("Schedule Loop Error:", err)
            traceback.print_exc()
            os._exit(1)


def start_client():
    global udp_thread, schedule_thread, end_threads, session_manager

    end_threads = False
    pending_transactions = []
    session_manager = F1SessionManager()
    
    udp_thread = threading.Thread(target=udp_loop, name="udp_thread")
    udp_thread.start()

    schedule_thread = threading.Thread(target=schedule_loop, name="schedule_thread")
    schedule_thread.start()


def exit_client():
    global udp_thread, schedule_thread, end_threads

    end_threads = True

    schedule_thread.join()
    udp_thread.join()
