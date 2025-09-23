import logging
from datetime import datetime, timedelta


class StateManager:
    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        self.last_swipe_times = {}  # Stores the last swipe time for each UID
        self.shift_state = {}  # uid -> 'in'/'out'
        self.shift_start_times = {}  # uid -> datetime

    def initialize_states(self):
        """Initializes shift states from storage at startup."""
        logging.info("Initializing states from storage...")
        initial_states = self.storage.read_latest_states()

        # Set default 'out' state for all badges
        for uid in self.config.badge_map.keys():
            self.shift_state[uid] = "out"

        # Restore latest known states
        for badge_uid, data in initial_states.items():
            if data and "state" in data and "timestamp" in data:
                self.shift_state[badge_uid] = data["state"]
                person_id = self.config.badge_map.get(badge_uid)
                person = (
                    self.config.people_map.get(person_id)
                    if person_id is not None
                    else None
                )
                person_name = person["name"] if person else "Unknown"

                if data["state"] == "in":
                    start_time = datetime.fromtimestamp(data["timestamp"])
                    self.shift_start_times[badge_uid] = start_time
                    logging.info(
                        f"Restored state for {person_name} ({badge_uid}): IN, started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                else:
                    logging.info(f"Restored state for {person_name} ({badge_uid}): OUT")
            else:
                logging.warning(
                    f"Could not restore state for badge {badge_uid}, data is incomplete: {data}"
                )

    def is_swipe_debounced(self, badge_uid, now):
        """
        Checks if the swipe is a duplicate based on the debounce setting.
        Returns True if the swipe is a duplicate, False otherwise.
        """
        last_swipe = self.last_swipe_times.get(badge_uid)
        if last_swipe:
            time_since_last_swipe = now - last_swipe
            if time_since_last_swipe < timedelta(
                minutes=self.config.swipe_debounce_minutes
            ):
                logging.warning(
                    f"Ignoring duplicate swipe for badge UID {badge_uid}. "
                    f"Last swipe was {time_since_last_swipe.total_seconds():.1f} seconds ago. "
                    f"Debounce is set to {self.config.swipe_debounce_minutes} minute(s)."
                )
                return True  # Is a duplicate
        return False  # Not a duplicate

    def handle_swipe(self, badge_uid, person_id, now):
        """
        Handles a card swipe, updating the state and returning action details.
        """
        # A swipe is only handled if it's not a duplicate, so update the last swipe time here.
        self.last_swipe_times[badge_uid] = now

        current_state = self.shift_state.get(badge_uid, "out")
        buffer = timedelta(minutes=self.config.swipe_time_buffer_minutes)

        if current_state == "out":
            new_state = "in"
            self.shift_state[badge_uid] = new_state
            self.shift_start_times[badge_uid] = now

            effective_time = (now - buffer).replace(second=0, microsecond=0)
            action = {
                "person_id": person_id,
                "new_state": new_state,
                "time_effective": int(effective_time.timestamp()),
            }
            return new_state, action, None  # new_state, action, duration_string

        else:  # current_state == 'in'
            new_state = "out"
            self.shift_state[badge_uid] = new_state
            start_time = self.shift_start_times.pop(badge_uid, now)
            duration = now - start_time

            total_seconds = duration.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            duration_str = f"{hours} Stunden und {minutes} Minuten"

            effective_time = (now + buffer).replace(second=0, microsecond=0)
            action = {
                "person_id": person_id,
                "new_state": new_state,
                "time_effective": int(effective_time.timestamp()),
                "shift_start_timestamp": int(start_time.timestamp()),
                "shift_end_timestamp": int(effective_time.timestamp()),
                "shift_duration_min": minutes,
            }
            return new_state, action, duration_str
