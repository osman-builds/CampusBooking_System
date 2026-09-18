# Campus Facility & Room Booking System
> Reference System: [Skedda](https://www.skedda.com) | CSEB5213 Software Evolution & Maintenance

A campus room reservation engine comparing two architectural styles generated from identical requirements:
- **Codebase A**: Monolithic single-class script (`codebase_a/booking_system.py`)
- **Codebase B**: Clean Architecture & SOLID modular design (`codebase_b/main.py`)

---

## Quickstart Guide for Collaborators

Follow these steps to set up your environment and run the project locally.

### 1. Prerequisites
- **Python 3.10+** (standard library only; no external package dependencies required)
- Recommended: [`uv`](https://github.com/astral-sh/uv) or standard Python `venv`

### 2. Setup Virtual Environment

Using **uv** (fast):
```powershell
uv venv .venv
.venv\Scripts\activate
```

*Or using standard Python:*
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Run the Codebases

#### Run Codebase A (Monolith):
```powershell
python codebase_a/booking_system.py
```

#### Run Codebase B (Clean Architecture):
```powershell
python codebase_b/main.py
```
*(Or via module syntax: `python -m codebase_b.main`)*

---

## Repository Structure

```text
CampusBooking_System/
├── codebase_a/            # Monolithic implementation (single-class script)
│   └── booking_system.py
├── codebase_b/            # Modular clean architecture
│   ├── models.py          # Domain entities & enums
│   ├── repository.py      # Abstract & in-memory data access (DIP)
│   ├── conflict_detector.py # Collision & quota domain service
│   ├── pricing_service.py # Dynamic fee calculations
│   ├── notification_service.py # Receipts & notifications
│   ├── booking_service.py # Application service & DI coordinator
│   ├── exceptions.py      # Custom domain exceptions
│   └── main.py            # Entry point & demo
├── docs/
│   └── milestone_1_system_design_and_codebases.md  # Milestone 1: System design & codebases report
└── README.md
```

---

## Documentation
- Detailed prompt design, architecture justification, and preliminary comparison:  
  👉 [Milestone 1 Report: System Design & Codebase Generation](docs/milestone_1_system_design_and_codebases.md)

---

## Team Contributions (Milestone 1)

| Team Member | Role / Focus Area | Deliverable |
| :--- | :--- | :--- |
| **Abdullahi Osman** | System Architecture & GenAI Codebases | Scoped-down design, Prompts A/B, Codebase setup |
| **[Teammate 1]** | Code Smell Analysis | Codebase A vs. B smells & technical evidence |
| **[Teammate 2]** | Fowler Refactoring | Refactoring implementation & quality metrics |
