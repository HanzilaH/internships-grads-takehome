#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional
from model import Schedule, Entry, ScheduleParsingError


# How to run:
# chmod +x render-schedule.py -> make this file an executable
# ./render-schedule.py --schedule schedule.json --overrides overrides.json --from 2025-11-07T17:00:00Z --until 2025-11-21T17:00:00Z


# Given a schedule.json and optional overrides.json, this file generate the final on-call schedule entries
# Steps:
# 1. Load and parse schedule.json into Schedule model
# 2. Load and parse overrides.json into list of Entry models
# 3. Generate base schedule entries between given from and until times
# 4. Apply overrides to base entries
# 5. Output final entries as JSON



# ---------- UTILS ----------
# NOTE: Python's datetime.fromisoformat does not support 'Z' suffix for UTC, so we handle that here.
def parse_time(s: str) -> datetime:
    """Parse ISO 8601 UTC time string."""
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def datetime_encoder(dt: datetime) -> str:
    """Format datetime back to ISO 8601 UTC."""
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def load_json(path: str | Path):
    """Load JSON file from given path with error handling."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {path}")
        raise
    except PermissionError:
        print(f"Error: Permission denied: {path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON in {path}")
        raise


# ---------- CORE LOGIC ----------

def generate_base_entries(schedule: Schedule, from_time: datetime, until: datetime) -> List[Entry]:
    """Generate the base schedule entries between from_time and until."""
    entries = []

    users = schedule.users
    handover = schedule.handover_start_at
    interval = timedelta(days=schedule.handover_interval_days)

    # Find the first shift that overlaps with [from_time, until)
    # Move forward until the end of the range
    i = 0
    while handover + interval * i < until:
        start = handover + interval * i
        end = start + interval
        user = users[i % len(users)]

        # Only include if overlaps range
        if end > from_time and start < until:
            entry_start = max(start, from_time)
            entry_end = min(end, until)
            entries.append(Entry(user=user, start_at=entry_start, end_at=entry_end))
        i += 1

    return entries

def apply_overrides(base_entries: List[Entry], overrides: List[Entry]) -> List[Entry]:
    '''
    Apply overrides to the base schedule entries. Overrides can partially or fully overlap with base entries.
    This function splits base entries as needed to accommodate overrides.
    Returns a new list of entries with overrides applied.
    '''
    
    if not overrides:
        return base_entries

    updated = []
    for entry in base_entries:
        overlapping_overrides = [
            o for o in overrides if o.end_at > entry.start_at and o.start_at < entry.end_at
        ]

        if not overlapping_overrides:
            updated.append(entry)
            continue

        current_start = entry.start_at
        for override in sorted(overlapping_overrides, key=lambda o: o.start_at):
            # Add normal period BEFORE override
            if override.start_at > current_start:
                updated.append(
                    Entry(
                        user=entry.user,
                        start_at=current_start,
                        end_at=min(override.start_at, entry.end_at),
                    )
                )
            # Add override itself (truncated to entry bounds)
            updated.append(
                Entry(
                    user=override.user,
                    start_at=max(override.start_at, entry.start_at),
                    end_at=min(override.end_at, entry.end_at),
                )
            )
            current_start = min(override.end_at, entry.end_at)

        # Add any remaining part AFTER last override
        if current_start < entry.end_at:
            updated.append(
                Entry(user=entry.user, start_at=current_start, end_at=entry.end_at)
            )

    # Sort by start time
    updated.sort(key=lambda e: e.start_at)
    return updated


# ---------- MAIN ----------
def render():
    parser = argparse.ArgumentParser(description="Render on-call schedule with overrides.")
    parser.add_argument("--schedule", required=True, help="Path to schedule JSON file")
    parser.add_argument("--overrides", required=True, help="Path to overrides JSON file", default=None)
    parser.add_argument("--from", dest="from_time", required=True, help="Start time (ISO8601)")
    parser.add_argument("--until", dest="until_time", required=True, help="End time (ISO8601)")
    args = parser.parse_args()

    # Load schedule and overrides
    schedule_data = load_json(args.schedule)
    overrides_data = load_json(args.overrides) if args.overrides else []
    start_from = parse_time(args.from_time)
    until = parse_time(args.until_time)
    
    # Parse models
    try:
        schedule = Schedule(**schedule_data)
        overrides = [Entry(**o) for o in overrides_data]
    except ScheduleParsingError as e:
        print(f"Error parsing schedule or overrides: {e}")
        return
    

    # Algorithm
    # 1. generate base entries between 'from' and 'until' depending on 'interval_days' and 'handover_start_at'
    # 2. apply overrides to base entries

    # Generate schedule entries
    base_entries = generate_base_entries(schedule, start_from, until)
    final_entries = apply_overrides(base_entries, overrides)
    output = [e.model_dump() for e in final_entries]

    print(json.dumps(output, indent=2, default=datetime_encoder))
    with open("output.json", "w") as f:
        json.dump(output, f, indent=2, default=datetime_encoder)



if __name__ == "__main__":
    render()
