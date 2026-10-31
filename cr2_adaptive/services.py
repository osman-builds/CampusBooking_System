"""
Campus Facility & Room Booking System - CR-02 (Adaptive Maintenance)
Module: services.py - Abstract Repository Port & SQLite3 Relational DBMS Adapter

Adapts Codebase B to a Stateless Containerized Server & Relational DBMS Environment:
1. AbstractBookingRepository (ABC): Formalizes the Dependency Inversion Principle (DIP) port
   so BookingService remains 100% agnostic of the storage technology.
2. SQLiteBookingRepository: Built-in Python sqlite3 relational adapter providing ACID
   transactions, foreign-key enforcement, composite SQL indexes, parameterized queries
   (preventing SQL injection), and ISO-8601 UTC+08:00 timestamp round-tripping.
3. InMemoryBookingRepository: Retained as a lightweight adapter for isolated unit tests.
"""

import datetime
import secrets
import sqlite3
import string
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    from .models import (
        CAMPUS_TIMEZONE,
        BookingException,
        OperatingHoursExceededError,
        QuotaExceededError,
        Reservation,
        ReservationStatus,
        ResourceNotFoundError,
        Room,
        RoomType,
        SlotConflictError,
        StoragePersistenceError,
        User,
        UserRole,
    )
except ImportError:
    from models import (
        CAMPUS_TIMEZONE,
        BookingException,
        OperatingHoursExceededError,
        QuotaExceededError,
        Reservation,
        ReservationStatus,
        ResourceNotFoundError,
        Room,
        RoomType,
        SlotConflictError,
        StoragePersistenceError,
        User,
        UserRole,
    )


@dataclass(frozen=True)
class PricingBreakdown:
    duration: int
    hourly_rate: float
    base_cost: float
    discount: float
    surcharge: float
    total_cost: float


class PricingService:
    """Encapsulates all financial and rate calculation rules."""

    STUDENT_DISCOUNT: float = 0.15
    WEEKEND_SURCHARGE: float = 0.20

    def calculate(self, room: Room, user: User, date_str: str, duration: int) -> PricingBreakdown:
        booking_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        is_weekend = booking_date.weekday() >= 5

        base_cost = round(duration * room.hourly_rate, 2)
        discount = round(base_cost * self.STUDENT_DISCOUNT, 2) if user.is_student() else 0.0
        subtotal = round(base_cost - discount, 2)
        surcharge = round(subtotal * self.WEEKEND_SURCHARGE, 2) if is_weekend else 0.0
        total_cost = round(subtotal + surcharge, 2)

        return PricingBreakdown(
            duration=duration,
            hourly_rate=room.hourly_rate,
            base_cost=base_cost,
            discount=discount,
            surcharge=surcharge,
            total_cost=total_cost,
        )


class ConflictDetector:
    """Encapsulates schedule collision and quota validation rules."""

    @staticmethod
    def has_overlap(existing_reservations: List[Reservation], start: int, end: int) -> bool:
        """Determines if [start, end) intersects with any active reservation."""
        for r in existing_reservations:
            if r.is_active and max(start, r.start_hour) < min(end, r.end_hour):
                return True
        return False

    @staticmethod
    def exceeds_daily_quota(user_reservations: List[Reservation], new_duration: int, limit: int = 2) -> bool:
        """Checks if active bookings for user on that day + new_duration exceed the daily limit."""
        booked = sum(r.duration for r in user_reservations if r.is_active)
        return (booked + new_duration) > limit


class AbstractBookingRepository(ABC):
    """Port interface decoupling domain orchestration from underlying storage environments."""

    @abstractmethod
    def add_user(self, user: User) -> None:
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def add_room(self, room: Room) -> None:
        pass

    @abstractmethod
    def get_room(self, room_id: str) -> Optional[Room]:
        pass

    @abstractmethod
    def save_reservation(self, res: Reservation) -> Reservation:
        pass

    @abstractmethod
    def get_reservation(self, booking_id: int) -> Optional[Reservation]:
        pass

    @abstractmethod
    def find_by_room_and_date(self, room_id: str, date_str: str) -> List[Reservation]:
        pass

    @abstractmethod
    def find_by_user_and_date(self, user_id: str, date_str: str) -> List[Reservation]:
        pass


