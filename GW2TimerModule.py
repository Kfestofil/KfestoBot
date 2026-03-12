import os
import sqlite3
import time
import requests
from typing import Dict, List, Tuple, Optional

WIKI_TIMER_URL = "https://wiki.guildwars2.com/wiki/Widget:Event_timer/data.json?action=raw"
CHECK_WINDOW = 5  # minutes before event start
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gw2_subscriptions.db")

from enum import Enum

class GW2Event(Enum):
    #world bosses
    ADMIRAL_TAIDHA_COVINGTON = "Admiral Taidha Covington"
    SVANIR_SHAMAN_CHIEF = "Svanir Shaman Chief"
    MEGADESTROYER = "Megadestroyer"
    FIRE_ELEMENTAL = "Fire Elemental"
    THE_SHATTERER = "The Shatterer"
    GREAT_JUNGLE_WURM = "Great Jungle Wurm"
    MODNIIR_ULGOTH = "Modniir Ulgoth"
    SHADOW_BEHEMOTH = "Shadow Behemoth"
    CLAW_OF_JORMAG = "Claw of Jormag"
    GOLEM_MARK_II = "Golem Mark II"

    TRIPLE_TROUBLE = "Triple Trouble"
    KARKA_QUEEN = "Karka Queen"
    TEQUATL_THE_SUNLESS = "Tequatl the Sunless"

    # Tangled Depths metas
    CHAK_GERENT = "Chak Gerent"

    # Auric Basin metas
    OCTOVINE = "Octovine"

    # PoF/Path of Fire metas

    DOPPELGANGER = "Doppelganger"

    # LW4/Domain of Istan
    PALAWADAN = "Palawadan"

    # LW4/Jahai Bluffs
    ESCORTS = "Escorts"
    DEATH_BRANDED_SHATTERER = "Death-Branded Shatterer"

    # LW4/Thunderhead Peaks metas
    THUNDERHEAD_KEEP = "Thunderhead Keep"
    THE_OIL_FLOES = "The Oil Floes"

    # Icebrood Saga metas
    EFFIGY = "Effigy"
    DOOMLORE_SHRINE = "Doomlore Shrine"
    OOZE_PITS = "Ooze Pits"
    METAL_CONCERT = "Metal Concert"
    DRAKKAR_AND_SPIRITS_OF_THE_WILD = "Drakkar and Spirits of the Wild"
    DEFEND_JORAS_KEEP = "Defend Jora's Keep"
    SHARDS_AND_CONSTRUCT = "Shards and Construct"
    ICEBROOD_CHAMPIONS = "Icebrood Champions"

    # End of Dragons metas
    AETHERBLADE_ASSAULT = "Aetherblade Assault"
    KAINENG_BLACKOUT = "Kaineng Blackout"
    GANG_WAR = "Gang War"
    JADE_MAW = "Jade Maw"
    THE_BATTLE_FOR_THE_JADE_SEA = "The Battle for the Jade Sea"

    # Public instance events
    TWISTED_MARIONETTE = "Twisted Marionette"
    BATTLE_FOR_LIONS_ARCH = "Battle For Lion's Arch"
    DRAGONSTORM = "Dragonstorm"
    TOWER_OF_NIGHTMARES = "Tower of Nightmares"

    #convergence
    MOUNT_BALRIOR = "Mount Balrior"
    OUTER_NAYOS = "Outer Nayos"

EVENT_NAME_TO_ID = {event.value: event for event in GW2Event.__members__.values()}

