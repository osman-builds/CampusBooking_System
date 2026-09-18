# Milestone 1: System Design & Codebase Generation

**System Title:** Campus Facility & Room Booking System  
**Reference System:** [Skedda Space Scheduling Platform](https://www.skedda.com)  
**Author / Contributor:** Abdullahi Osman 

---

## 1.1 System Architecture & Scope Justification

Skedda is a commercial multi-tenant spatial scheduling system that incorporates interactive vector floor plans, live IoT hardware door-access locks, enterprise single sign-on (SAML/OAuth 2.0), and external payment processing.

For experimental evaluation in software evolution, code smell analysis, and refactoring, the design was scoped down to an autonomous backend reservation engine:

- **User Identity Module:** Manages accounts with role distinctions (`Student`, `Staff`, `Faculty`, `Admin`).
- **Facility Inventory Module:** Manages bookable room spaces, capacity thresholds, and base hourly rates.
- **Reservation & Collision Engine:** Validates operating window constraints (08:00–22:00), executes slot overlap verification, and enforces daily usage quotas.
- **Pricing & Policy Calculator:** Calculates base fees, role-based discounts (15% for students), and weekend peak surcharges (20%).
- **Notification Dispatcher:** Dispatches formatted booking confirmations and tokens.

### Scope Shrinkage Rationale
Excluding third-party network dependencies (such as payment gateways, SSO providers, and vector rendering engines) isolates the system's core business logic. This ensures that software maintenance operations, automated test suites, and refactoring steps are deterministic and self-contained within the Python runtime.

---

## 1.2 Generative AI Prompt Execution & Documentation

Two distinct prompts were executed in the GenAI tool to generate two contrasting architectural implementations of the same system blueprint.

### Prompt A (Monolithic Generation — Codebase A)
> *"Write a complete backend reservation module for a Campus Facility & Room Booking System (inspired by Skedda) in Python as a single, self-contained monolithic script. Implement everything inside ONE single class named `BookingSystem`. Do not import or create separate files, external helper classes, design patterns, or ORM modules. The single `BookingSystem` class must manage internal dictionary storage for users, rooms, and reservations; user/room registration; a large sequential `create_booking` method validating user/room existence, 08:00-22:00 bounds, nested loop slot conflicts, a 2-hour student daily quota, nested pricing calculations (base cost, 15% student discount, 20% weekend surcharge); direct receipt printing; and cancellation. Ensure it is runnable with a `__main__` demo block."*

- **Prompt Strategy:** Enforces procedural coding within a single class without design abstractions, forcing the LLM to bundle state storage, validation, pricing math, and string formatting into deeply nested conditional structures.

### Prompt B (Modular Generation — Codebase B)
> *"Write a modular, clean-architecture backend reservation engine for a Campus Facility & Room Booking System (inspired by Skedda) in Python adhering strictly to SOLID principles. Decouple the design into distinct modules: Domain Models (`models.py`), Repository Interfaces and In-Memory Data Access (`repository.py`), Domain Services (`conflict_detector.py`, `pricing_service.py`, `notification_service.py`), Custom Business Exceptions (`exceptions.py`), and an Orchestration Application Service (`booking_service.py`) using dependency injection. Include explicit type hints and a clean `main.py` entry demo script."*

- **Prompt Strategy:** Uses explicit architectural patterns (SOLID, Repository pattern, Strategy pattern, Dependency Injection), guiding the LLM to separate domain logic, enforce high cohesion, and isolate failure points through custom domain exceptions.

---

## 1.3 Preliminary Comparison of Codebases

| Comparison Attribute | Codebase A (Prompt A Output) | Codebase B (Prompt B Output) |
| :--- | :--- | :--- |
| **Architectural Style** | Monolithic Single-Class Architecture (`BookingSystem`). | Layered / Modular Domain-Driven Architecture. |
| **File Structure** | 1 single script ([`codebase_a/booking_system.py`](../codebase_a/booking_system.py)) of ~450 lines. | 8 decoupled modules in [`codebase_b/`](../codebase_b/) (`models`, `repository`, `conflict_detector`, `pricing_service`, `notification_service`, `exceptions`, `booking_service`, `main`). |
| **State Management** | Raw dictionaries (`dict`) and lists manipulated directly inside business methods. | Typed domain entities/dataclasses (`User`, `Room`, `Reservation`) encapsulated inside repository interfaces. |
| **Separation of Concerns** | **Low:** Storage, validation, conflict detection, pricing, and string printing are coupled into one class. | **High:** Each class has a single responsibility (e.g., `ConflictDetector` only checks slot collisions). |
| **Cyclomatic Complexity** | **Very High:** `create_booking` contains nested `for` loops inside nested `if-elif-else` branches. | **Low:** Short, single-purpose methods with linear control flow and guard clauses. |
| **Error Handling** | Returns `None` or `False` and prints raw error messages to `stdout`. | Raises specific domain exceptions (`SlotConflictError`, `QuotaExceededError`, `ResourceNotFoundError`). |
| **Testability** | **Difficult:** Isolated unit testing of pricing or collision detection requires running the whole class. | **Straightforward:** Each service can be unit-tested in complete isolation via mocks or in-memory stubs. |

### Prompt Influence Analysis
- **Codebase A:** Specifying *"single class"* and *"no helper modules"* compelled the LLM to use procedural control flows and primitive types.
- **Codebase B:** Specifying *"SOLID"*, *"dependency injection"*, and explicit file names prompted the LLM to define formal interfaces and class boundaries.

---

## 1.4 Next Steps & Maintenance Roadmap

Following the establishment of Codebase A and Codebase B, the subsequent project milestones will evaluate software evolution across both paradigms:

1. **Change Request 1 (CR1 - Corrective Maintenance):** Addressing critical reservation defects, edge-case bounds, and quota enforcement in `cr1_corrective/`.
2. **Change Request 2 (CR2 - Adaptive Maintenance):** Adapting the systems to new operational constraints, updated role policies, or external interfaces in `cr2_adaptive/`.
3. **Change Request 3 (CR3 - Perfective Maintenance):** Optimizing system performance, feature expansion, and code refactoring in `cr3_perfective/` and `refactored_codebase_a/`.
4. **Automated Testing Suite:** Developing comprehensive unit and regression tests in `tests/` to verify behavioral parity between codebases.
