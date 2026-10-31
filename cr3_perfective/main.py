"""
Campus Facility & Room Booking System - CR-03 (Perfective Maintenance)
Module: main.py - Verification Entry Point for Capacity Bounds, Room Search & O(1) Indexing
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models import CapacityExceededError, Room, RoomType, User, UserRole
from services import (
    BookingRepository,
    BookingService,
    ConflictDetector,
    ConsoleNotificationService,
    PricingService,
)


def main():
    print("=== Campus Room Booking System (CR-03: Perfective Maintenance) ===")

    repo = BookingRepository()
    service = BookingService(
        repo=repo,
        pricing=PricingService(),
        conflict=ConflictDetector(),
        notifier=ConsoleNotificationService(),
    )

    repo.add_user(User("U-101", "Alice Johnson", UserRole.STUDENT, "alice@campus.edu"))
    repo.add_user(User("U-102", "Dr. Robert Smith", UserRole.FACULTY, "rsmith@campus.edu"))
    repo.add_room(Room("R-ST1", "Media Pod Studio", RoomType.STUDIO, 8, 35.0))
    repo.add_room(Room("R-LB2", "Computer Vision Lab", RoomType.LAB, 15, 35.0))
    repo.add_room(Room("R-SR1", "Seminar Room Alpha", RoomType.STANDARD, 30, 20.0))

    print("\n--- 1. Valid Booking with Attendee Headcount Verification ---")
    service.create_booking("U-101", "R-LB2", "2026-10-12", 10, 12, attendees=12)

    print("--- 2. Room Capacity Safety Enforcement (20 attendees > 15-seat Lab) ---")
    try:
        service.create_booking("U-102", "R-LB2", "2026-10-12", 14, 16, attendees=20)
    except CapacityExceededError as e:
        print(f"[CAUGHT CapacityExceededError] {e}")

    print("\n--- 3. Smart Best-Fit Room Availability Discovery (10:00-12:00, >= 10 seats) ---")
    available = service.find_available_rooms("2026-10-12", 10, 12, min_capacity=10)
    for r in available:
        print(f"  [AVAILABLE] {r.room_id}: {r.name} ({r.room_type.value}, Cap: {r.capacity}, ${r.hourly_rate:.2f}/hr)")


if __name__ == "__main__":
    main()
