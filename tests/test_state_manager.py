import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from badgereader.state_manager import StateManager


@pytest.fixture
def state_manager(mock_config, mock_storage):
    """Fixture for a StateManager instance."""
    sm = StateManager(mock_config, mock_storage)
    return sm


def test_initial_state(state_manager):
    """Test that the initial state of all badges is 'out'."""
    state_manager.initialize_states()
    assert all(state == "out" for state in state_manager.shift_state.values())


def test_debounce_logic(state_manager):
    """Test that the debounce logic correctly identifies duplicate swipes."""
    badge_uid = "12345678"
    now = datetime.now()

    # First swipe should not be debounced
    assert not state_manager.is_swipe_debounced(badge_uid, now)

    # Update the last swipe time to simulate a handled swipe
    state_manager.last_swipe_times[badge_uid] = now

    # Second swipe within the debounce period should be debounced
    assert state_manager.is_swipe_debounced(badge_uid, now + timedelta(seconds=30))

    # Third swipe after the debounce period should not be debounced
    assert not state_manager.is_swipe_debounced(badge_uid, now + timedelta(minutes=2))


def test_handle_swipe_in_and_out(state_manager):
    """Test the full swipe-in and swipe-out cycle."""
    badge_uid = "12345678"
    person_id = "person_a"
    now = datetime.now()

    # Swipe in
    new_state, action, duration_str = state_manager.handle_swipe(
        badge_uid, person_id, now
    )
    assert new_state == "in"
    assert action["new_state"] == "in"
    assert duration_str is None
    assert state_manager.shift_state[badge_uid] == "in"

    # Swipe out
    now = now + timedelta(hours=1)
    new_state, action, duration_str = state_manager.handle_swipe(
        badge_uid, person_id, now
    )
    assert new_state == "out"
    assert action["new_state"] == "out"
    assert duration_str is not None
    assert "1 Stunden und 0 Minuten" in duration_str
    assert state_manager.shift_state[badge_uid] == "out"
