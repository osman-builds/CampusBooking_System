"""
Campus Facility & Room Booking System (Inspired by Skedda)
Codebase A: Monolithic Single-Script Implementation

All state and procedural logic are contained inside one single class 'BookingSystem'.
Designed to be small, simple, and self-contained while exhibiting classic code smells:
- God Class / Large Class
- Long Method (create_booking)
- Duplicate Code (pricing & fee branches)
- Primitive Obsession (raw dictionaries and string keys)
"""

import datetime
import secrets
import string


class BookingSystem:
    """Monolithic reservation system managing storage, rules, pricing, and receipts."""

    def __init__(self):
        self.users = {}          # user_id -> dict
        self.rooms = {}          # room_id -> dict
        self.reservations = []   # list of raw dicts
        self.booking_counter = 1

    def register_user(self, user_id, name, role, email=""):
        role_clean = str(role).strip().lower()
        if role_clean not in ["student", "faculty", "staff", "admin"]:
            print(f"[ERROR] Invalid role '{role}'. Allowed: student, faculty, staff, admin.")
            return False
        if user_id in self.users:
            print(f"[ERROR] User ID '{user_id}' already exists.")
            return False
        self.users[user_id] = {
            "user_id": user_id,
            "name": name,
            "role": role_clean,
            "email": email,
            "is_active": True
        }
        print(f"[SUCCESS] Registered User '{name}' ({role_clean}) [{user_id}]")
        return True

    def register_room(self, room_id, name, room_type, capacity):
        type_clean = str(room_type).strip().lower()
        if type_clean not in ["standard", "lab", "studio"]:
            print(f"[ERROR] Invalid room_type '{room_type}'. Allowed: standard, lab, studio.")
            return False
        if room_id in self.rooms:
            print(f"[ERROR] Room ID '{room_id}' already exists.")
            return False
        self.rooms[room_id] = {
            "room_id": room_id,
            "name": name,
            "room_type": type_clean,
            "capacity": capacity,
            "is_active": True
        }
        print(f"[SUCCESS] Registered Room '{name}' ({type_clean}, Cap: {capacity}) [{room_id}]")
        return True

    def create_booking(self, user_id, room_id, date_str, start_hour, end_hour):
        """Monolithic sequential procedure performing all validation, pricing, and receipts."""
        # 1. User & Room validation
        if user_id not in self.users or not self.users[user_id].get("is_active"):
            print(f"[REJECTED] Active user '{user_id}' not found.")
            return None
        if room_id not in self.rooms or not self.rooms[room_id].get("is_active"):
            print(f"[REJECTED] Active room '{room_id}' not found.")
            return None

        user = self.users[user_id]
        room = self.rooms[room_id]

        # 2. Operating hours check (08:00 to 22:00)
        if start_hour < 8 or end_hour > 22 or start_hour >= end_hour:
            print(f"[REJECTED] Operating bounds exceeded: 08:00-22:00 required (requested {start_hour}:00-{end_hour}:00).")
            return None

        try:
            booking_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            print(f"[REJECTED] Invalid date format '{date_str}'. Expected 'YYYY-MM-DD'.")
            return None

        # 3. Schedule collision check (nested loops over hour ranges)
        for existing in self.reservations:
            if existing["room_id"] == room_id and existing["date"] == date_str and existing["status"] == "CONFIRMED":
                for req_h in range(start_hour, end_hour):
                    for exist_h in range(existing["start_hour"], existing["end_hour"]):
                        if req_h == exist_h:
                            print(f"[CONFLICT] Room '{room['name']}' already booked {existing['start_hour']:02d}:00-{existing['end_hour']:02d}:00.")
                            return None

        # 4. Student daily quota restriction (max 2 hours/day)
        duration = end_hour - start_hour
        if user["role"] == "student":
            booked_today = sum(
                (r["end_hour"] - r["start_hour"])
                for r in self.reservations
                if r["user_id"] == user_id and r["date"] == date_str and r["status"] == "CONFIRMED"
            )
            if booked_today + duration > 2:
                print(f"[QUOTA] Student '{user['name']}' exceeded daily limit (max 2 hrs; already booked {booked_today} hrs).")
                return None

        # 5. Pricing calculation (Code Smell: duplicated branching logic)
        is_weekend = booking_date.weekday() >= 5
        if room["room_type"] == "standard":
            hourly_rate = 20.0
            base_cost = duration * hourly_rate
            discount = base_cost * 0.15 if user["role"] == "student" else 0.0
            subtotal = base_cost - discount
            surcharge = subtotal * 0.20 if is_weekend else 0.0
            total_cost = subtotal + surcharge
        elif room["room_type"] in ["lab", "studio"]:
            hourly_rate = 35.0
            base_cost = duration * hourly_rate
            discount = base_cost * 0.15 if user["role"] == "student" else 0.0
            subtotal = base_cost - discount
            surcharge = subtotal * 0.20 if is_weekend else 0.0
            total_cost = subtotal + surcharge
        else:
            hourly_rate = 20.0
            base_cost = duration * hourly_rate
            discount, surcharge = 0.0, 0.0
            total_cost = base_cost

        token_suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        token = f"SKD-{booking_date.strftime('%Y%m%d')}-{token_suffix}"
        record = {
            "booking_id": self.booking_counter,
            "token": token,
            "user_id": user_id,
            "room_id": room_id,
            "date": date_str,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "duration": duration,
            "hourly_rate": hourly_rate,
            "base_cost": round(base_cost, 2),
            "discount": round(discount, 2),
            "surcharge": round(surcharge, 2),
            "total_cost": round(total_cost, 2),
            "status": "CONFIRMED"
        }
        self.reservations.append(record)
        self.booking_counter += 1

        # 7. Print Receipt directly
        print(f"\n[RECEIPT] Booking #{record['booking_id']} | Token: {token}")
        print(f"  User: {user['name']} ({user['role'].title()}) | Room: {room['name']} ({room['room_type'].title()})")
        print(f"  Slot: {date_str} {start_hour:02d}:00-{end_hour:02d}:00 ({duration} hrs)")
        print(f"  Cost: Base ${base_cost:.2f} - Disc ${discount:.2f} + Surch ${surcharge:.2f} = Total ${total_cost:.2f}\n")
        return record

    def cancel_booking(self, booking_id):
        for r in self.reservations:
            if r["booking_id"] == booking_id:
                if r["status"] == "CANCELLED":
                    print(f"[NOTICE] Booking #{booking_id} is already cancelled.")
                    return False
                r["status"] = "CANCELLED"
                print(f"[CANCELLED] Booking #{booking_id} (Token: {r['token']}) cancelled successfully.")
                return True
        print(f"[ERROR] Booking #{booking_id} not found.")
        return False

    def get_booking(self, booking_id):
        return next((r for r in self.reservations if r["booking_id"] == booking_id), None)


if __name__ == "__main__":
    print("=== Campus Room Booking System (Codebase A: Monolith) ===")
    bs = BookingSystem()
    bs.register_user("U-101", "Alice Johnson", "student", "alice@campus.edu")
    bs.register_user("U-102", "Dr. Robert Smith", "faculty", "rsmith@campus.edu")
    bs.register_room("R-SR1", "Seminar Room Alpha", "standard", 30)
    bs.register_room("R-LB2", "Computer Vision Lab", "lab", 15)

    print("\n--- 1. Valid Bookings ---")
    bs.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)  # Weekday Student: $40 - 15% = $34.00
    bs.create_booking("U-102", "R-LB2", "2026-10-17", 14, 17)  # Weekend Faculty: $105 + 20% = $126.00

    print("--- 2. Schedule Conflict Test ---")
    bs.create_booking("U-102", "R-SR1", "2026-10-12", 11, 13)

    print("--- 3. Student Daily Quota Test ---")
    bs.create_booking("U-101", "R-LB2", "2026-10-12", 15, 16)

    print("--- 4. Cancellation & Re-booking ---")
    bs.cancel_booking(1)
    bs.create_booking("U-101", "R-SR1", "2026-10-12", 10, 12)
