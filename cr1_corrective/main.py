"""
Campus Facility & Room Booking System — CR-01 (Corrective Maintenance)
Module: main.py - Verification Entry Point for Date Normalization & Boundary Defect Fixes
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models import (
    InvalidDateError,
    InvalidTimeSlotError,
    QuotaExceededError,
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
    print("=== Campus Room Booking System (CR-01: Corrective Maintenance) ===")

    repo = BookingRepository()
    service = BookingService(repo=repo, pricing=PricingService(), conflict=ConflictDetector())

    repo.add_user(User("U-101", "Alice Johnson", UserRole.STUDENT, "alice@campus.edu"))
    repo.add_user(User("U-102", "Dr. Robert Smith", UserRole.FACULTY, "rsmith@campus.edu"))
    repo.add_room(Room("R-SR1", "Seminar Room Alpha", RoomType.STANDARD, 30, 20.0))
    repo.add_room(Room("R-LB2", "Computer Vision Lab", RoomType.LAB, 15, 35.0))

    print("\n--- 1. Non-Padded Date Canonicalization ('2026-1-5' -> '2026-01-05') ---")
    res = service.create_booking("U-101", "R-SR1", "2026-1-5", 10, 12)
    print(f"[VERIFIED] Stored Canonical Date: {res.date_str} | Token Length: {len(res.token)} ({res.token})")

    print("\n--- 2. Double-Booking Bypass Blocked ('2026-01-05' collides with '2026-1-5') ---")
    try:
        service.create_booking("U-102", "R-SR1", "2026-01-05", 11, 13)
    except SlotConflictError as e:
        print(f"[BLOCKED SlotConflictError] {e}")

    print("\n--- 3. Student Quota Bypass Blocked ('2026-01-5' counted against '2026-1-5') ---")
    try:
        service.create_booking("U-101", "R-LB2", "2026-01-5", 14, 15)
    except QuotaExceededError as e:
        print(f"[BLOCKED QuotaExceededError] {e}")

    print("\n--- 4. Malformed Calendar Date Contained via InvalidDateError ---")
    try:
        service.create_booking("U-102", "R-LB2", "2026-02-30", 14, 16)
    except InvalidDateError as e:
        print(f"[CAUGHT InvalidDateError] {e}")

    print("\n--- 5. Float & Boolean Hour Inputs Rejected Before Persistence ---")
    try:
        service.create_booking("U-102", "R-LB2", "2026-01-06", 10.5, 12)  # type: ignore[arg-type]
    except InvalidTimeSlotError as e:
        print(f"[CAUGHT InvalidTimeSlotError] {e}")


if __name__ == "__main__":
    main()
