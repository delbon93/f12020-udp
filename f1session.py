import time
import f1config
from f1enums import PacketIDs

class F1SessionManager:

    def __init__(self):
        self.sessions = {}
    

    def dispatch_packet(self, packet) -> None:
        session_uid = packet["header"]["m_sessionUID"]
        if not session_uid in self.sessions.keys():
            self.sessions[session_uid] = F1Session()
            print("Registered session '%d'" % session_uid)
        self.sessions[session_uid].receive_packet(packet)

    
    def handle_inactive_sessions(self, handler, pop_on_inactive=False) -> list:
        to_pop = []
        for uid in self.sessions.keys():
            if not self.sessions[uid].is_active():
                handler(self.sessions[uid])
                if pop_on_inactive:
                    to_pop.append(uid)
        
        for uid in to_pop:
            self.sessions.pop(uid)



class F1Session:
    LOBBY_PACKET_TIMEOUT = f1config.CONFIG.get("/sessions/lobbyPacketTimeout", 3.0)
    SESSION_ACTIVE_TIMEOUT = f1config.CONFIG.get("/sessions/sessionActiveTimeout", 10.0)

    def __init__(self):
        self.motion_data = {}
        self.session_data = {}
        self.lap_data = {}
        self.event_data = {}
        self.participants_data = {}
        self.car_setup_data = {}
        self.car_telemetry_data = {}
        self.car_status_data = {}
        self.final_classification_data = {}
        self.lobby_info_data = {}

        self._id_to_packet_list = [
            self.motion_data, self.session_data, self.lap_data, self.event_data,
            self.participants_data, self.car_setup_data, self.car_telemetry_data,
            self.car_status_data, self.final_classification_data, self.lobby_info_data,
        ]

        self._session_start_time = time.time()
        self._last_packet_received_time = None
        self._last_lobby_packet_received_time = None

        self.session_uid = None
        self.num_players = 0
        self.total_packets_reveived = 0
        self._players = {}


    def is_in_lobby(self) -> bool:
        in_lobby = self._last_lobby_packet_received_time != None
        if in_lobby:
            time_diff = time.time() - self._last_lobby_packet_received_time
            in_lobby = in_lobby and (time_diff < F1Session.LOBBY_PACKET_TIMEOUT)
        return in_lobby
    

    def is_active(self) -> bool:
        if self._last_packet_received_time == None:
            return False
        return (time.time() - self._last_packet_received_time) < F1Session.SESSION_ACTIVE_TIMEOUT


    def has_best_lap_data(self) -> bool:
        if len(self.session_data) == 0: return False
        if len(self.car_status_data) == 0: return False
        if len(self.lap_data) == 0: return False
        return True

    
    def get_participants(self, players_only=False) -> list:
        if len(self.participants_data) == 0:
            return []
        
        active_players = []
        participants_packet = list(self.participants_data.values())[0]
        for p_data in participants_packet["content"]["m_participants"]:
            if (p_data["m_aiControlled"] == 0 or not players_only) and p_data["m_nationality"] > 0:
                active_players.append(p_data)
        
        return active_players

    
    def receive_packet(self, packet) -> None:
        if self.session_uid == None:
            self.session_uid = packet["header"]["m_sessionUID"]

        player_car_id = packet["header"]["m_playerCarIndex"]
        packet_id = packet["header"]["m_packetId"]
        frame_id = packet["header"]["m_frameIdentifier"]
        
        # Discard packet if present packet is newer
        if player_car_id in self._id_to_packet_list[packet_id].keys():
            if self._id_to_packet_list[packet_id][player_car_id]["header"]["m_frameIdentifier"] > frame_id:
                return

        self._id_to_packet_list[packet_id][player_car_id] = packet

        if packet["header"]["m_packetId"] == PacketIDs.PARTICIPANTS_DATA:
            player_car_id = packet["header"]["m_playerCarIndex"]
            player_data = packet["content"]["m_participants"]
            player_driver_id = player_data[player_car_id]["m_driverId"]
            self._players[player_driver_id] = {
                "data": player_data[player_car_id],
                "carIndex": player_car_id,
            }
        
        self.total_packets_reveived += 1
        self._last_packet_received_time = time.time()



def session_query(session: F1Session, car_id: int, packet_id: int, query: str):
    query_elements = query.split("/")
    packet = session._id_to_packet_list[packet_id][car_id]
    current_element = packet
    last_query_element = "<root>"
    while len(query_elements) > 0:
        #print("--------\n", current_element, "----------\n")
        curr_query_element = query_elements.pop(0)
        
        # replace placeholders
        curr_query_element = curr_query_element.replace("@", "%d" % car_id)

        if "[" in curr_query_element:
            element_split = curr_query_element.split("[")
            member_name, index = element_split[0], int(element_split[1].replace("]", ""))
            if not member_name in current_element.keys():
                return {"error": "No member '%s' in '%s'!" % (member_name, last_query_element), "query": query}
            if index >= len(current_element[member_name]) or index < 0:
                return {
                    "error": "Index '%d' out of range for list '%s' (has %d elements)" % (index, member_name, len(current_element[member_name])), 
                    "query": query
                    }
            current_element = current_element[member_name][index]
        else:
            current_element = current_element[curr_query_element]

        last_query_element = curr_query_element
    
    return current_element
        
