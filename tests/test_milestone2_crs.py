"""
Automated Unit & Regression Test Suite for CSEB5213 Milestone 2 Change Requests (CR-01, CR-02, CR-03).

Verifies:
- CR-01 (Corrective): Canonical ISO-8601 date normalization blocking double-booking & quota bypasses,
  19-char token integrity, domain InvalidDateError containment, and strict integer-hour enforcement.
- CR-02 (Adaptive): SQLite3 relational DBMS persistence across connection restarts, parameterized SQL
  safety, Dependency Inversion (DIP) repository substitutability, and UTC+08:00 timezone timestamps.
- CR-03 (Perfective): Room.capacity attendee validation, best-fit available room discovery,
  SilentNotificationService stdout decoupling (SRP), and O(1) composite-key repository indexing.
"""

import contextlib
import datetime
import io
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cr1_corrective import (
    BookingException as CR1BookingException,
    BookingRepository as CR1Repository,
    BookingService as CR1BookingService,
    ConflictDetector as CR1ConflictDetector,
    InvalidDateError,
    InvalidTimeSlotError,
    PricingService as CR1PricingService,
    QuotaExceededError as CR1QuotaExceededError,
    Room as CR1Room,
    RoomType as CR1RoomType,
    SlotConflictError as CR1SlotConflictError,
    User as CR1User,
    UserRole as CR1UserRole,
)
from cr2_adaptive import (
    BookingService as CR2BookingService,
    ConflictDetector as CR2ConflictDetector,
    InMemoryBookingRepository as CR2InMemoryRepository,
    PricingService as CR2PricingService,
    Room as CR2Room,
    RoomType as CR2RoomType,
    SlotConflictError as CR2SlotConflictError,
    SQLiteBookingRepository,
    User as CR2User,
    UserRole as CR2UserRole,
)
from cr3_perfective import (
    BookingRepository as CR3Repository,
    BookingService as CR3BookingService,
    CapacityExceededError,
    ConflictDetector as CR3ConflictDetector,
    PricingService as CR3PricingService,
    Room as CR3Room,
    RoomType as CR3RoomType,
    SilentNotificationService,
    User as CR3User,
    UserRole as CR3UserRole,
)


