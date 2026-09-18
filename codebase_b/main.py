"""
Entry Point / Demonstration Script for Campus Booking System (Codebase B).
Demonstrates Clean Architecture, SOLID principles, and Dependency Injection.
"""

import sys
from datetime import datetime, time
from pathlib import Path

# Add current directory to path for direct execution
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from booking_service import BookingService
from conflict_detector import ConflictDetector
from exceptions import (
    BookingException,
    OperatingHoursExceededError,
    QuotaExceededError,
    ResourceNotFoundError,
    SlotConflictError,
)
from models import Room, RoomType, User, UserRole
from notification_service import InMemoryNotificationService
from pricing_service import PricingService
from repository import (
    InMemoryBookingRepository,
    InMemoryRoomRepository,
    InMemoryUserRepository,
)


def print_section(title: str) -> None:
    print(f"\n{'=' * 70}\n  {title}\n{'=' * 70}")


def main() -> None:
    print_section("Campus Facility & Room Booking Engine (Codebase B - Clean Architecture)")

    # -------------------------------------------------------------------------
    # 1. Composition Root: Dependency Injection Setup
    # -------------------------------------------------------------------------
    print("\n[SETUP] Initializing repositories and domain services...")
    booking_repo = InMemoryBookingRepository()
    room_repo = InMemoryRoomRepository()
    user_repo = InMemoryUserRepository()

    conflict_detector = ConflictDetector()
    pricing_service = PricingService()
    notification_service = InMemoryNotificationService()

    # Inject all dependencies into the Application Service
    booking_service = BookingService(
        booking_repo=booking_repo,
        room_repo=room_repo,
        user_repo=user_repo,
        conflict_detector=conflict_detector,
        pricing_service=pricing_service,
        notification_service=notification_service,
    )
    print("[SETUP] Application service wired successfully via Dependency Injection.")

    # -------------------------------------------------------------------------
    # 2. Seed Master Data (Users & Rooms)
    # -------------------------------------------------------------------------
    print_section("1. Registering Users & Rooms")

    user_student = User(
        user_id="U-101",
        name="Alice Johnson",
        role=UserRole.STUDENT,
        email="alice@campus.edu",
    )
    user_staff = User(
        user_id="U-102",
        name="Dr. Robert Smith",
        role=UserRole.STAFF,
        email="rsmith@campus.edu",
    )
    user_repo.save(user_student)
    user_repo.save(user_staff)
    print(f"[SEEDED] User: {user_student.name} ({user_student.role.value}) - ID: {user_student.user_id}")
    print(f"[SEEDED] User: {user_staff.name} ({user_staff.role.value}) - ID: {user_staff.user_id}")

    room_standard = Room(
        room_id="R-SR1",
        name="Seminar Room Alpha",
        room_type=RoomType.STANDARD,
        capacity=30,
        base_hourly_rate=20.0,
    )
    room_lab = Room(
        room_id="R-LB2",
        name="Computer Vision Lab",
        room_type=RoomType.LAB,
        capacity=15,
        base_hourly_rate=35.0,
    )
    room_repo.save(room_standard)
    room_repo.save(room_lab)
    print(f"[SEEDED] Room: {room_standard.name} ({room_standard.room_type.value}) - Rate: ${room_standard.base_hourly_rate}/hr")
    print(f"[SEEDED] Room: {room_lab.name} ({room_lab.room_type.value}) - Rate: ${room_lab.base_hourly_rate}/hr")

    # -------------------------------------------------------------------------
    # 3. Executing Valid Sample Bookings
    # -------------------------------------------------------------------------
    print_section("2. Executing Valid Bookings")

    # Booking 1: Student Alice Johnson books Seminar Room Alpha on a weekday (2 hrs)
    # Base: 2 * $20 = $40. 15% student discount -> $34.00
    print("\n--- Request 1: Student Weekday Booking (Discount Policy Applied) ---")
    b1 = booking_service.create_booking(
        user_id="U-101",
        room_id="R-SR1",
        start_time=datetime(2026, 10, 12, 10, 0),  # Monday (Weekday)
        end_time=datetime(2026, 10, 12, 12, 0),
    )
    print(f"[SUCCESS] Created Booking #{b1.id} (Token: {b1.confirmation_token}) - Charged: ${b1.total_cost:.2f}")

    # Booking 2: Staff Dr. Robert Smith books Computer Vision Lab on a weekend (3 hrs)
    # Base: 3 * $35 = $105. 20% weekend peak surcharge -> $126.00
    print("\n--- Request 2: Staff Weekend Booking (Peak Surcharge Applied) ---")
    b2 = booking_service.create_booking(
        user_id="U-102",
        room_id="R-LB2",
        start_time=datetime(2026, 10, 17, 14, 0),  # Saturday (Weekend)
        end_time=datetime(2026, 10, 17, 17, 0),
    )
    print(f"[SUCCESS] Created Booking #{b2.id} (Token: {b2.confirmation_token}) - Charged: ${b2.total_cost:.2f}")

    # -------------------------------------------------------------------------
    # 4. Triggering & Handling Domain Exceptions
    # -------------------------------------------------------------------------
    print_section("3. Expected Exception Handling (Policy & Conflict Enforcement)")

    # Test Case A: Time Slot Collision
    print("\n[TEST A] Attempting overlapping booking for Seminar Room Alpha (11:00 - 13:00)...")
    try:
        booking_service.create_booking(
            user_id="U-102",
            room_id="R-SR1",
            start_time=datetime(2026, 10, 12, 11, 0),
            end_time=datetime(2026, 10, 12, 13, 0),
        )
    except SlotConflictError as ex:
        print(f"  --> CAUGHT SlotConflictError as expected: {ex}")

    # Test Case B: Student Daily Quota Violation (Max 2 hours/day)
    print("\n[TEST B] Student Alice Johnson attempts booking another hour on same day (15:00 - 16:00)...")
    try:
        booking_service.create_booking(
            user_id="U-101",
            room_id="R-LB2",
            start_time=datetime(2026, 10, 12, 15, 0),
            end_time=datetime(2026, 10, 12, 16, 0),
        )
    except QuotaExceededError as ex:
        print(f"  --> CAUGHT QuotaExceededError as expected: {ex}")

    # Test Case C: Outside Operating Hours (Operating bounds: 08:00 - 22:00)
    print("\n[TEST C] Attempting out-of-bounds booking (06:00 - 08:00)...")
    try:
        booking_service.create_booking(
            user_id="U-102",
            room_id="R-SR1",
            start_time=datetime(2026, 10, 12, 6, 0),
            end_time=datetime(2026, 10, 12, 8, 0),
        )
    except OperatingHoursExceededError as ex:
        print(f"  --> CAUGHT OperatingHoursExceededError as expected: {ex}")

    # -------------------------------------------------------------------------
    # 5. Cancellation & Slot Reclaim Flow
    # -------------------------------------------------------------------------
    print_section("4. Cancellation Lifecycle & Slot Reclaim")

    print(f"\n[ACTION] Cancelling Booking #{b1.id}...")
    cancelled_booking = booking_service.cancel_booking(b1.id)
    print(f"[SUCCESS] Booking #{cancelled_booking.id} status is now {cancelled_booking.status.value}")

    print("\n[ACTION] Student Alice Johnson re-books the vacated slot after cancellation...")
    b3 = booking_service.create_booking(
        user_id="U-101",
        room_id="R-SR1",
        start_time=datetime(2026, 10, 12, 10, 0),
        end_time=datetime(2026, 10, 12, 12, 0),
    )
    print(f"[SUCCESS] Successfully re-booked slot as Booking #{b3.id} (Token: {b3.confirmation_token})")

    # -------------------------------------------------------------------------
    # 6. Final State Inspection
    # -------------------------------------------------------------------------
    print_section("5. Final System State Summary")

    print("\n[REGISTERED ROOMS]")
    for r in room_repo.find_all():
        print(f"  * {r.room_id}: {r.name:<22} Type: {r.room_type.value:<10} Rate: ${r.base_hourly_rate:<5.2f} Cap: {r.capacity}")

    print("\n[RECORDED RESERVATIONS IN REPOSITORY]")
    for res in booking_repo.find_all():
        time_str = f"{res.start_time.strftime('%Y-%m-%d %H:%M')} -> {res.end_time.strftime('%H:%M')}"
        print(f"  * #{res.id:<2} | Token: {res.confirmation_token:<24} | User: {res.user_id} | Room: {res.room_id} | {time_str} | ${res.total_cost:<6.2f} | Status: {res.status.value}")

    print(f"\n[AUDIT LOG: DISPATCHED NOTIFICATIONS] (Total: {len(notification_service.sent_notifications)})")
    for idx, notif in enumerate(notification_service.sent_notifications, 1):
        print(f"  {idx}. [{notif.event_type}] Token: {notif.confirmation_token} to {notif.user_name} ({notif.user_email})")

    print_section("Demonstration Completed Successfully")


if __name__ == "__main__":
    main()
