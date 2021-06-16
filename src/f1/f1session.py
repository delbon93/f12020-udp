import time
import config
from f1enums import PacketIDs

class F1SessionManager:
    """
    Maintains sessions by snooping packets for their session UID. Dispatches
    packets to their respective sessions and provides a way to handle sessions
    that have become inactive
    """

    def __init__(self):
        self.sessions = {}
    

    def dispatch_packet(self, packet) -> None:
        """
        Check for session UID in packet header and dispatch the packet
        to the relevant session
        """

        session_uid = packet["header"]["m_sessionUID"]
        if not session_uid in self.sessions.keys():
            self.sessions[session_uid] = F1Session()
        self.sessions[session_uid].receive_packet(packet)

    
    def handle_inactive_sessions(self, handler, pop_on_inactive=False) -> list:
        """
        Check all sessions for inactivity. If any session is inactive, the handler function
        is called with that session as its parameter. If pop_on_inactive is True, the inactive
        session will be removed from the session managers session registry.
        """

        to_pop = []
        for uid in self.sessions.keys():
            if not self.sessions[uid].is_active():
                handler(self.sessions[uid])
                if pop_on_inactive:
                    to_pop.append(uid)
        
        for uid in to_pop:
            self.sessions.pop(uid)



class F1Session:
    """
    Maintains incoming data about a session. The most recent packets are stored
    per packet type and therein per player (= client that sends packets belonging
    to this session).
    Also stores meta data like timestamps for last received packet etc.
    """

    LOBBY_PACKET_TIMEOUT = config.CONFIG.get("/sessions/lobbyPacketTimeout", 3.0)
    SESSION_ACTIVE_TIMEOUT = config.CONFIG.get("/sessions/sessionActiveTimeout", 10.0)

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

        # Lookup table to map packet types to their respective data
        self._id_to_packet_list = [
            self.motion_data, self.session_data, self.lap_data, self.event_data,
            self.participants_data, self.car_setup_data, self.car_telemetry_data,
            self.car_status_data, self.final_classification_data, self.lobby_info_data,
        ]

        self._session_start_time = time.time()
        self._last_packet_received_time = None
        self._last_lobby_packet_received_time = None

        self.session_uid = None
        self.total_packets_reveived = 0
        self._players = {}


    def is_in_lobby(self) -> bool:
        """
        Returns True if the session is in lobby, False if not.
        If for LOBBY_PACKET_TIMEOUT seconds no lobby packet is received,
        the session is considered to be not in a lobby
        """

        in_lobby = self._last_lobby_packet_received_time != None
        if in_lobby:
            time_diff = time.time() - self._last_lobby_packet_received_time
            in_lobby = in_lobby and (time_diff < F1Session.LOBBY_PACKET_TIMEOUT)
        return in_lobby
    

    def is_active(self) -> bool:
        """
        Returns True if the session is active, False if not.
        If for SESSION_ACTIVE_TIMOUT seconds no packet is received,
        the session is considered to be inactive
        """

        if self._last_packet_received_time == None:
            return False
        return (time.time() - self._last_packet_received_time) < F1Session.SESSION_ACTIVE_TIMEOUT


    def has_best_lap_data(self) -> bool:
        """
        Returns True if all data is present to get all relevant data
        to determine best lap times for the session, False if not
        """

        if len(self.session_data) == 0: return False
        if len(self.car_status_data) == 0: return False
        if len(self.lap_data) == 0: return False
        if len(self.participants_data) == 0: return False
        return True

    
    def get_participants(self, players_only=False) -> list:
        """
        Returns packet data about all participants in the session (or just players).
        The packet data will be the contents of all relevant ParticipantData structures
        in the PARTICIPANT_DATA packet
        """

        if len(self.participants_data) == 0:
            return []
        
        active_players = []
        participants_packet = list(self.participants_data.values())[0]
        for p_data in participants_packet["content"]["m_participants"]:
            if (p_data["m_aiControlled"] == 0 or not players_only) and p_data["m_nationality"] > 0:
                active_players.append(p_data)
        
        return active_players

    
    def receive_packet(self, packet) -> None:
        """
        The session saves data from the decoded packet.
        """

        # Set session UID
        if self.session_uid == None:
            self.session_uid = packet["header"]["m_sessionUID"]

        player_car_id = packet["header"]["m_playerCarIndex"]
        packet_id = packet["header"]["m_packetId"]
        frame_id = packet["header"]["m_frameIdentifier"]
        
        # Discard packet if present packet is newer
        if player_car_id in self._id_to_packet_list[packet_id].keys():
            if self._id_to_packet_list[packet_id][player_car_id]["header"]["m_frameIdentifier"] > frame_id:
                return

        # Store the packet in the right place
        self._id_to_packet_list[packet_id][player_car_id] = packet

        # If the packet is a PARTICIPANTS_DATA packet, extract information about players
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
    """
    Get data from the session.
        car_id: The query will use packets from that clients point of view (i.e. packets
            that have been sent by them)
        packet_id: The packet type to apply the query to
        query: A string that describes the data to be retrieved

    About query strings:
        Query strings are unix path-like: 'content/m_somePacketStructMember'
        A packet contains a header and its content, so the query string starts with either
        'content' or 'header', depending on the information that is to be queried.
        After that, the path of the data that is to be queried relies on the packet structure
        in question, for that the struct definitions in 'f1structs.py' or the official
        specification (https://forums.codemasters.com/topic/50942-f1-2020-udp-specification/) 
        should be referenced.

        Arrays can be indexed as expected: 'content/m_someArray[4]/m_someValue'
        Instead of an index, special placeholders can be used:

            'm_someArray[@]':
                @ will be replaced by the given car_id

            'm_someArray[+]':
                + acts like a glob that evaluates to the car_ids of all human players in the
                session. For each player a sub-query will be created, with all occurences of
                the + character replaced by their respective car_id. The result of all 
                sub-queries are stored in a list, which will be the result of the main query

    """

    # Create sub-queries if the + placeholder is used
    if "+" in query:
        results = []
        for player in session._players.values():
            player_query = query.replace("+", str(player["carIndex"]))
            results.append((player, session_query(session, car_id, packet_id, player_query)))
        return results


    query_elements = query.split("/")
    if not car_id in session._id_to_packet_list[packet_id]:
        return {"error": "No packet for car id '%d'!" % (car_id), "query": query}

    packet = session._id_to_packet_list[packet_id][car_id]
    current_element = packet
    last_query_element = "<root>"

    while len(query_elements) > 0:
        curr_query_element = query_elements.pop(0).replace("@", "%d" % car_id)

        # If current query element is an indexed array
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
        