class GW2EventNotifier:
    """
    Handles GW2 event rotation checking and user subscriptions.
    """

    def __init__(self):
        # raw JSON from wiki
        self.data = None

        # Per-group rotation cache:
        # group_key -> list of { "event_id": GW2Event, "chatlink": str, "duration": int }
        self.group_rotations: Dict[str, List[Dict]] = {}

        # event_id -> list of user IDs
        self.subscriptions: Dict[GW2Event, List[int]] = {}

        # to prevent duplicate notifications per minute
        self.last_notified: Dict[str, bool] = {}

        self._init_db()
        self._load_subscriptions()
        self._load_data()
        self._build_rotation()

    # -------------------------------
    # Database
    # -------------------------------
    def _init_db(self):
        con = sqlite3.connect(DB_PATH)
        con.execute(
            "CREATE TABLE IF NOT EXISTS subscriptions ("
            "  user_id INTEGER NOT NULL,"
            "  event_name TEXT NOT NULL,"
            "  PRIMARY KEY (user_id, event_name)"
            ")"
        )
        con.commit()
        con.close()

    def _load_subscriptions(self):
        """Load all subscriptions from the database into memory."""
        con = sqlite3.connect(DB_PATH)
        rows = con.execute("SELECT user_id, event_name FROM subscriptions").fetchall()
        con.close()
        for user_id, event_name in rows:
            event_id = EVENT_NAME_TO_ID.get(event_name)
            if event_id is None:
                continue
            self.subscriptions.setdefault(event_id, [])
            if user_id not in self.subscriptions[event_id]:
                self.subscriptions[event_id].append(user_id)

    def _load_data(self):
        r = requests.get(WIKI_TIMER_URL)
        self.data = r.json()

    def _build_rotation(self):
        """
        Builds a per-group rotation cache. Each event group (world bosses, HoT metas, etc.)
        has its own independent rotation that cycles simultaneously.
        """
        for group_key, event_group in self.data["events"].items():
            segments = event_group.get("segments", {})
            pattern = event_group.get("sequences", {}).get("pattern", [])

            if not pattern:
                continue

            group_steps = []
            for step in pattern:
                seg = segments.get(str(step["r"]))
                if seg is None:
                    continue

                name = seg.get("name", "")
                chatlink = seg.get("chatlink") or seg.get("chat_link")
                event_id = EVENT_NAME_TO_ID.get(name)
                duration = step["d"]

                group_steps.append({
                    "event_id": event_id,  # None for filler/unknown segments
                    "chatlink": chatlink,
                    "duration": duration,
                    "name": name
                })

            if group_steps:
                self.group_rotations[group_key] = group_steps

    # -------------------------------
    # Subscription management
    # -------------------------------
    def subscribe(self, user_id: int, event_id: GW2Event):
        self.subscriptions.setdefault(event_id, [])
        if user_id not in self.subscriptions[event_id]:
            self.subscriptions[event_id].append(user_id)
            con = sqlite3.connect(DB_PATH)
            con.execute(
                "INSERT OR IGNORE INTO subscriptions (user_id, event_name) VALUES (?, ?)",
                (user_id, event_id.value)
            )
            con.commit()
            con.close()

    def unsubscribe(self, user_id: int, event_id: GW2Event):
        if event_id in self.subscriptions and user_id in self.subscriptions[event_id]:
            self.subscriptions[event_id].remove(user_id)
            con = sqlite3.connect(DB_PATH)
            con.execute(
                "DELETE FROM subscriptions WHERE user_id = ? AND event_name = ?",
                (user_id, event_id.value)
            )
            con.commit()
            con.close()

    def get_subscribers(self, event_id: GW2Event) -> List[int]:
        return self.subscriptions.get(event_id, [])

    # -------------------------------
    # Rotation checking
    # -------------------------------
    def _get_upcoming_events(self) -> List[Tuple[Dict, int, int]]:
        """
        For each group, finds the NEXT event that hasn't started yet.
        Returns a list of (next_step_dict, minutes_until_start, start_minute_utc)
        where start_minute_utc is the absolute minute the event begins (used for dedup).
        """
        now_minutes = int(time.time() // 60)
        upcoming = []

        for group_key, steps in self.group_rotations.items():
            total = sum(s["duration"] for s in steps)
            if total == 0:
                continue

            offset = now_minutes % total

            # Find which step is currently active and where the next one starts
            elapsed = 0
            for i, step in enumerate(steps):
                start = elapsed
                end = elapsed + step["duration"]
                if start <= offset < end:
                    minutes_until_next = end - offset
                    next_index = (i + 1) % len(steps)
                    next_step = steps[next_index]
                    # Absolute UTC minute when the next event starts
                    start_minute_utc = now_minutes + minutes_until_next
                    upcoming.append((next_step, minutes_until_next, start_minute_utc))
                    break
                elapsed = end

        return upcoming

    def check_events(self) -> List[Tuple[GW2Event, Optional[str], List[int]]]:
        """
        Returns a list of tuples (event_id, chatlink, [user_ids]) for tracked events
        starting in CHECK_WINDOW minutes or less, across ALL groups simultaneously.
        Only notifies once per event occurrence.
        """
        notifications = []

        for step, minutes_until_start, start_minute_utc in self._get_upcoming_events():
            event_id = step["event_id"]

            # skip filler/unknown segments
            if event_id is None:
                continue

            if minutes_until_start > CHECK_WINDOW:
                continue

            if event_id not in self.subscriptions:
                continue

            # Dedup key: event + its absolute start time, so we only notify once per occurrence
            dedup_key = f"{event_id.value}:{start_minute_utc}"
            if dedup_key in self.last_notified:
                continue

            users = self.subscriptions[event_id]
            notifications.append((event_id, step["chatlink"], users))
            self.last_notified[dedup_key] = True

        return notifications