"""
Campus Facility & Room Booking System - CR-02 (Adaptive Maintenance)
Module: main.py - Verification Entry Point for SQLite3 DBMS Durability & UTC+08:00 Timestamps
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models import Room, RoomType, SlotConflictError, User, UserRole
from services import (
    BookingService,
    ConflictDetector,
    PricingService,
    SQLiteBookingRepository,
)


def main():
    print("=== Campus Room Booking System (CR-02: Adaptive Maintenance - SQLite3 & UTC+08:00) ===")

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = Path(tmp_dir) / "campus_booking_prod.sqlite3"

        print(f"\n--- Session 1: Initializing SQLite3 Database ({db_file.name}) & Creating Booking ---")
        with SQLiteBookingRepository(db_file) as repo_session_1:
            service_1 = BookingService(repo=repo_session_1, pricing=PricingService(), conflict=ConflictDetector())
            repo_session_1.add_user(User("U-101", "Alice Johnson", UserRole.STUDENT, "alice@campus.edu"))
            repo_session_1.add_user(User("U-102", "Dr. Robert Smith", UserRole.FACULTY, "rsmith@campus.edu"))
            repo_session_1.add_room(Room("R-SR1", "Seminar Room Alpha", RoomType.STANDARD, 30, 20.0))
            repo_session_1.add_room(Room("R-LB2", "Computer Vision Lab", RoomType.LAB, 15, 35.0))

            saved = service_1.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
            saved_id = saved.booking_id
            print(f"[SESSION 1 CLOSED] Persisted Booking #{saved_id} to disk; simulating container restart...")

        print("\n--- Session 2: New Process Reconnecting to Existing SQLite3 Database ---")
        with SQLiteBookingRepository(db_file) as repo_session_2:
            service_2 = BookingService(repo=repo_session_2, pricing=PricingService(), conflict=ConflictDetector())
            recovered = repo_session_2.get_reservation(saved_id)
            assert recovered is not None
            print(
                f"[RECOVERED] Booking #{recovered.booking_id} | Token: {recovered.token}"
                f" | TZ: {recovered.created_at.tzname()} ({recovered.created_at.isoformat()})"
            )

            print("\n--- Verifying Cross-Restart Collision Detection Against SQLite3 State ---")
            try:
                service_2.create_booking("U-102", "R-SR1", "2026-10-12", 11, 13)
            except SlotConflictError as e:
                print(f"[CAUGHT SlotConflictError Across Restart] {e}")

            print("\n--- Verifying Persistent Cancellation & Slot Reclamation ---")
            service_2.cancel_booking(saved_id)
            service_2.create_booking("U-102", "R-SR1", "2026-10-12", 11, 13)


if __name__ == "__main__":
    main()
