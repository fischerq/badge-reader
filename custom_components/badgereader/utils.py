"""Utility functions for the Badge Reader component."""
from datetime import datetime, timedelta

def calculate_shift_duration(check_in_time: datetime, check_out_time: datetime) -> timedelta:
    """Calculates the duration of a work shift."""
    if check_in_time is None or check_out_time is None:
        return timedelta(0)
    return check_out_time - check_in_time

def format_duration(duration: timedelta) -> str:
    """Formats a timedelta duration into a human-readable string."""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def format_datetime_for_sheets(dt: datetime) -> str:
    """Formats a datetime object for Google Sheets."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_date_for_sheets(dt: datetime) -> str:
    """Formats a date from a datetime object for Google Sheets."""
    return dt.strftime("%Y-%m-%d")

def parse_datetime_from_sheets(date_str: str, time_str: str) -> datetime | None:
    """Parses date and time strings from Google Sheets into a datetime object."""
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None

def parse_float_from_sheets(value_str: str) -> float | None:
    """Parses a float value from a string, handling potential errors."""
    try:
        return float(value_str)
    except (ValueError, TypeError):
        return None

def calculate_target_hours_for_day(weekly_target_hours: float, usual_work_days: int) -> float:
    """Calculates the target hours for a single workday."""
    if usual_work_days <= 0:
        return 0.0
    return weekly_target_hours / usual_work_days

def calculate_net_change(shift_duration: timedelta, special_hours: float, target_hours_for_day: float) -> float:
    """Calculates the net change in hours for a day."""
    shift_hours = shift_duration.total_seconds() / 3600
    return shift_hours + special_hours - target_hours_for_day

def calculate_running_balance(previous_balance: float, net_change: float) -> float:
    """Calculates the new running balance."""
    return previous_balance + net_change