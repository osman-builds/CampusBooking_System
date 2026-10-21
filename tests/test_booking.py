"""
Comprehensive Automated Unit Test Suite for Campus Facility & Room Booking System.
Automated Unit and Regression Test Suite for Continuous Integration (CI) and TDD:
- Fast execution (< 1 second)
- Isolated unit testing without external database or network dependencies
- Verifies behavioral parity across Codebase A, Codebase B, and Refactored Codebase A
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from codebase_a.booking_system import BookingSystem as MonolithBookingSystem
from codebase_b.models import (
    OperatingHoursExceededError,
    QuotaExceededError,
    Room,
    RoomType,
    SlotConflictError,
    User,
    UserRole,
)
from codebase_b.services import (
    BookingRepository,
    BookingService,
    ConflictDetector,
    PricingService,
)
from refactored_codebase_a.booking_system import (
    BookingSystem as RefactoredBookingSystem,
    PricingCalculator,
)


class TestCodebaseA(unittest.TestCase):
    """Unit tests for Codebase A (Monolith)."""

    def setUp(self):
        self.bs = MonolithBookingSystem()
        self.bs.register_user("U-101", "Alice Johnson", "student", "alice@campus.edu")
        self.bs.register_user("U-102", "Dr. Robert Smith", "faculty", "rsmith@campus.edu")
        self.bs.register_room("R-SR1", "Seminar Room Alpha", "standard", 30)
        self.bs.register_room("R-LB2", "Computer Vision Lab", "lab", 15)

    def test_valid_booking_with_student_discount(self):
        # 2 hrs @ $20 = $40; -15% student discount = $34.00
        booking = self.bs.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
        self.assertIsNotNone(booking)
        self.assertEqual(booking["base_cost"], 40.0)
        self.assertEqual(booking["discount"], 6.0)
        self.assertEqual(booking["total_cost"], 34.0)

    def test_weekend_surcharge_calculation(self):
        # 3 hrs @ $35 = $105; weekend +20% surcharge = $126.00
        booking = self.bs.create_booking("U-102", "R-LB2", "2026-10-17", 14, 17)
        self.assertIsNotNone(booking)
        self.assertEqual(booking["base_cost"], 105.0)
        self.assertEqual(booking["surcharge"], 21.0)
        self.assertEqual(booking["total_cost"], 126.0)

    def test_overlapping_conflict_rejected(self):
        self.bs.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
        conflict = self.bs.create_booking("U-102", "R-SR1", "2026-10-12", 11, 13)
        self.assertIsNone(conflict)

    def test_student_daily_quota_enforced(self):
        self.bs.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)  # 2 hrs used
        over_quota = self.bs.create_booking("U-101", "R-LB2", "2026-10-12", 15, 16)
        self.assertIsNone(over_quota)

    def test_operating_hours_bounds(self):
        early = self.bs.create_booking("U-102", "R-SR1", "2026-10-12", 7, 9)
        self.assertIsNone(early)
        late = self.bs.create_booking("U-102", "R-SR1", "2026-10-12", 21, 23)
        self.assertIsNone(late)

    def test_cancellation_and_rebooking(self):
        b1 = self.bs.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
        self.assertTrue(self.bs.cancel_booking(b1["booking_id"]))
        # Slot should now be available again
        b2 = self.bs.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
        self.assertIsNotNone(b2)


class TestCodebaseB(unittest.TestCase):
    """Unit tests for Codebase B (Clean Architecture)."""

    def setUp(self):
        self.repo = BookingRepository()
        self.pricing = PricingService()
        self.conflict = ConflictDetector()
        self.service = BookingService(self.repo, self.pricing, self.conflict)

        self.user_student = User("U-101", "Alice Johnson", UserRole.STUDENT, "alice@campus.edu")
        self.user_faculty = User("U-102", "Dr. Robert Smith", UserRole.FACULTY, "rsmith@campus.edu")
        self.room_standard = Room("R-SR1", "Seminar Room Alpha", RoomType.STANDARD, 30, 20.0)
        self.room_lab = Room("R-LB2", "Computer Vision Lab", RoomType.LAB, 15, 35.0)

        self.repo.add_user(self.user_student)
        self.repo.add_user(self.user_faculty)
        self.repo.add_room(self.room_standard)
        self.repo.add_room(self.room_lab)

    def test_valid_booking_with_pricing(self):
        res = self.service.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
        self.assertEqual(res.base_cost, 40.0)
        self.assertEqual(res.discount, 6.0)
        self.assertEqual(res.total_cost, 34.0)

    def test_slot_conflict_raises_exception(self):
        self.service.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
        with self.assertRaises(SlotConflictError):
            self.service.create_booking("U-102", "R-SR1", "2026-10-12", 11, 13)

    def test_quota_exceeded_raises_exception(self):
        self.service.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
        with self.assertRaises(QuotaExceededError):
            self.service.create_booking("U-101", "R-LB2", "2026-10-12", 15, 16)

    def test_operating_hours_raises_exception(self):
        with self.assertRaises(OperatingHoursExceededError):
            self.service.create_booking("U-102", "R-SR1", "2026-10-12", 7, 9)

    def test_cancellation_and_rebooking(self):
        b1 = self.service.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
        self.assertTrue(self.service.cancel_booking(b1.booking_id))
        b2 = self.service.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
        self.assertIsNotNone(b2)


class TestRefactoredCodebaseA(unittest.TestCase):
    """Unit tests for Refactored Codebase A."""

    def setUp(self):
        self.bs = RefactoredBookingSystem()
        self.bs.register_user("U-101", "Alice Johnson", "student", "alice@campus.edu")
        self.bs.register_user("U-102", "Dr. Robert Smith", "faculty", "rsmith@campus.edu")
        self.bs.register_room("R-SR1", "Seminar Room Alpha", "standard", 30)
        self.bs.register_room("R-LB2", "Computer Vision Lab", "lab", 15)

    def test_isolated_pricing_calculator(self):
        # Unit test extracted class directly
        res = PricingCalculator.calculate("standard", "student", "2026-10-12", 2)
        self.assertEqual(res.base_cost, 40.0)
        self.assertEqual(res.discount, 6.0)
        self.assertEqual(res.total_cost, 34.0)

    def test_functional_parity(self):
        b1 = self.bs.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
        self.assertIsNotNone(b1)
        self.assertEqual(b1["total_cost"], 34.0)

        # Conflict rejection
        conflict = self.bs.create_booking("U-102", "R-SR1", "2026-10-12", 11, 13)
        self.assertIsNone(conflict)

        # Quota rejection
        quota = self.bs.create_booking("U-101", "R-LB2", "2026-10-12", 15, 16)
        self.assertIsNone(quota)


if __name__ == "__main__":
    unittest.main()