class InMemoryBookingRepository(AbstractBookingRepository):
    """Volatile in-memory repository adapter retained for ultra-fast unit testing."""

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._rooms: Dict[str, Room] = {}
        self._reservations: Dict[int, Reservation] = {}
        self._seq = 1

    def add_user(self, user: User) -> None:
        self._users[user.user_id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def add_room(self, room: Room) -> None:
        self._rooms[room.room_id] = room

    def get_room(self, room_id: str) -> Optional[Room]:
        return self._rooms.get(room_id)

    def save_reservation(self, res: Reservation) -> Reservation:
        if res.booking_id <= 0:
            res.booking_id = self._seq
            self._seq += 1
        self._reservations[res.booking_id] = res
        return res

    def get_reservation(self, booking_id: int) -> Optional[Reservation]:
        return self._reservations.get(booking_id)

    def find_by_room_and_date(self, room_id: str, date_str: str) -> List[Reservation]:
        return [r for r in self._reservations.values() if r.room_id == room_id and r.date_str == date_str]

    def find_by_user_and_date(self, user_id: str, date_str: str) -> List[Reservation]:
        return [r for r in self._reservations.values() if r.user_id == user_id and r.date_str == date_str]


# Backward-compatible alias
BookingRepository = InMemoryBookingRepository


class SQLiteBookingRepository(AbstractBookingRepository):
    """
    Persistent SQLite3 relational DBMS adapter for stateless server/container deployments.
    Uses Python's standard library sqlite3 with ACID transactions and parameterized SQL.
    """

    def __init__(self, db_path: Union[str, Path] = ":memory:"):
        self.db_path = str(db_path)
        try:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON;")
            self._init_schema()
        except sqlite3.Error as exc:
            raise StoragePersistenceError(f"Failed to initialize SQLite database '{self.db_path}': {exc}") from exc

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT NOT NULL DEFAULT '',
                    is_active INTEGER NOT NULL DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS rooms (
                    room_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    room_type TEXT NOT NULL,
                    capacity INTEGER NOT NULL,
                    hourly_rate REAL NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS reservations (
                    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT NOT NULL UNIQUE,
                    user_id TEXT NOT NULL,
                    room_id TEXT NOT NULL,
                    date_str TEXT NOT NULL,
                    start_hour INTEGER NOT NULL,
                    end_hour INTEGER NOT NULL,
                    base_cost REAL NOT NULL,
                    discount REAL NOT NULL,
                    surcharge REAL NOT NULL,
                    total_cost REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
                );

                CREATE INDEX IF NOT EXISTS idx_res_room_date
                    ON reservations(room_id, date_str);

                CREATE INDEX IF NOT EXISTS idx_res_user_date
                    ON reservations(user_id, date_str);
                """
            )

    def close(self) -> None:
        """Deterministically releases the underlying SQLite file handle."""
        if getattr(self, "_conn", None) is not None:
            self._conn.close()

    def __enter__(self) -> "SQLiteBookingRepository":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def add_user(self, user: User) -> None:
        try:
            with self._conn:
                self._conn.execute(
                    """
                    INSERT OR REPLACE INTO users (user_id, name, role, email, is_active)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user.user_id, user.name, user.role.value, user.email, int(user.is_active)),
                )
        except sqlite3.Error as exc:
            raise StoragePersistenceError(f"Failed to persist user '{user.user_id}': {exc}") from exc

    def get_user(self, user_id: str) -> Optional[User]:
        row = self._conn.execute(
            "SELECT user_id, name, role, email, is_active FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            return None
        return User(
            user_id=row["user_id"],
            name=row["name"],
            role=UserRole(row["role"]),
            email=row["email"],
            is_active=bool(row["is_active"]),
        )

    def add_room(self, room: Room) -> None:
        try:
            with self._conn:
                self._conn.execute(
                    """
                    INSERT OR REPLACE INTO rooms (room_id, name, room_type, capacity, hourly_rate, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        room.room_id,
                        room.name,
                        room.room_type.value,
                        room.capacity,
                        room.hourly_rate,
                        int(room.is_active),
                    ),
                )
        except sqlite3.Error as exc:
            raise StoragePersistenceError(f"Failed to persist room '{room.room_id}': {exc}") from exc

    def get_room(self, room_id: str) -> Optional[Room]:
        row = self._conn.execute(
            "SELECT room_id, name, room_type, capacity, hourly_rate, is_active FROM rooms WHERE room_id = ?",
            (room_id,),
        ).fetchone()
        if not row:
            return None
        return Room(
            room_id=row["room_id"],
            name=row["name"],
            room_type=RoomType(row["room_type"]),
            capacity=int(row["capacity"]),
            hourly_rate=float(row["hourly_rate"]),
            is_active=bool(row["is_active"]),
        )

    @staticmethod
    def _normalize_timestamp(dt: datetime.datetime) -> datetime.datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=CAMPUS_TIMEZONE)
        return dt.astimezone(CAMPUS_TIMEZONE)

    @staticmethod
    def _row_to_reservation(row: sqlite3.Row) -> Reservation:
        parsed_dt = datetime.datetime.fromisoformat(row["created_at"])
        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=CAMPUS_TIMEZONE)
        return Reservation(
            booking_id=int(row["booking_id"]),
            token=row["token"],
            user_id=row["user_id"],
            room_id=row["room_id"],
            date_str=row["date_str"],
            start_hour=int(row["start_hour"]),
            end_hour=int(row["end_hour"]),
            base_cost=float(row["base_cost"]),
            discount=float(row["discount"]),
            surcharge=float(row["surcharge"]),
            total_cost=float(row["total_cost"]),
            status=ReservationStatus(row["status"]),
            created_at=parsed_dt,
        )

    def save_reservation(self, res: Reservation) -> Reservation:
        res.created_at = self._normalize_timestamp(res.created_at)
        try:
            with self._conn:
                if res.booking_id <= 0:
                    cursor = self._conn.execute(
                        """
                        INSERT INTO reservations (
                            token, user_id, room_id, date_str, start_hour, end_hour,
                            base_cost, discount, surcharge, total_cost, status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            res.token,
                            res.user_id,
                            res.room_id,
                            res.date_str,
                            res.start_hour,
                            res.end_hour,
                            res.base_cost,
                            res.discount,
                            res.surcharge,
                            res.total_cost,
                            res.status.value,
                            res.created_at.isoformat(),
                        ),
                    )
                    res.booking_id = int(cursor.lastrowid or 0)
                else:
                    self._conn.execute(
                        """
                        UPDATE reservations
                        SET status = ?, date_str = ?, start_hour = ?, end_hour = ?,
                            base_cost = ?, discount = ?, surcharge = ?, total_cost = ?
                        WHERE booking_id = ?
                        """,
                        (
                            res.status.value,
                            res.date_str,
                            res.start_hour,
                            res.end_hour,
                            res.base_cost,
                            res.discount,
                            res.surcharge,
                            res.total_cost,
                            res.booking_id,
                        ),
                    )
            return res
        except sqlite3.Error as exc:
            raise StoragePersistenceError(f"Failed to persist reservation: {exc}") from exc

    def get_reservation(self, booking_id: int) -> Optional[Reservation]:
        row = self._conn.execute(
            "SELECT * FROM reservations WHERE booking_id = ?",
            (booking_id,),
        ).fetchone()
        return self._row_to_reservation(row) if row else None

    def find_by_room_and_date(self, room_id: str, date_str: str) -> List[Reservation]:
        rows = self._conn.execute(
            "SELECT * FROM reservations WHERE room_id = ? AND date_str = ? ORDER BY start_hour ASC",
            (room_id, date_str),
        ).fetchall()
        return [self._row_to_reservation(r) for r in rows]

    def find_by_user_and_date(self, user_id: str, date_str: str) -> List[Reservation]:
        rows = self._conn.execute(
            "SELECT * FROM reservations WHERE user_id = ? AND date_str = ? ORDER BY start_hour ASC",
            (user_id, date_str),
        ).fetchall()
        return [self._row_to_reservation(r) for r in rows]


class BookingService:
    """
    Orchestrates room reservation workflows against AbstractBookingRepository.
    Notice zero SQL or sqlite3 imports/calls exist anywhere in BookingService (DIP).
    """

    OPERATING_START: int = 8
    OPERATING_END: int = 22
    STUDENT_DAILY_LIMIT: int = 2

    def __init__(
        self,
        repo: AbstractBookingRepository,
        pricing: PricingService,
        conflict: ConflictDetector,
    ):
        self.repo = repo
        self.pricing = pricing
        self.conflict = conflict

    def create_booking(self, user_id: str, room_id: str, date_str: str, start_hour: int, end_hour: int) -> Reservation:
        # 1. User & Room validation
        user = self.repo.get_user(user_id)
        if not user or not user.is_active:
            raise ResourceNotFoundError(f"Active user '{user_id}' not found.")

        room = self.repo.get_room(room_id)
        if not room or not room.is_active:
            raise ResourceNotFoundError(f"Active room '{room_id}' not found.")

        # 2. Operating hours validation
        if start_hour < self.OPERATING_START or end_hour > self.OPERATING_END or start_hour >= end_hour:
            raise OperatingHoursExceededError(
                f"Booking {start_hour}:00-{end_hour}:00 is outside operating window (08:00-22:00)."
            )

        # 3. Collision validation
        existing_room_bookings = self.repo.find_by_room_and_date(room_id, date_str)
        if self.conflict.has_overlap(existing_room_bookings, start_hour, end_hour):
            raise SlotConflictError(f"Room '{room.name}' is already reserved for requested time on {date_str}.")

        # 4. Student quota validation
        duration = end_hour - start_hour
        if user.is_student():
            user_bookings = self.repo.find_by_user_and_date(user_id, date_str)
            if self.conflict.exceeds_daily_quota(user_bookings, duration, limit=self.STUDENT_DAILY_LIMIT):
                raise QuotaExceededError(
                    f"Student '{user.name}' exceeded daily quota of {self.STUDENT_DAILY_LIMIT} hours."
                )

        # 5. Pricing calculation via PricingService
        breakdown = self.pricing.calculate(room, user, date_str, duration)

        # 6. Generate confirmation token & persist via AbstractBookingRepository
        clean_date = date_str.replace("-", "")
        suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        token = f"SKD-{clean_date}-{suffix}"
        reservation = Reservation(
            booking_id=0,
            token=token,
            user_id=user_id,
            room_id=room_id,
            date_str=date_str,
            start_hour=start_hour,
            end_hour=end_hour,
            base_cost=breakdown.base_cost,
            discount=breakdown.discount,
            surcharge=breakdown.surcharge,
            total_cost=breakdown.total_cost,
            status=ReservationStatus.CONFIRMED,
        )
        saved = self.repo.save_reservation(reservation)

        print(f"[RECEIPT] Booking #{saved.booking_id} | Token: {token}")
        print(f"  User: {user.name} ({user.role.value.title()}) | Room: {room.name} ({room.room_type.value.title()})")
        print(f"  Slot: {date_str} {start_hour:02d}:00-{end_hour:02d}:00 ({duration} hrs)")
        print(
            f"  Cost: Base ${breakdown.base_cost:.2f} - Disc ${breakdown.discount:.2f}"
            f" + Surch ${breakdown.surcharge:.2f} = Total ${breakdown.total_cost:.2f}"
        )
        print(f"  Audit Timestamp (UTC+08:00): {saved.created_at.isoformat()}\n")
        return saved

    def cancel_booking(self, booking_id: int) -> bool:
        res = self.repo.get_reservation(booking_id)
        if not res:
            raise ResourceNotFoundError(f"Booking #{booking_id} not found.")
        if not res.is_active:
            return False
        res.status = ReservationStatus.CANCELLED
        self.repo.save_reservation(res)
        print(f"[CANCELLED] Booking #{booking_id} (Token: {res.token}) cancelled and persisted.")
        return True
