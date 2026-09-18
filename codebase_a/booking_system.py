"""
Campus Facility & Room Booking System (Inspired by Skedda)
Codebase A: Monolithic Single-Script Implementation

This module contains the entire backend reservation logic implemented within
a single monolithic class 'BookingSystem'. All state is managed in-memory
using native Python data structures (dictionaries and lists), and procedural
business logic is executed sequentially.
"""

import datetime
import random
import string


class BookingSystem:
    """
    Monolithic reservation management system containing all data storage,
    validation, collision detection, fee calculation, and notification logic.
    """

    def __init__(self):
        # In-memory storage for users, rooms, and reservations
        self.users = {}          # user_id -> dict
        self.rooms = {}          # room_id -> dict
        self.reservations = []   # list of raw reservation dicts
        self.booking_counter = 1

    # -------------------------------------------------------------------------
    # User Registration
    # -------------------------------------------------------------------------
    def register_user(self, user_id, name, role, email=""):
        """
        Registers a new user with rudimentary string validation.
        Valid roles: 'student', 'faculty', 'staff', 'admin'
        """
        if not isinstance(user_id, str) or not user_id.strip():
            print(f"[ERROR] User registration failed: Invalid user_id '{user_id}'. Must be a non-empty string.")
            return False

        if not isinstance(name, str) or not name.strip():
            print(f"[ERROR] User registration failed: Invalid name '{name}'. Must be a non-empty string.")
            return False

        normalized_role = str(role).strip().lower()
        if normalized_role not in ["student", "faculty", "staff", "admin"]:
            print(f"[ERROR] User registration failed: Invalid role '{role}'. Allowed roles: student, faculty, staff, admin.")
            return False

        user_id_clean = user_id.strip()
        if user_id_clean in self.users:
            print(f"[ERROR] User registration failed: User ID '{user_id_clean}' already exists.")
            return False

        # Store raw user dictionary
        self.users[user_id_clean] = {
            "user_id": user_id_clean,
            "name": name.strip(),
            "role": normalized_role,
            "email": email.strip() if isinstance(email, str) else "",
            "is_active": True
        }
        print(f"[SUCCESS] User '{name.strip()}' ({normalized_role}) registered successfully with ID: {user_id_clean}")
        return True

    # -------------------------------------------------------------------------
    # Room Registration
    # -------------------------------------------------------------------------
    def register_room(self, room_id, room_name, room_type, capacity):
        """
        Registers a new room facility with rudimentary capacity and string validation.
        Valid types: 'standard', 'lab', 'studio'
        """
        if not isinstance(room_id, str) or not room_id.strip():
            print(f"[ERROR] Room registration failed: Invalid room_id '{room_id}'. Must be a non-empty string.")
            return False

        if not isinstance(room_name, str) or not room_name.strip():
            print(f"[ERROR] Room registration failed: Invalid room_name '{room_name}'. Must be a non-empty string.")
            return False

        normalized_type = str(room_type).strip().lower()
        if normalized_type not in ["standard", "lab", "studio"]:
            print(f"[ERROR] Room registration failed: Invalid room_type '{room_type}'. Allowed types: standard, lab, studio.")
            return False

        if not isinstance(capacity, int) or capacity <= 0:
            print(f"[ERROR] Room registration failed: Invalid capacity '{capacity}'. Must be a positive integer.")
            return False

        room_id_clean = room_id.strip()
        if room_id_clean in self.rooms:
            print(f"[ERROR] Room registration failed: Room ID '{room_id_clean}' already exists.")
            return False

        # Store raw room dictionary
        self.rooms[room_id_clean] = {
            "room_id": room_id_clean,
            "room_name": room_name.strip(),
            "room_type": normalized_type,
            "capacity": capacity,
            "is_active": True
        }
        print(f"[SUCCESS] Room '{room_name.strip()}' ({normalized_type}, Cap: {capacity}) registered with ID: {room_id_clean}")
        return True

    # -------------------------------------------------------------------------
    # Core Monolithic Booking Creation Method
    # -------------------------------------------------------------------------
    def create_booking(self, user_id, room_id, date_str, start_hour, end_hour):
        """
        Creates a room booking through a sequential monolithic execution pipeline:
        1. User existence & active status verification
        2. Room existence & capacity/availability verification
        3. Operating bounds verification (08:00 to 22:00)
        4. Overlapping collision detection using nested loops
        5. Student daily quota restriction (max 2 hours/day)
        6. Nested pricing logic (base cost, student discount, weekend surcharge)
        7. Confirmation token generation and mock email receipt printing
        """
        print(f"\n--- Initiating Booking Request: User '{user_id}', Room '{room_id}', Date '{date_str}', Time: {start_hour}:00 - {end_hour}:00 ---")

        # 1. Verify user existence and active status
        if user_id not in self.users:
            print(f"[REJECTED] User validation failed: User ID '{user_id}' does not exist in the system.")
            return None

        user = self.users[user_id]
        if not user.get("is_active", False):
            print(f"[REJECTED] User validation failed: User account '{user_id}' is inactive or suspended.")
            return None

        # 2. Verify room existence and room capacity/status
        if room_id not in self.rooms:
            print(f"[REJECTED] Room validation failed: Room ID '{room_id}' does not exist in the system.")
            return None

        room = self.rooms[room_id]
        if not room.get("is_active", False):
            print(f"[REJECTED] Room validation failed: Room '{room_id}' is currently decommissioned/inactive.")
            return None

        if room.get("capacity", 0) <= 0:
            print(f"[REJECTED] Room validation failed: Room '{room_id}' has invalid capacity ({room.get('capacity')}).")
            return None

        # 3. Check operating bounds (08:00 to 22:00) and slot consistency
        if not isinstance(start_hour, int) or not isinstance(end_hour, int):
            print(f"[REJECTED] Hours validation failed: Start hour and end hour must be whole numbers (integers).")
            return None

        if start_hour < 8 or end_hour > 22:
            print(f"[REJECTED] Operating bounds exceeded: Campus facility operates strictly between 08:00 and 22:00. Requested: {start_hour}:00 to {end_hour}:00.")
            return None

        if start_hour >= end_hour:
            print(f"[REJECTED] Time sequence invalid: Start hour ({start_hour}:00) must be earlier than end hour ({end_hour}:00).")
            return None

        # Parse date string to validate format and retrieve day of week
        try:
            booking_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            print(f"[REJECTED] Date format invalid: '{date_str}'. Expected ISO format 'YYYY-MM-DD'.")
            return None

        # 4. Detect overlapping time slot collisions using nested loops
        # Outer loop iterates through existing reservations; inner loop iterates hour by hour
        for existing in self.reservations:
            if existing["room_id"] == room_id and existing["date"] == date_str:
                if existing["status"] == "CONFIRMED":
                    # Nested loop over every hour in requested slot vs existing slot
                    for req_hour in range(start_hour, end_hour):
                        for exist_hour in range(existing["start_hour"], existing["end_hour"]):
                            if req_hour == exist_hour:
                                print(f"[CONFLICT REJECTED] Schedule collision: Room '{room['room_name']}' is already booked from "
                                      f"{existing['start_hour']:02d}:00 to {existing['end_hour']:02d}:00 on {date_str} "
                                      f"(Booking #{existing['booking_id']}).")
                                return None

        # 5. Enforce Student daily quota limit (max 2 hours per day across all rooms)
        booking_duration = end_hour - start_hour
        if user["role"] == "student":
            student_hours_today = 0
            for existing in self.reservations:
                if existing["user_id"] == user_id and existing["date"] == date_str:
                    if existing["status"] == "CONFIRMED":
                        student_hours_today += (existing["end_hour"] - existing["start_hour"])

            if student_hours_today + booking_duration > 2:
                print(f"[QUOTA REJECTED] Student quota exceeded: Students may book at most 2 hours per day. "
                      f"User '{user['name']}' already has {student_hours_today} hour(s) booked on {date_str}. "
                      f"Requesting {booking_duration} additional hour(s) would exceed the 2-hour daily allowance.")
                return None

        # 6. Calculate Pricing with Nested if-elif-else logic
        # Base rates: Standard = $20/hr, Lab/Studio = $35/hr
        # Student discount: 15% off base rate
        # Weekend peak surcharge: 20% added
        is_weekend = booking_date.weekday() >= 5  # 5=Saturday, 6=Sunday

        if room["room_type"] == "standard":
            hourly_rate = 20.0
            base_cost = booking_duration * hourly_rate
            if user["role"] == "student":
                discount_amount = base_cost * 0.15
                subtotal = base_cost - discount_amount
                if is_weekend:
                    surcharge_amount = subtotal * 0.20
                    total_cost = subtotal + surcharge_amount
                else:
                    surcharge_amount = 0.0
                    total_cost = subtotal
            else:
                discount_amount = 0.0
                subtotal = base_cost
                if is_weekend:
                    surcharge_amount = subtotal * 0.20
                    total_cost = subtotal + surcharge_amount
                else:
                    surcharge_amount = 0.0
                    total_cost = subtotal
        elif room["room_type"] in ["lab", "studio"]:
            hourly_rate = 35.0
            base_cost = booking_duration * hourly_rate
            if user["role"] == "student":
                discount_amount = base_cost * 0.15
                subtotal = base_cost - discount_amount
                if is_weekend:
                    surcharge_amount = subtotal * 0.20
                    total_cost = subtotal + surcharge_amount
                else:
                    surcharge_amount = 0.0
                    total_cost = subtotal
            else:
                discount_amount = 0.0
                subtotal = base_cost
                if is_weekend:
                    surcharge_amount = subtotal * 0.20
                    total_cost = subtotal + surcharge_amount
                else:
                    surcharge_amount = 0.0
                    total_cost = subtotal
        else:
            hourly_rate = 20.0
            base_cost = booking_duration * hourly_rate
            discount_amount = 0.0
            subtotal = base_cost
            surcharge_amount = 0.0
            total_cost = base_cost

        # 7. Generate Confirmation Token and Store Reservation
        random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        confirmation_token = f"SKD-{booking_date.strftime('%Y%m%d')}-{random_suffix}"

        booking_record = {
            "booking_id": self.booking_counter,
            "confirmation_token": confirmation_token,
            "user_id": user_id,
            "room_id": room_id,
            "date": date_str,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "duration": booking_duration,
            "hourly_rate": hourly_rate,
            "base_cost": round(base_cost, 2),
            "discount_amount": round(discount_amount, 2),
            "surcharge_amount": round(surcharge_amount, 2),
            "total_cost": round(total_cost, 2),
            "status": "CONFIRMED",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.reservations.append(booking_record)
        self.booking_counter += 1

        # Direct formatting and printing of mock multi-line email receipt
        day_name = booking_date.strftime("%A")
        print("\n" + "=" * 65)
        print("          CAMPUS BOOKING SYSTEM - EMAIL RECEIPT          ")
        print("=" * 65)
        print(f" Confirmation Token  : {confirmation_token}")
        print(f" Booking ID          : #{booking_record['booking_id']}")
        print(f" Booking Status      : {booking_record['status']}")
        print(f" Booked By           : {user['name']} (ID: {user_id}, Role: {user['role'].capitalize()})")
        print(f" Facility / Room     : {room['room_name']} (ID: {room_id}, Type: {room['room_type'].capitalize()})")
        print(f" Scheduled Date      : {date_str} ({day_name})")
        print(f" Time Slot           : {start_hour:02d}:00 to {end_hour:02d}:00 ({booking_duration} Hour(s))")
        print("-" * 65)
        print(f" Base Pricing Rate   : ${hourly_rate:.2f} / hr")
        print(f" Base Subtotal       : ${base_cost:.2f} ({booking_duration} hrs @ ${hourly_rate:.2f}/hr)")
        if discount_amount > 0:
            print(f" Student Discount    : -${discount_amount:.2f} (15% applied)")
        else:
            print(f" Student Discount    : $0.00 (None)")
        if surcharge_amount > 0:
            print(f" Weekend Surcharge   : +${surcharge_amount:.2f} (20% weekend peak applied)")
        else:
            print(f" Weekend Surcharge   : $0.00 (Standard weekday)")
        print(f" Total Amount Paid   : ${total_cost:.2f}")
        print("=" * 65)
        print(" Thank you for reserving campus resources responsibly.")
        print(" Please present this token upon facility entry.")
        print("=" * 65 + "\n")

        return booking_record

    # -------------------------------------------------------------------------
    # Booking Cancellation
    # -------------------------------------------------------------------------
    def cancel_booking(self, booking_id):
        """
        Cancels a booking by modifying the raw reservation dictionary directly.
        """
        for reservation in self.reservations:
            if reservation["booking_id"] == booking_id:
                if reservation["status"] == "CANCELLED":
                    print(f"[NOTICE] Booking #{booking_id} is already cancelled.")
                    return False
                # Direct dictionary modification
                reservation["status"] = "CANCELLED"
                reservation["cancelled_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[CANCELLED] Booking #{booking_id} (Token: {reservation['confirmation_token']}) has been successfully CANCELLED.")
                return True

        print(f"[ERROR] Cancellation failed: Booking #{booking_id} not found.")
        return False

    # -------------------------------------------------------------------------
    # Status Inspection Methods
    # -------------------------------------------------------------------------
    def get_booking(self, booking_id):
        """
        Retrieves a raw reservation dictionary by its booking ID.
        """
        for reservation in self.reservations:
            if reservation["booking_id"] == booking_id:
                return reservation
        return None

    def print_system_status(self):
        """
        Inspects and displays raw dictionary state for all users, rooms, and reservations.
        """
        print("\n" + "#" * 70)
        print("                 CURRENT SYSTEM STATE INSPECTION                 ")
        print("#" * 70)

        print(f"\n[REGISTERED USERS] (Total: {len(self.users)})")
        for uid, udata in self.users.items():
            status_flag = "Active" if udata.get("is_active") else "Inactive"
            print(f"  * ID: {uid:<10} Name: {udata['name']:<18} Role: {udata['role']:<10} Status: {status_flag}")

        print(f"\n[REGISTERED ROOMS] (Total: {len(self.rooms)})")
        for rid, rdata in self.rooms.items():
            status_flag = "Active" if rdata.get("is_active") else "Inactive"
            print(f"  * ID: {rid:<10} Name: {rdata['room_name']:<22} Type: {rdata['room_type']:<10} Capacity: {rdata['capacity']:<4} Status: {status_flag}")

        print(f"\n[RECORDED RESERVATIONS] (Total: {len(self.reservations)})")
        if not self.reservations:
            print("  (No reservations on file)")
        for res in self.reservations:
            print(f"  * ID #{res['booking_id']} | Token: {res['confirmation_token']} | "
                  f"User: {res['user_id']} | Room: {res['room_id']} | "
                  f"Date: {res['date']} ({res['start_hour']:02d}:00-{res['end_hour']:02d}:00) | "
                  f"Cost: ${res['total_cost']:.2f} | Status: {res['status']}")

        print("#" * 70 + "\n")


# -----------------------------------------------------------------------------
# Main Execution Demo Block
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Initializing Campus Facility & Room Booking System (Codebase A Monolith)...")
    system = BookingSystem()

    print("\n--- 1. Registering Users ---")
    # Register 2 users: 1 student and 1 faculty
    system.register_user(user_id="U-101", name="Alice Johnson", role="student", email="alice@campus.edu")
    system.register_user(user_id="U-102", name="Dr. Robert Smith", role="faculty", email="rsmith@campus.edu")

    print("\n--- 2. Registering Rooms ---")
    # Register 2 rooms: 1 standard classroom and 1 multimedia lab/studio
    system.register_room(room_id="R-SR1", room_name="Seminar Room Alpha", room_type="standard", capacity=30)
    system.register_room(room_id="R-LB2", room_name="Computer Vision Lab", room_type="lab", capacity=15)

    print("\n--- 3. Executing Valid Bookings ---")
    # Valid Booking 1: Alice Johnson (Student) books Seminar Room Alpha for 2 hours on a weekday
    # 2 hours * $20/hr = $40; with 15% student discount = $34.00
    b1 = system.create_booking(
        user_id="U-101",
        room_id="R-SR1",
        date_str="2026-10-12",  # Monday (Weekday)
        start_hour=10,
        end_hour=12
    )

    # Valid Booking 2: Dr. Robert Smith (Faculty) books Computer Vision Lab for 3 hours on a weekend
    # 3 hours * $35/hr = $105; weekend +20% surcharge = $126.00
    b2 = system.create_booking(
        user_id="U-102",
        room_id="R-LB2",
        date_str="2026-10-17",  # Saturday (Weekend Peak)
        start_hour=14,
        end_hour=17
    )

    print("\n--- 4. Triggering Schedule Conflict & Quota Rejection ---")
    # Conflict Rejection: Attempting to book Seminar Room Alpha during overlapping hours (11:00 - 13:00)
    print("\n[TEST CASE: Overlapping Slot Conflict]")
    system.create_booking(
        user_id="U-102",
        room_id="R-SR1",
        date_str="2026-10-12",
        start_hour=11,
        end_hour=13
    )

    # Quota Rejection: Student Alice attempts to book an additional hour on the same day (2-hour daily limit reached)
    print("\n[TEST CASE: Student Daily Quota Exceeded]")
    system.create_booking(
        user_id="U-101",
        room_id="R-LB2",
        date_str="2026-10-12",
        start_hour=15,
        end_hour=16
    )

    # Operating Bounds Check Rejection
    print("\n[TEST CASE: Outside Operating Bounds]")
    system.create_booking(
        user_id="U-102",
        room_id="R-SR1",
        date_str="2026-10-12",
        start_hour=7,
        end_hour=9
    )

    print("\n--- 5. Booking Cancellation Demonstration ---")
    # Cancel Booking #1 directly
    system.cancel_booking(booking_id=1)

    # Now that Booking #1 is cancelled, the student should be allowed to book again on the same day!
    print("\n[TEST CASE: Re-booking after Cancellation]")
    system.create_booking(
        user_id="U-101",
        room_id="R-SR1",
        date_str="2026-10-12",
        start_hour=10,
        end_hour=12
    )

    print("\n--- 6. System State Inspection ---")
    system.print_system_status()