class TestCR1CorrectiveMaintenance(unittest.TestCase):
    """Verification tests for CR-01 (Corrective Maintenance)."""

    def setUp(self):
        self.repo = CR1Repository()
        self.service = CR1BookingService(self.repo, CR1PricingService(), CR1ConflictDetector())
        self.repo.add_user(CR1User("U-101", "Alice Johnson", CR1UserRole.STUDENT, "alice@campus.edu"))
        self.repo.add_user(CR1User("U-102", "Dr. Robert Smith", CR1UserRole.FACULTY, "rsmith@campus.edu"))
        self.repo.add_room(CR1Room("R-SR1", "Seminar Room Alpha", CR1RoomType.STANDARD, 30, 20.0))
        self.repo.add_room(CR1Room("R-LB2", "Computer Vision Lab", CR1RoomType.LAB, 15, 35.0))

    def test_canonical_date_prevents_double_booking_and_fixes_token(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = self.service.create_booking("U-101", "R-SR1", "2026-1-5", 10, 12)
        self.assertEqual(res.date_str, "2026-01-05")
        self.assertEqual(len(res.token), 19)
        self.assertTrue(res.token.startswith("SKD-20260105-"))

        for variant in ("2026-01-05", "2026-01-5", "2026-1-05", " 2026-1-5 "):
            with self.assertRaises(CR1SlotConflictError):
                self.service.create_booking("U-102", "R-SR1", variant, 11, 13)

    def test_canonical_date_prevents_student_quota_bypass(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.service.create_booking("U-101", "R-SR1", "2026-1-5", 10, 12)  # 2 hrs used
        with self.assertRaises(CR1QuotaExceededError):
            self.service.create_booking("U-101", "R-LB2", "2026-01-05", 14, 15)

    def test_invalid_calendar_dates_raise_domain_exception(self):
        for bad_date in ("2026-02-30", "12/10/2026", "2026-13-01", "", "   ", None):
            with self.assertRaises(InvalidDateError) as ctx:
                self.service.create_booking("U-102", "R-SR1", bad_date, 10, 12)  # type: ignore[arg-type]
            self.assertIsInstance(ctx.exception, CR1BookingException)

    def test_non_integer_hours_rejected_without_phantom_persistence(self):
        for bad_start, bad_end in ((10.5, 12), (10, 12.5), (True, 10), (9, False), ("10", 12)):
            with self.assertRaises(InvalidTimeSlotError):
                self.service.create_booking("U-102", "R-SR1", "2026-01-06", bad_start, bad_end)  # type: ignore[arg-type]
        self.assertEqual(len(self.repo.find_by_room_and_date("R-SR1", "2026-01-06")), 0)


class TestCR2AdaptiveMaintenance(unittest.TestCase):
    """Verification tests for CR-02 (Adaptive Maintenance)."""

    def test_sqlite_file_durability_across_restarts(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test_campus.sqlite3"

            with SQLiteBookingRepository(db_path) as repo1:
                svc1 = CR2BookingService(repo1, CR2PricingService(), CR2ConflictDetector())
                repo1.add_user(CR2User("U-101", "Alice Johnson", CR2UserRole.STUDENT))
                repo1.add_user(CR2User("U-102", "Dr. Robert Smith", CR2UserRole.FACULTY))
                repo1.add_room(CR2Room("R-SR1", "Seminar Room Alpha", CR2RoomType.STANDARD, 30, 20.0))

                with contextlib.redirect_stdout(io.StringIO()):
                    created = svc1.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
                booking_id = created.booking_id

            # Reconnect in a fresh repository session simulating container restart
            with SQLiteBookingRepository(db_path) as repo2:
                svc2 = CR2BookingService(repo2, CR2PricingService(), CR2ConflictDetector())
                recovered = repo2.get_reservation(booking_id)
                self.assertIsNotNone(recovered)
                assert recovered is not None
                self.assertEqual(recovered.total_cost, 34.0)
                self.assertEqual(recovered.created_at.utcoffset(), datetime.timedelta(hours=8))

                # Persisted reservation must enforce conflict detection in new session
                with self.assertRaises(CR2SlotConflictError):
                    svc2.create_booking("U-102", "R-SR1", "2026-10-12", 11, 13)

                # Persisted cancellation must free slot across sessions
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertTrue(svc2.cancel_booking(booking_id))
                    rebooked = svc2.create_booking("U-102", "R-SR1", "2026-10-12", 11, 13)
                self.assertEqual(rebooked.total_cost, 40.0)

    def test_parameterized_sql_injection_safety(self):
        with SQLiteBookingRepository(":memory:") as repo:
            malicious_id = "U-999'; DROP TABLE reservations; --"
            repo.add_user(CR2User(malicious_id, "Sec Audit", CR2UserRole.STAFF))
            fetched = repo.get_user(malicious_id)
            self.assertIsNotNone(fetched)
            self.assertEqual(repo.find_by_user_and_date(malicious_id, "2026-10-12"), [])

    def test_dip_parity_between_inmemory_and_sqlite_adapters(self):
        mem_repo = CR2InMemoryRepository()
        with SQLiteBookingRepository(":memory:") as sql_repo:
            for repo in (mem_repo, sql_repo):
                repo.add_user(CR2User("U-101", "Alice", CR2UserRole.STUDENT))
                repo.add_room(CR2Room("R-LB2", "Vision Lab", CR2RoomType.LAB, 15, 35.0))

            svc_mem = CR2BookingService(mem_repo, CR2PricingService(), CR2ConflictDetector())
            svc_sql = CR2BookingService(sql_repo, CR2PricingService(), CR2ConflictDetector())

            with contextlib.redirect_stdout(io.StringIO()):
                r_mem = svc_mem.create_booking("U-101", "R-LB2", "2026-10-17", 10, 12)
                r_sql = svc_sql.create_booking("U-101", "R-LB2", "2026-10-17", 10, 12)

            self.assertEqual(r_mem.total_cost, r_sql.total_cost)
            self.assertEqual(r_mem.created_at.utcoffset(), datetime.timedelta(hours=8))
            self.assertEqual(r_sql.created_at.utcoffset(), datetime.timedelta(hours=8))


class TestCR3PerfectiveMaintenance(unittest.TestCase):
    """Verification tests for CR-03 (Perfective Maintenance)."""

    def setUp(self):
        self.repo = CR3Repository()
        self.service = CR3BookingService(
            repo=self.repo,
            pricing=CR3PricingService(),
            conflict=CR3ConflictDetector(),
            notifier=SilentNotificationService(),
        )
        self.repo.add_user(CR3User("U-101", "Alice Johnson", CR3UserRole.STUDENT))
        self.repo.add_user(CR3User("U-102", "Dr. Robert Smith", CR3UserRole.FACULTY))
        self.repo.add_room(CR3Room("R-ST1", "Media Pod Studio", CR3RoomType.STUDIO, 8, 35.0))
        self.repo.add_room(CR3Room("R-LB2", "Computer Vision Lab", CR3RoomType.LAB, 15, 35.0))
        self.repo.add_room(CR3Room("R-SR1", "Seminar Room Alpha", CR3RoomType.STANDARD, 30, 20.0))

    def test_attendee_capacity_validation_and_default_compatibility(self):
        # Default attendees=1 works without breaking existing 5-arg callers
        b_default = self.service.create_booking("U-101", "R-ST1", "2026-10-12", 10, 11)
        self.assertEqual(b_default.attendees, 1)

        # Exceeding capacity or < 1 attendee raises CapacityExceededError
        with self.assertRaises(CapacityExceededError):
            self.service.create_booking("U-102", "R-LB2", "2026-10-12", 14, 16, attendees=16)
        with self.assertRaises(CapacityExceededError):
            self.service.create_booking("U-102", "R-LB2", "2026-10-12", 14, 16, attendees=0)

    def test_smart_available_room_discovery_and_best_fit_sorting(self):
        # Book R-LB2 (15 seats) for 10:00-12:00
        b1 = self.service.create_booking("U-102", "R-LB2", "2026-10-12", 10, 12, attendees=12)

        # Query >= 10 seats for 10:00-12:00: R-ST1 (8 seats) & R-LB2 (occupied) excluded -> only R-SR1
        avail = self.service.find_available_rooms("2026-10-12", 10, 12, min_capacity=10)
        self.assertEqual([r.room_id for r in avail], ["R-SR1"])

        # Cancel R-LB2 -> now both R-LB2 (15) and R-SR1 (30) returned in best-fit capacity order
        self.service.cancel_booking(b1.booking_id)
        avail_after = self.service.find_available_rooms("2026-10-12", 10, 12, min_capacity=10)
        self.assertEqual([r.room_id for r in avail_after], ["R-LB2", "R-SR1"])

        # Optional room_type filter
        labs_only = self.service.find_available_rooms(
            "2026-10-12", 10, 12, min_capacity=10, room_type=CR3RoomType.LAB
        )
        self.assertEqual([r.room_id for r in labs_only], ["R-LB2"])

    def test_silent_notifier_produces_zero_stdout_and_o1_index_scales(self):
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            for day_offset in range(120):
                d = (datetime.date(2026, 1, 1) + datetime.timedelta(days=day_offset)).isoformat()
                self.service.create_booking("U-102", "R-SR1", d, 9, 11, attendees=20)
        self.assertEqual(captured.getvalue(), "")
        self.assertEqual(len(self.repo.find_by_room_and_date("R-SR1", "2026-01-15")), 1)
        self.assertEqual(len(self.repo.find_by_room_and_date("R-SR1", "2026-12-31")), 0)


if __name__ == "__main__":
    unittest.main()
