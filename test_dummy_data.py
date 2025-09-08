#!/usr/bin/env python3
"""Test script to verify that dummy data population includes current day and
3 weeks of data."""

import datetime as dt
import os
import time

from sqlmodel import Session

from src.database import (
    CompiledFormData,
    CompiledFormDataRepository,
    TasksFormData,
    YouthFormData,
    engine,
    populate_dummy_data,
)


def test_dummy_data_timestamps():
    """Test that dummy data includes current day and 3 weeks of
    historical data."""

    # Set the environment variable to enable dummy data population
    os.environ["POPULATEDUMMY"] = "true"

    # Clear existing data first
    with Session(engine) as session:
        # Delete all records in reverse order of dependencies
        session.query(CompiledFormData).delete()
        session.query(TasksFormData).delete()
        session.query(YouthFormData).delete()
        session.commit()

    # Populate dummy data
    populate_dummy_data()

    # Get all compiled entries
    compiled_entries = CompiledFormDataRepository.get_all()

    if not compiled_entries:
        print("❌ No compiled entries found!")
        return False

    print(f"✅ Found {len(compiled_entries)} compiled entries")

    # Calculate current time and time ranges
    current_time = time.time()
    current_day_start = dt.datetime.combine(
        dt.date.today(), dt.time.min
    ).timestamp()
    three_weeks_ago = current_time - (21 * 24 * 60 * 60)

    # Analyze timestamps
    timestamps = [entry.timestamp for entry in compiled_entries]
    timestamps.sort()

    earliest_timestamp = min(timestamps)
    latest_timestamp = max(timestamps)

    print(f"📅 Current time: {dt.datetime.fromtimestamp(current_time)}")
    print(
        f"📅 Current day start: {dt.datetime.fromtimestamp(current_day_start)}"
    )
    print(f"📅 Three weeks ago: {dt.datetime.fromtimestamp(three_weeks_ago)}")
    print(
        f"📅 Earliest entry: {dt.datetime.fromtimestamp(earliest_timestamp)}"
    )
    print(f"📅 Latest entry: {dt.datetime.fromtimestamp(latest_timestamp)}")

    # Check if we have entries for current day
    current_day_entries = [
        entry
        for entry in compiled_entries
        if entry.timestamp >= current_day_start
    ]

    print(f"📊 Entries for current day: {len(current_day_entries)}")

    # Check if data spans approximately 3 weeks
    time_span_days = (latest_timestamp - earliest_timestamp) / (24 * 60 * 60)
    print(f"📊 Data spans {time_span_days:.1f} days")

    # Verify expectations
    success = True

    if len(current_day_entries) == 0:
        print("❌ No entries found for current day!")
        success = False
    else:
        print("✅ Found entries for current day")

    if time_span_days < 20:  # Should span at least 20 days (close to 3 weeks)
        print(
            f"❌ Data spans only {time_span_days:.1f} days, "
            f"expected at least 20 days"
        )
        success = False
    else:
        print(f"✅ Data spans {time_span_days:.1f} days (good coverage)")

    # Show distribution by day
    print("\n📈 Distribution of entries by day:")
    entries_by_day = {}
    for entry in compiled_entries:
        entry_date = dt.datetime.fromtimestamp(entry.timestamp).date()
        entries_by_day[entry_date] = entries_by_day.get(entry_date, 0) + 1

    # Sort by date and show last 7 days
    sorted_dates = sorted(entries_by_day.keys(), reverse=True)[:7]
    for date in sorted_dates:
        count = entries_by_day[date]
        print(f"  {date}: {count} entries")

    return success


if __name__ == "__main__":
    print(
        "🧪 Testing dummy data population with current day and "
        "3 weeks coverage..."
    )
    success = test_dummy_data_timestamps()

    if success:
        print(
            "\n🎉 All tests passed! Dummy data includes current day and "
            "3 weeks of historical data."
        )
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
        exit(1)
