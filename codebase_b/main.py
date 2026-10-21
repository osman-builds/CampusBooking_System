"""
Campus Facility & Room Booking System (Codebase B)
Module: main.py - Demonstration Entry Point

Showcases Clean Architecture, SOLID separation of concerns, and explicit domain exception handling.
"""

import sys
from pathlib import Path

# Add parent/current directory for clean relative imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models import (
    BookingException,
    OperatingHoursExceededError,
    QuotaExceededError,
    ResourceNotFoundError,
    Room,
    RoomType,
    SlotConflictError,
    User,
    UserRole,
)
from services import (
    BookingRepository,
    BookingService,
    ConflictDetector,
    PricingService,
)


def main():
    print("=== Campus Room Booking System (Codebase B: Clean Architecture) ===")

    # 1. Dependency Injection Setup
    repo = BookingRepository()
    pricing = PricingService()
    conflict = ConflictDetector()
    service = BookingService(repo=repo, pricing=pricing, conflict=conflict)

    # 2. Seed Users & Rooms
    alice = User("U-101", "Alice Johnson", UserRole.STUDENT, "alice@campus.edu")
    robert = User("U-102", "Dr. Robert Smith", UserRole.FACULTY, "rsmith@campus.edu")
    seminar_room = Room("R-SR1", "Seminar Room Alpha", RoomType.STANDARD, 30, 20.0)
    vision_lab = Room("R-LB2", "Computer Vision Lab", RoomType.LAB, 15, 35.0)

    repo.add_user(alice)
    repo.add_user(robert)
    repo.add_room(seminar_room)
    repo.add_room(vision_lab)

    print(f"[SEEDED] Users: {alice.name} ({alice.role.value}), {robert.name} ({robert.role.value})")
    print(f"[SEEDED] Rooms: {seminar_room.name} (${seminar_room.hourly_rate}/hr), {vision_lab.name} (${vision_lab.hourly_rate}/hr)")

    print("\n--- 1. Valid Bookings ---")
    service.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)  # Weekday Student: $40 - 15% = $34.00
    service.create_booking("U-102", "R-LB2", "2026-10-17", 14, 17)  # Weekend Faculty: $105 + 20% = $126.00

    print("--- 2. Schedule Conflict Test ---")
    try:
        service.create_booking("U-102", "R-SR1", "2026-10-12", 11, 13)
    except SlotConflictError as e:
        print(f"[CAUGHT SlotConflictError] {e}")

    print("\n--- 3. Student Daily Quota Test ---")
    try:
        service.create_booking("U-101", "R-LB2", "2026-10-12", 15, 16)
    except QuotaExceededError as e:
        print(f"[CAUGHT QuotaExceededError] {e}")

    print("\n--- 4. Operating Bounds Test ---")
    try:
        service.create_booking("U-102", "R-SR1", "2026-10-12", 7, 9)
    except OperatingHoursExceededError as e:
        print(f"[CAUGHT OperatingHoursExceededError] {e}")

    print("\n--- 5. Cancellation & Re-booking ---")
    service.cancel_booking(1)
    service.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)


if __name__ == "__main__":
    main()
