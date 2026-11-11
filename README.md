# Campus Facility & Room Booking System

<div align="center">

[![CI - Build & Test](https://img.shields.io/badge/CI-Passing-brightgreen?style=for-the-badge&logo=github-actions&logoColor=white)](.github/workflows/ci.yml)
[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=osman-builds_CampusBooking_System&token=bef713a6ca2db7df5b52c81f08230f2f605f667b)](https://sonarcloud.io/summary/new_code?id=osman-builds_CampusBooking_System)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-23%20Passed-success?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20%26%20SOLID-00599C?style=for-the-badge)](codebase_b/)
[![SMLC](https://img.shields.io/badge/SMLC-CI--IMLC%20(6--Phase)-6A1B9A?style=for-the-badge)](docs/milestone_2_smlc_and_change_requests.md)

**An autonomous campus space and room reservation engine comparing monolithic and modular clean architectures across refactoring and software maintenance life cycles.**  
*Inspired by [Skedda Space Scheduling Platform](https://www.skedda.com) • CSEB5213 Software Evolution & Maintenance*

</div>

---

## 🛠️ Tech Stack & Tooling

| Category | Tools & Technologies | Description |
| :--- | :--- | :--- |
| **Language & Runtime** | **Python 3.10+** | Zero external dependencies; standard library native (`dataclasses`, `enum`, `datetime`, `sqlite3`, `unittest`, `secrets`) |
| **Persistence (CR-02)** | **SQLite3 (`sqlite3`)** | Built-in ACID relational DBMS adapter with parameterized SQL, foreign keys, and `UTC+08:00` audit timestamps |
| **Automation & CI** | **GitHub Actions & SonarCloud** | Matrix CI builds (Python 3.10, 3.11, 3.12), static quality & security analysis, and regression gates on push/PR |
| **Testing** | **Python `unittest`** | 23 automated unit, boundary, durability & regression tests executing in ~0.11s |
| **Design Patterns** | **SOLID & Clean Architecture** | Single Responsibility, Open/Closed, Dependency Inversion, Port-Adapter Repository, Decoupled Notification Service |
| **Maintenance & Refactoring** | **CI-IMLC & Martin Fowler Catalog** | 6-phase CI-Gated Iterative Maintenance Life Cycle (IEEE 1219 + ISO 14764 + Basili) & Fowler Refactoring |
| **Version Control** | **Git & GitHub** | Atomic semantic Conventional Commits, branch protection, CI status checks |

---

## ⚡ Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** (standard library only; no external package dependencies required)

### 2. Setup Virtual Environment (Optional)
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Run Milestone 1 Codebases
```powershell
# Run Codebase A (Monolith)
python codebase_a/booking_system.py

# Run Codebase B (Modular Clean Architecture - Selected Superior Baseline)
python codebase_b/main.py

# Run Refactored Codebase A
python refactored_codebase_a/booking_system.py
```

### 4. Run Milestone 2 Change Requests (Evolved from Codebase B)
```powershell
# CR-01 (Corrective): Canonical ISO-8601 Date Normalization & Strict Hour-Type Validation
python cr1_corrective/main.py

# CR-02 (Adaptive): SQLite3 Relational DBMS Persistence & UTC+08:00 Server Runtime
python cr2_adaptive/main.py

# CR-03 (Perfective): Attendee Capacity Bounds, Smart Room Discovery, NotificationService & O(1) Indexing
python cr3_perfective/main.py
```

### 5. Run Full Automated Test Suite (Continuous Integration)
```powershell
python -m unittest discover tests -v
```

---

## 🔄 Continuous Integration (CI) with GitHub Actions

The repository includes an automated CI pipeline defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) alongside SonarCloud configuration in [`sonar-project.properties`](sonar-project.properties).

The pipeline automatically triggers on every `push` and `pull_request` to `main` across Python 3.10, 3.11, and 3.12:
1. Validates Milestone 1 executions (`codebase_a`, `codebase_b`, and `refactored_codebase_a`).
2. Validates Milestone 2 Change Request executions (`cr1_corrective`, `cr2_adaptive`, and `cr3_perfective`).
3. Executes all **23 automated unit and regression tests** (`tests/test_booking.py` and `tests/test_milestone2_crs.py`) in `< 1 second`.

---

## 📁 Repository Structure

```text
CampusBooking_System/
├── .github/
│   └── workflows/
│       └── ci.yml                                       # GitHub Actions CI workflow (multi-version matrix runner)
├── codebase_a/                                          # Milestone 1: Monolithic implementation (poorer baseline)
│   └── booking_system.py
├── codebase_b/                                          # Milestone 1 & 2 Baseline: Modular Clean Architecture (better quality)
│   ├── __init__.py
│   ├── models.py                                        # Domain entities, enums & custom exceptions
│   ├── services.py                                      # PricingService, ConflictDetector, Repository, BookingService
│   └── main.py                                          # Demo entry point
├── refactored_codebase_a/                               # Milestone 1: Fowler-refactored Codebase A
│   └── booking_system.py
├── cr1_corrective/                                      # Milestone 2 CR-01 (Corrective): Canonical date & hour-type boundary fix
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── main.py
├── cr2_adaptive/                                        # Milestone 2 CR-02 (Adaptive): SQLite3 RDBMS adapter & UTC+08:00 runtime
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── main.py
├── cr3_perfective/                                      # Milestone 2 CR-03 (Perfective): Capacity bounds, search, NotificationService & O(1) index
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── main.py
├── tests/
│   ├── test_booking.py                                  # Milestone 1 unit & parity test suite (13 tests)
│   └── test_milestone2_crs.py                           # Milestone 2 CR-01, CR-02 & CR-03 test suite (10 tests)
├── docs/
│   ├── milestone_1_system_design_and_codebases.md       # Comprehensive Milestone 1 Report (16 Marks)
│   └── milestone_2_smlc_and_change_requests.md          # Comprehensive Milestone 2 Report (14 Marks)
├── sonar-project.properties                             # SonarCloud scanner configuration
├── .sonarcloud.properties                               # SonarCloud automatic analysis configuration
└── README.md
```

---

## 📑 Milestone 1 Report & Rubric Mapping (16 Marks)

👉 **[docs/milestone_1_system_design_and_codebases.md](docs/milestone_1_system_design_and_codebases.md)**

| Rubric Criterion | Marks | Deliverable / Artifact Location |
| :--- | :---: | :--- |
| **1. System Design & GenAI Two Codebases** | 4 | System scope, stakeholder specifications, Prompts A/B documentation, Codebase A & B |
| **2. Code Smell Comparison & Poorer Quality Analysis** | 4 | Comparative smell analysis (God Class, Long Method, Duplicate Code, Primitive Obsession) concluding Codebase B is superior |
| **3. Recommendation of Refactoring Techniques** | 4 | Fowler refactoring recommendations with deep technical justification (Extract Class, Extract Method, Guard Clauses, Constants) |
| **4. Analysis of Probable Refactoring Results** | 4 | Quantitative metrics (LOC, Cyclomatic Complexity -64%), software quality attributes, and trade-off analysis |
| **Total** | **16** | All Milestone 1 criteria fully addressed |

---

## 📑 Milestone 2 Report & Rubric Mapping (14 Marks)

👉 **[docs/milestone_2_smlc_and_change_requests.md](docs/milestone_2_smlc_and_change_requests.md)**

| Rubric Criterion | Marks | Deliverable / Artifact Location |
| :--- | :---: | :--- |
| **1. Specifications of SMLC Model Best Suited to Experimented System** | 4 | Synthesis of IEEE 1219, ISO/IEC 14764, Basili Iterative Enhancement & DevOps gates into the 6-phase **CI-IMLC** model for Codebase B |
| **2. Proposal of THREE (3) Change / Modification Requests (CR/MR)** | 4 | Line-level audit of Codebase B proposing **CR-01 (Corrective)** [`cr1_corrective/`](cr1_corrective/), **CR-02 (Adaptive)** [`cr2_adaptive/`](cr2_adaptive/), and **CR-03 (Perfective)** [`cr3_perfective/`](cr3_perfective/) |
| **3. SMLC Phase Inputs, Outputs, Control & Metrics for Corrective CR/MR** | 2 | Complete 6-phase CI-IMLC specification, empirical metrics & explicit assumptions for **CR-01** (Section 4) |
| **4. SMLC Phase Inputs, Outputs, Control & Metrics for Adaptive CR/MR** | 2 | Complete 6-phase CI-IMLC specification, empirical durability/latency metrics & explicit assumptions for **CR-02** (Section 5) |
| **5. SMLC Phase Inputs, Outputs, Control & Metrics for Perfective CR/MR** | 2 | Complete 6-phase CI-IMLC specification, $1,891\times$ $O(1)$ lookup benchmark & explicit assumptions for **CR-03** (Section 6) |
| **Total** | **14** | All Milestone 2 criteria fully addressed & verified by automated CI |

---

## 🧪 Automated Test Verification

Execution of `python -m unittest discover tests -v`:
```text
test_cancellation_and_rebooking (test_booking.TestCodebaseA.test_cancellation_and_rebooking) ... ok
test_operating_hours_bounds (test_booking.TestCodebaseA.test_operating_hours_bounds) ... ok
test_overlapping_conflict_rejected (test_booking.TestCodebaseA.test_overlapping_conflict_rejected) ... ok
test_student_daily_quota_enforced (test_booking.TestCodebaseA.test_student_daily_quota_enforced) ... ok
test_valid_booking_with_student_discount (test_booking.TestCodebaseA.test_valid_booking_with_student_discount) ... ok
test_weekend_surcharge_calculation (test_booking.TestCodebaseA.test_weekend_surcharge_calculation) ... ok
test_cancellation_and_rebooking (test_booking.TestCodebaseB.test_cancellation_and_rebooking) ... ok
test_operating_hours_raises_exception (test_booking.TestCodebaseB.test_operating_hours_raises_exception) ... ok
test_quota_exceeded_raises_exception (test_booking.TestCodebaseB.test_quota_exceeded_raises_exception) ... ok
test_slot_conflict_raises_exception (test_booking.TestCodebaseB.test_slot_conflict_raises_exception) ... ok
test_valid_booking_with_pricing (test_booking.TestCodebaseB.test_valid_booking_with_pricing) ... ok
test_functional_parity (test_booking.TestRefactoredCodebaseA.test_functional_parity) ... ok
test_isolated_pricing_calculator (test_booking.TestRefactoredCodebaseA.test_isolated_pricing_calculator) ... ok
test_canonical_date_prevents_double_booking_and_fixes_token (test_milestone2_crs.TestCR1CorrectiveMaintenance.test_canonical_date_prevents_double_booking_and_fixes_token) ... ok
test_canonical_date_prevents_student_quota_bypass (test_milestone2_crs.TestCR1CorrectiveMaintenance.test_canonical_date_prevents_student_quota_bypass) ... ok
test_invalid_calendar_dates_raise_domain_exception (test_milestone2_crs.TestCR1CorrectiveMaintenance.test_invalid_calendar_dates_raise_domain_exception) ... ok
test_non_integer_hours_rejected_without_phantom_persistence (test_milestone2_crs.TestCR1CorrectiveMaintenance.test_non_integer_hours_rejected_without_phantom_persistence) ... ok
test_dip_parity_between_inmemory_and_sqlite_adapters (test_milestone2_crs.TestCR2AdaptiveMaintenance.test_dip_parity_between_inmemory_and_sqlite_adapters) ... ok
test_parameterized_sql_injection_safety (test_milestone2_crs.TestCR2AdaptiveMaintenance.test_parameterized_sql_injection_safety) ... ok
test_sqlite_file_durability_across_restarts (test_milestone2_crs.TestCR2AdaptiveMaintenance.test_sqlite_file_durability_across_restarts) ... ok
test_attendee_capacity_validation_and_default_compatibility (test_milestone2_crs.TestCR3PerfectiveMaintenance.test_attendee_capacity_validation_and_default_compatibility) ... ok
test_silent_notifier_produces_zero_stdout_and_o1_index_scales (test_milestone2_crs.TestCR3PerfectiveMaintenance.test_silent_notifier_produces_zero_stdout_and_o1_index_scales) ... ok
test_smart_available_room_discovery_and_best_fit_sorting (test_milestone2_crs.TestCR3PerfectiveMaintenance.test_smart_available_room_discovery_and_best_fit_sorting) ... ok

----------------------------------------------------------------------
Ran 23 tests in 0.109s

OK
```
