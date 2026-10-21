# Campus Facility & Room Booking System

<div align="center">

[![CI - Build & Test](https://img.shields.io/badge/CI-Passing-brightgreen?style=for-the-badge&logo=github-actions&logoColor=white)](.github/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-13%20Passed-success?style=for-the-badge&logo=pytest&logoColor=white)](tests/test_booking.py)
[![Architecture](https://img.shields.io/badge/Architecture-Clean%20%26%20SOLID-00599C?style=for-the-badge)](codebase_b/)
[![Refactoring](https://img.shields.io/badge/Refactoring-Martin%20Fowler-FF6F00?style=for-the-badge)](refactored_codebase_a/)

**An autonomous campus space and room reservation engine comparing monolithic and modular clean architectures.**  
*Inspired by [Skedda Space Scheduling Platform](https://www.skedda.com) • CSEB5213 Software Evolution & Maintenance*

</div>

---

## 🛠️ Tech Stack & Tooling

| Category | Tools & Technologies | Description |
| :--- | :--- | :--- |
| **Language** | **Python 3.10+** | Zero external dependencies; standard library native (`dataclasses`, `enum`, `datetime`, `unittest`, `secrets`) |
| **Automation & CI** | **GitHub Actions** | Automated CI pipeline executing matrix builds (Python 3.10, 3.11, 3.12) and regression tests on push and PR |
| **Testing** | **Python `unittest`** | 13 automated unit & regression tests executing in <0.02s |
| **Design Patterns** | **SOLID & Clean Architecture** | Single Responsibility, Dependency Inversion, Repository Pattern, Strategy Pattern |
| **Refactoring** | **Martin Fowler Catalog** | Extract Class (`PricingCalculator`, `ReceiptPrinter`), Extract Method, Guard Clauses, Symbolic Constants |
| **Version Control** | **Git & GitHub** | Atomic semantic commits, branch protection, CI status checks |

---

## 👥 Project Contributors & Module Ownership

| Contributor | Focus Area | Deliverables & Responsibilities | Covered Scope |
| :--- | :--- | :--- | :--- |
| **Abdullahi Osman** | System Design, Codebase Generation & Code Smell Analysis | Scoped-down architecture based on Skedda, engineered GenAI Prompts A & B, established Codebase A (Monolith) and Codebase B (Modular Clean Architecture), and conducted comparative code smell analysis (God Class, Long Method, Duplicate Code, Primitive Obsession) with poorer codebase selection. | **Sections 1, 2, and 3**<br>([`codebase_a/`](codebase_a/), [`codebase_b/`](codebase_b/)) |
| **Contributor 2** | Refactoring Strategy & Implementation | Formulated Fowler refactoring recommendations (Extract Class, Extract Method, Guard Clauses, Symbolic Constants) and implemented the refactored system. | **Section 4**<br>([`refactored_codebase_a/`](refactored_codebase_a/)) |
| **Contributor 3** | Quality Metrics Evaluation & CI Pipeline | Analyzed probable results, measured software quality metrics (LOC, Cyclomatic Complexity, coupling/cohesion), developed automated unit tests, and established GitHub Actions CI. | **Section 5**<br>([`tests/`](tests/), [`.github/workflows/ci.yml`](.github/workflows/ci.yml)) |

---

## ⚡ Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** (standard library only; no external package dependencies required)

### 2. Setup Virtual Environment (Optional)
```powershell
uv venv .venv
.venv\Scripts\activate
```
*Or standard Python:*
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Run the Codebases

#### Run Codebase A (Monolith):
```powershell
python codebase_a/booking_system.py
```

#### Run Codebase B (Modular Clean Architecture):
```powershell
python codebase_b/main.py
```

#### Run Refactored Codebase A:
```powershell
python refactored_codebase_a/booking_system.py
```

#### Run Automated Test Suite (Continuous Integration):
```powershell
python -m unittest discover tests -v
```

---

## 🔄 Continuous Integration (CI) with GitHub Actions

The repository includes an automated CI pipeline defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

The pipeline automatically triggers on every `push` and `pull_request` to the `main` branch across Python 3.10, 3.11, and 3.12:
1. Validates that Codebase A (Monolith) runs successfully without errors.
2. Validates that Codebase B (Clean Architecture) executes all domain flows and exception handling.
3. Validates that Refactored Codebase A runs with full functional parity.
4. Executes the full automated unit test suite (`tests/test_booking.py`) in < 1 second.

---

## 📁 Repository Structure

```text
CampusBooking_System/
├── .github/
│   └── workflows/
│       └── ci.yml                       # GitHub Actions CI workflow (multi-version test runner)
├── codebase_a/                          # Monolithic implementation (1 concise script)
│   └── booking_system.py
├── codebase_b/                          # Modular Clean Architecture (3 simple files)
│   ├── __init__.py
│   ├── models.py                        # Domain entities, enums & custom exceptions
│   ├── services.py                      # PricingService, ConflictDetector, Repository, BookingService
│   └── main.py                          # Demo entry point
├── refactored_codebase_a/               # Fowler-refactored Codebase A
│   └── booking_system.py                # Extract Class (PricingCalculator, ReceiptPrinter) & Guard Clauses
├── tests/
│   └── test_booking.py                  # Automated unit test suite (13 passing tests)
├── docs/
│   └── milestone_1_system_design_and_codebases.md  # Comprehensive Milestone 1 Report (Criteria 1-4)
├── cr1_corrective/                      # Prepared for Milestone 2 (Corrective CR)
├── cr2_adaptive/                        # Prepared for Milestone 2 (Adaptive CR)
├── cr3_perfective/                      # Prepared for Milestone 2 (Perfective CR)
├── sonar-project.properties             # SonarCloud scanner configuration
├── .sonarcloud.properties               # SonarCloud automatic analysis configuration
└── README.md
```

---

## 📑 Milestone 1 Report & Rubric Mapping

All Milestone 1 assessment criteria are comprehensively documented in:  
👉 **[docs/milestone_1_system_design_and_codebases.md](docs/milestone_1_system_design_and_codebases.md)**

| Rubric Criterion | Marks | Deliverable / Artifact Location |
| :--- | :---: | :--- |
| **1. System Design & GenAI Two Codebases** | 4 | System scope, stakeholder specifications, Prompts A/B documentation, Codebase A & B |
| **2. Code Smell Comparison & Poorer Quality Analysis** | 4 | Comparative smell analysis (God Class, Long Method, Duplicate Code, Primitive Obsession) with code excerpts & threshold justification |
| **3. Recommendation of Refactoring Techniques** | 4 | Fowler refactoring recommendations with deep technical justification (Extract Class, Extract Method, Guard Clauses, Constants) |
| **4. Analysis of Probable Refactoring Results** | 4 | Quantitative metrics (LOC, Cyclomatic Complexity -64%), software quality attributes, and trade-off analysis |
| **Total** | **16** | All criteria fully addressed |

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

----------------------------------------------------------------------
Ran 13 tests in 0.013s

OK
```
