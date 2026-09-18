"""
Data Access Layer (Repository Pattern) for Campus Booking System (Codebase B).
Enforces Dependency Inversion Principle (DIP) through abstract base repositories.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, Optional

try:
    from models import Reservation, Room, User
except ImportError:
    from .models import Reservation, Room, User


# =============================================================================
# Abstract Repository Interfaces
# =============================================================================

class BookingRepository(ABC):
    """Abstract interface defining persistence operations for reservations."""

    @abstractmethod
    def save(self, reservation: Reservation) -> Reservation:
        """Persists a new reservation or updates an existing one."""
        pass

    @abstractmethod
    def find_by_id(self, reservation_id: int) -> Optional[Reservation]:
        """Finds a reservation by its unique numeric identifier."""
        pass

    @abstractmethod
    def find_by_room_and_date(self, room_id: str, booking_date: date) -> List[Reservation]:
        """Finds all reservations for a given room on a specific date."""
        pass

    @abstractmethod
    def find_by_user_and_date(self, user_id: str, booking_date: date) -> List[Reservation]:
        """Finds all reservations made by a user on a specific date."""
        pass

    @abstractmethod
    def find_all(self) -> List[Reservation]:
        """Retrieves all reservations in persistence."""
        pass


class RoomRepository(ABC):
    """Abstract interface defining persistence operations for rooms/facilities."""

    @abstractmethod
    def save(self, room: Room) -> Room:
        """Persists or updates a room."""
        pass

    @abstractmethod
    def find_by_id(self, room_id: str) -> Optional[Room]:
        """Finds a room by its room identifier."""
        pass

    @abstractmethod
    def find_all(self) -> List[Room]:
        """Retrieves all registered rooms."""
        pass


class UserRepository(ABC):
    """Abstract interface defining persistence operations for users."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Persists or updates a user."""
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Finds a user by their user identifier."""
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        """Retrieves all registered users."""
        pass


# =============================================================================
# In-Memory Concrete Implementations
# =============================================================================

class InMemoryBookingRepository(BookingRepository):
    """In-memory thread-isolated storage for reservations."""

    def __init__(self) -> None:
        self._storage: Dict[int, Reservation] = {}
        self._id_sequence: int = 1

    def save(self, reservation: Reservation) -> Reservation:
        if reservation.id <= 0:
            reservation.id = self._id_sequence
            self._id_sequence += 1
        self._storage[reservation.id] = reservation
        return reservation

    def find_by_id(self, reservation_id: int) -> Optional[Reservation]:
        return self._storage.get(reservation_id)

    def find_by_room_and_date(self, room_id: str, booking_date: date) -> List[Reservation]:
        return [
            res for res in self._storage.values()
            if res.room_id == room_id and res.start_time.date() == booking_date
        ]

    def find_by_user_and_date(self, user_id: str, booking_date: date) -> List[Reservation]:
        return [
            res for res in self._storage.values()
            if res.user_id == user_id and res.start_time.date() == booking_date
        ]

    def find_all(self) -> List[Reservation]:
        return list(self._storage.values())


class InMemoryRoomRepository(RoomRepository):
    """In-memory storage for room facilities."""

    def __init__(self) -> None:
        self._storage: Dict[str, Room] = {}

    def save(self, room: Room) -> Room:
        self._storage[room.room_id] = room
        return room

    def find_by_id(self, room_id: str) -> Optional[Room]:
        return self._storage.get(room_id)

    def find_all(self) -> List[Room]:
        return list(self._storage.values())


class InMemoryUserRepository(UserRepository):
    """In-memory storage for campus users."""

    def __init__(self) -> None:
        self._storage: Dict[str, User] = {}

    def save(self, user: User) -> User:
        self._storage[user.user_id] = user
        return user

    def find_by_id(self, user_id: str) -> Optional[User]:
        return self._storage.get(user_id)

    def find_all(self) -> List[User]:
        return list(self._storage.values())
