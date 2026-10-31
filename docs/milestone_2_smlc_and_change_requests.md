# CSEB5213 Software Evolution & Maintenance
## Assignment Milestone 2: System Evolution and Maintenance Life Cycle Model Construction

| Assessment Metadata | Details |
| :--- | :--- |
| **Course Code / Name** | **CSEB5213** - Software Evolution & Maintenance |
| **Academic Session** | Semester 1, 2026/2027 |
| **Assessment Title** | Assignment Milestone 2 (System Evolution and Maintenance Life Cycle Model Construction) |
| **Weightage** | 14 Marks (completing 30 Total Coursework Marks alongside Milestone 1's 16 Marks) |
| **System Title** | Campus Facility & Room Booking System |
| **Experimented Baseline** | **Codebase B** — Modular Clean Architecture & SOLID Implementation ([`codebase_b/`](../codebase_b/)) |
| **Reference System** | [Skedda Space Scheduling Platform (https://www.skedda.com)](https://www.skedda.com) |
| **Author** | **Abdullahi Osman** |

---

## Rubric Alignment & Deliverable Mapping

| Rubric Criterion | Allocated Marks | Report Section & Companion Repository Artifacts |
| :--- | :---: | :--- |
| **1. Specifications of a system maintenance life cycle (SMLC) model that best suits experimented system** | **4** | [Section 1](#1-baseline-system-continuity--architectural-profile-codebase-b) & [Section 2](#2-specification-of-the-ci-gated-iterative-maintenance-life-cycle-ci-imlc-model) (Classical SMLC synthesis, 6-phase **CI-IMLC** blueprint, attributes, and CI/SonarCloud components) |
| **2. Proposal of THREE (3) change / modification requests (CR/MR) that can be conducted on the experimented system** | **4** | [Section 3](#3-codebase-b-audit--proposal-of-three-3-real-change--modification-requests) (**CR-01 Corrective** [`cr1_corrective/`](../cr1_corrective/), **CR-02 Adaptive** [`cr2_adaptive/`](../cr2_adaptive/), **CR-03 Perfective** [`cr3_perfective/`](../cr3_perfective/)) |
| **3. Details of inputs, outputs, control and metrics of each phase of specified SMLC for corrective CR/MR** | **2** | [Section 4](#4-smlc-phase-details-for-corrective-maintenance-cr-01) (6-phase Inputs, Controls, Outputs, Empirical Metrics & Explicit Assumptions for **CR-01**) |
| **4. Details of inputs, outputs, control and metrics of each phase of specified SMLC for adaptive CR/MR** | **2** | [Section 5](#5-smlc-phase-details-for-adaptive-maintenance-cr-02) (6-phase Inputs, Controls, Outputs, Empirical Metrics & Explicit Assumptions for **CR-02**) |
| **5. Details of inputs, outputs, control and metrics of each phase of specified SMLC for perfective CR/MR** | **2** | [Section 6](#6-smlc-phase-details-for-perfective-maintenance-cr-03) (6-phase Inputs, Controls, Outputs, Empirical Metrics & Explicit Assumptions for **CR-03**) |
| **Total** | **14** | Verified by 23 automated unit & regression tests ([`tests/test_milestone2_crs.py`](../tests/test_milestone2_crs.py)) and GitHub Actions CI ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) |

---

## Table of Contents
1. [Baseline System Continuity & Architectural Profile (Codebase B)](#1-baseline-system-continuity--architectural-profile-codebase-b)
   - 1.1 Justification of Experimented Baseline Selection
   - 1.2 Architectural & Operational Profile Driving SMLC Selection
2. [Specification of the CI-Gated Iterative Maintenance Life Cycle (CI-IMLC) Model](#2-specification-of-the-ci-gated-iterative-maintenance-life-cycle-ci-imlc-model)
   - 2.1 Critical Evaluation & Synthesis of Existing SMLC Models
   - 2.2 Architectural Specification of the Proposed 6-Phase CI-IMLC Model
   - 2.3 Justification of Chosen Phases, Phase Attributes, and Maintenance Components
3. [Codebase B Audit & Proposal of THREE (3) Real Change / Modification Requests](#3-codebase-b-audit--proposal-of-three-3-real-change--modification-requests)
   - 3.1 Maintenance Category Orthogonality Matrix
   - 3.2 CR-01 (Corrective Maintenance): Canonical ISO-8601 Date Normalization & Input Boundary Defect Fix
   - 3.3 CR-02 (Adaptive Maintenance): Persistent SQLite3 Relational DBMS Adapter & `UTC+08:00` Server Runtime
   - 3.4 CR-03 (Perfective Maintenance): Attendee Capacity Enforcement, Best-Fit Space Discovery, `NotificationService` & $O(1)$ Indexing
4. [SMLC Phase Details for Corrective Maintenance (CR-01)](#4-smlc-phase-details-for-corrective-maintenance-cr-01)
   - 4.1 System & Operational Assumptions for CR-01
   - 4.2 Phase-by-Phase Inputs, Controls, Outputs, and Metrics (CR-01)
5. [SMLC Phase Details for Adaptive Maintenance (CR-02)](#5-smlc-phase-details-for-adaptive-maintenance-cr-02)
   - 5.1 Environmental & Infrastructure Assumptions for CR-02
   - 5.2 Phase-by-Phase Inputs, Controls, Outputs, and Metrics (CR-02)
6. [SMLC Phase Details for Perfective Maintenance (CR-03)](#6-smlc-phase-details-for-perfective-maintenance-cr-03)
   - 6.1 Domain, Compatibility & Performance Assumptions for CR-03
   - 6.2 Phase-by-Phase Inputs, Controls, Outputs, and Metrics (CR-03)
7. [Cross-CR Synthesis & Empirical Verification Summary](#7-cross-cr-synthesis--empirical-verification-summary)

---

## 1. Baseline System Continuity & Architectural Profile (Codebase B)

### 1.1 Justification of Experimented Baseline Selection
In Milestone 1 ([`docs/milestone_1_system_design_and_codebases.md`](milestone_1_system_design_and_codebases.md)), two functionally equivalent implementations of the Skedda-inspired **Campus Facility & Room Booking System** were empirically evaluated:
- **Codebase A ([`codebase_a/booking_system.py`](../codebase_a/booking_system.py)):** Concluded as **poorer in quality** due to four concentrated code smells (*God Class*, *Long Method* with high cyclomatic complexity, *Duplicate Code* across pricing tiers, and *Primitive Obsession*), and subsequently restructured in Milestone 1.
- **Codebase B ([`codebase_b/`](../codebase_b/)):** Concluded as **superior in quality** because it strictly enforces SOLID principles and Clean Architecture across three cohesive modules:
  1. [`codebase_b/models.py`](../codebase_b/models.py): Strongly typed `@dataclass` entities (`User`, `Room`, `Reservation`), `Enum` value types (`UserRole`, `RoomType`, `ReservationStatus`), and an explicit `BookingException` hierarchy (`ResourceNotFoundError`, `OperatingHoursExceededError`, `SlotConflictError`, `QuotaExceededError`).
  2. [`codebase_b/services.py`](../codebase_b/services.py): Single-responsibility domain services (`PricingService`, `ConflictDetector`), data persistence (`BookingRepository`), and dependency-injected workflow orchestration (`BookingService`).
  3. [`codebase_b/main.py`](../codebase_b/main.py): Composition root and executable demonstration entry point.

In strict compliance with the Milestone 2 specification—*"continue the experimentation of codebase that was concluded as better in quality in Milestone 1"*—**Codebase B** serves as the immutable baseline system for all maintenance life cycle modeling and evolutionary Change Requests in this report.

### 1.2 Architectural & Operational Profile Driving SMLC Selection
An effective System Maintenance Life Cycle (SMLC) cannot be selected in a vacuum; it must match the structural, operational, and tooling realities of the target software system:
1. **Modular, Low-Coupling Clean Architecture (451 Total Lines / 354 SLOC):** Changes to pricing, collision algorithms, persistence, or entity constraints are structurally isolated behind explicit class boundaries and constructor Dependency Injection.
2. **Zero External Package Dependencies (Python 3.10+ Standard Library):** Eliminates third-party supply-chain churn while allowing deterministic builds across Python 3.10, 3.11, and 3.12+.
3. **Sub-Second Deterministic Regression Suite (`< 0.15s`):** Unit and regression tests via Python `unittest` execute instantaneously without external network mocks, making automated Continuous Integration (CI) execution viable on every single commit.
4. **Active Automated DevOps Tooling:** The repository already integrates **GitHub Actions** multi-version matrix builds ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) and **SonarCloud** static quality and security analysis ([`sonar-project.properties`](../sonar-project.properties)).

---

## 2. Specification of the CI-Gated Iterative Maintenance Life Cycle (CI-IMLC) Model

### 2.1 Critical Evaluation & Synthesis of Existing SMLC Models
To construct an SMLC that accurately reflects modern software maintenance while preserving rigorous engineering governance, five established maintenance models from software evolution literature were evaluated against Codebase B:

| Existing SMLC Model | Core Lifecycle Structure & Strengths | Limitations for Modern Maintenance of Codebase B | Disposition in Our Tailored SMLC |
| :--- | :--- | :--- | :--- |
| **1. IEEE Std 1219-1998** (*7-Phase Sequential Maintenance Process*) | Defines 7 rigorous phases (*Identification & Classification*, *Analysis*, *Design*, *Implementation*, *System Test*, *Acceptance Test*, *Delivery*), each governed by explicit **Inputs, Controls, Outputs, and Metrics**. | Assumes heavyweight, waterfall-style manual handoffs between separate System QA and UAT teams—creating disproportionate overhead for a 354-SLOC modular Python engine with sub-second automated tests. Lacks automated static analysis gates and post-release telemetry loops. | **Core Foundation Adopted & Streamlined:** Retain IEEE 1219's formal *Input–Control–Output–Metrics* attribute contract, triage discipline, and impact analysis, while consolidating manual Phases 5 & 6 into an automated CI Matrix Regression & Acceptance gate. |
| **2. ISO/IEC 14764** (*International Standard for Software Maintenance*) | Organizes maintenance into 6 primary activities (*Process Implementation*, *Problem & Modification Analysis*, *Modification Implementation*, *Maintenance Review/Acceptance*, *Migration*, *Retirement*). | Treats *Modification Implementation* as a high-level black box delegating to ISO/IEC 12207, providing insufficient granularity on modern Test-Driven Development (TDD), branch isolation, or static code-smell enforcement. | **Selectively Integrated:** Adopt ISO/IEC 14764's explicit **Architectural Impact Analysis** and **Baseline Migration** governance (essential when adapting storage from volatile RAM to SQLite3 RDBMS). |
| **3. Basili's Iterative Enhancement Model (1990)** | Evolves systems through repeated cycles of *Analyze Existing System -> Characterize Proposed Change -> Redesign Current Release -> Implement & Verify*. | Focuses heavily on structural redesign per iteration without specifying automated CI/CD deployment pipelines, defect SLA prioritization, or static security scanning. | **Core Design Philosophy Adopted:** Embed iterative contract redesign before coding so every CR preserves Codebase B's SOLID boundaries and counteracts **Lehman's Law II (Increasing Complexity)**. |
| **4. Boehm's Maintenance Model (1983)** | Models maintenance as a closed economic management loop (*Change Proposal -> CCB Economic Evaluation -> Approved Modification -> Verification -> Feedback*). | Over-emphasizes manual Change Control Board (CCB) accounting committees over automated technical verification gates. | **Adapted for Lightweight Governance:** Translate CCB triage into structured GitHub Issue/CR severity & ROI prioritization in Phase 1 and post-release feedback in Phase 6 (**Lehman's Law VIII: Feedback System**). |
| **5. Quick-Fix Model** | Modifies source code immediately upon problem report, updating tests and documentation retroactively (if at all). | Directly induces architectural erosion, regression defects, undocumented side effects, and code-smell re-introduction (**Lehman's Law VII: Declining Quality**). | **Explicitly Rejected:** Unacceptable for Codebase B; bypassing contract design and static gates would degrade Clean Architecture back toward Codebase A's monolithic smells. |

### 2.2 Architectural Specification of the Proposed 6-Phase CI-IMLC Model
Synthesizing the formal phase-attribute rigor of **IEEE Std 1219**, the migration/impact discipline of **ISO/IEC 14764**, the architectural preservation of **Basili's Iterative Enhancement**, and modern **DevOps Continuous Integration / Static Analysis Gates**, we specify the **CI-Gated Iterative Maintenance Life Cycle (CI-IMLC)** for the Campus Facility & Room Booking System.

```mermaid
flowchart TD
    Trigger["Operational Trigger: Bug Report / Environment Shift / Enhancement Request"] --> P1

    subgraph CI_IMLC ["CI-Gated Iterative Maintenance Life Cycle (CI-IMLC) for Codebase B"]
        P1["Phase 1: CR/MR Triage, Classification & Prioritization (IEEE 1219 Ph.1 + Boehm)"]
        P2["Phase 2: Architectural Impact & Ripple Analysis (IEEE 1219 Ph.2 + ISO 14764)"]
        P3["Phase 3: Evolutionary Contract Design & TDD Specification (Basili Iterative + SOLID)"]
        P4["Phase 4: Modular Implementation & Static Quality Gate (Git Branch + SonarCloud)"]
        P5["Phase 5: Automated CI Matrix Regression & Acceptance (GitHub Actions Py 3.10-3.12)"]
        P6["Phase 6: Release Delivery, Baseline Migration & Observability (ISO 14764 + DevOps)"]

        P1 -->|"Approved & Prioritized CR Specification"| P2
        P2 -->|"Layer Impact Matrix & Risk Clearance"| P3
        P3 -->|"SOLID Interface Delta & Failing TDD Suite"| P4
        P4 -->|"SonarCloud Gate Pass (0 Bugs, 0 Security Hotspots)"| P5
        P4 -.->|"Static Gate Fail: Complexity / Smell / Security Violation"| P4
        P5 -->|"100% Matrix Pass & Stakeholder Acceptance"| P6
        P5 -.->|"Unit / Regression Failure"| P4
        P5 -.->|"Architectural Contract Mismatch"| P3
    end

    P6 -->|"Production Baseline Tag & Telemetry Feedback Loop (Lehman Law VIII)"| Trigger
```

### 2.3 Justification of Chosen Phases, Phase Attributes, and Maintenance Components

#### A. Justification of the Six Chosen Phases
1. **Phase 1 — CR/MR Triage, Classification & Prioritization:** Prevents ad-hoc "Quick-Fix" code edits by assigning every incoming request a unique identifier (`CR-YYYY-NNN`), classifying it strictly under ISO/IEC 14764 taxonomy (*Corrective*, *Adaptive*, *Perfective*, or *Preventive*), verifying reproducibility or business driver validity, and assigning severity/priority SLAs.
2. **Phase 2 — Architectural Impact & Ripple Analysis:** Because Codebase B enforces strict unidirectional dependencies (`main.py -> services.py -> models.py`), Phase 2 traces how a proposed change ripples across domain entities, exceptions, injected service ports, and existing tests—quantifying blast radius and technical feasibility before design begins.
3. **Phase 3 — Evolutionary Contract Design & TDD Specification:** Operationalizes Basili's Iterative Enhancement and SOLID's Open/Closed & Dependency Inversion Principles. Maintainers specify interface signatures, domain exceptions, and **failing automated test cases (TDD Red stage)** upfront so behavioral acceptance criteria are executable rather than ambiguous prose.
4. **Phase 4 — Modular Implementation & Static Quality Gate:** Isolates code mutations on dedicated feature branches/packages with atomic semantic commits. Crucially, modern maintenance embeds **automated static analysis (SonarCloud)** directly in Phase 4 to block complexity spikes ($V(G)$), copy-paste duplication, or security flaws (e.g., insecure PRNGs or raw SQL string concatenation) *before* integration testing.
5. **Phase 5 — Automated CI Matrix Regression & Acceptance Verification:** Consolidates IEEE 1219's separate System Testing and Acceptance Testing phases into an automated **GitHub Actions CI Matrix** running across Python 3.10, 3.11, and 3.12+. For Codebase B's deterministic `< 0.15s` test suite, automated multi-version regression paired with executable acceptance assertions provides higher reliability and $100\times$ faster feedback than manual multi-stage QA handoffs.
6. **Phase 6 — Release Delivery, Baseline Migration & Post-Deployment Observability:** Merges verified changes into the protected `main` baseline, executes data/schema migration scripts (critical for stateful RDBMS adaptations), updates documentation, and monitors runtime audit logs/metrics—closing **Lehman's Eighth Law (Feedback System)** back to Phase 1.

#### B. Justification of Chosen Phase Attributes
To ensure rigorous engineering traceability across all six phases, each phase is governed by five standardized attributes (extending IEEE Std 1219's four canonical attributes with explicit *Assumptions*):
- **Inputs:** Concrete upstream artifacts, baseline source modules, defect/environment specifications, and test fixtures entering the phase.
- **Controls:** Architectural rules (SOLID/DIP boundaries), coding standards, branch protection policies, and automated pass/fail quality gates constraining phase execution.
- **Outputs:** Verifiable deliverables produced upon phase completion that serve as traceable inputs to the subsequent phase.
- **Metrics:** Quantitative product and process indicators (with explicit target thresholds) measuring defect containment, complexity drift, performance, durability, and regression safety.
- **Assumptions:** Explicit environmental, domain, compatibility, and operational preconditions under which phase controls and metrics hold valid.

#### C. Justification of Chosen Maintenance Components (Repository Ecosystem)
| Maintenance Component | Concrete Tooling in Repository | Role Within the CI-IMLC Model |
| :--- | :--- | :--- |
| **Configuration & Change Control** | Git & GitHub (`main` branch + semantic commits) | Enforces atomic change isolation, diff auditability, and rollback capability across Phases 1–6. |
| **Static Quality & Security Gate** | **SonarCloud** ([`sonar-project.properties`](../sonar-project.properties)) | Automatically audits cognitive/cyclomatic complexity, code smells, security hotspots (e.g., S2245, S3649), and duplication in Phase 4. |
| **Automated Regression Harness** | Python `unittest` ([`tests/`](../tests/)) | Executes 23 deterministic unit, boundary, persistence, and behavioral parity assertions in `0.109s` during Phases 3–5. |
| **Continuous Integration Matrix** | **GitHub Actions** ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) | Validates cross-version runtime compatibility (`Python 3.10 | 3.11 | 3.12`) on `ubuntu-latest` containers in Phase 5. |
| **Architectural Documentation** | Markdown & Mermaid Specs ([`docs/`](../docs/), [`README.md`](../README.md)) | Preserves synchronization between living source code and system architecture specifications in Phases 3 & 6. |

---

## 3. Codebase B Audit & Proposal of THREE (3) Real Change / Modification Requests

### 3.1 Maintenance Category Orthogonality Matrix
A comprehensive static and dynamic audit of **Codebase B** ([`codebase_b/models.py`](../codebase_b/models.py) and [`codebase_b/services.py`](../codebase_b/services.py)) was performed to identify three authentic, high-priority Change Requests—strictly one per required ISO/IEC 14764 maintenance category:

| CR ID | Maintenance Category | Title & Summary | Primary Trigger / Driver | Impacted Codebase B Modules | Companion Implementation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CR-01** (`CR-2026-001`) | **Corrective Maintenance** | Canonical ISO-8601 Date Normalization, Domain Exception Containment & Strict Integer-Hour Validation | **Latent Functional Defects:** Non-padded date strings bypass room collision & student quota checks, corrupt confirmation tokens, leak raw `ValueError`, and crash post-persistence on float/bool hours. | `models.py` (exceptions), `services.py` (`PricingService`, `BookingRepository`, `BookingService`) | [`cr1_corrective/`](../cr1_corrective/) |
| **CR-02** (`CR-2026-002`) | **Adaptive Maintenance** | Persistent SQLite3 Relational DBMS Adapter (`sqlite3`) & Timezone-Aware `UTC+08:00` Server Runtime | **External Environment Shift:** Deployment to stateless Linux/Docker campus servers requires ACID disk persistence across restarts (Milestone 1 Sec. 5.3) and deterministic `UTC+08:00` timestamps. | `models.py` (`CAMPUS_TIMEZONE`, `Reservation`), `services.py` (`AbstractBookingRepository`, `SQLiteBookingRepository`) | [`cr2_adaptive/`](../cr2_adaptive/) |
| **CR-03** (`CR-2026-003`) | **Perfective Maintenance** | Attendee Capacity Validation, Best-Fit Room Availability Discovery, Decoupled `NotificationService` & $O(1)$ Indexing | **User Enhancement & Quality Perfection:** Activate unused `Room.capacity` attribute, add best-fit room search, decouple console `print()` I/O (SRP), and optimize $O(N)$ repository scans to $O(1)$. | `models.py` (`CapacityExceededError`, `Reservation.attendees`), `services.py` (`NotificationService`, `BookingRepository`, `BookingService`) | [`cr3_perfective/`](../cr3_perfective/) |

---

### 3.2 CR-01 (Corrective Maintenance): Canonical ISO-8601 Date Normalization & Input Boundary Defect Fix

#### 1. Problem Identification & Root-Cause Code Audit
Although Codebase B is modularly structured, line-by-line inspection of [`codebase_b/services.py`](../codebase_b/services.py) exposed **three severe functional defects** where actual runtime behavior violates Milestone 1's domain specifications:

- **Defect 1A — Double-Booking & 4× Student Daily Quota Bypass via Unnormalized Date Strings:**  
  In `BookingService.create_booking` ([`codebase_b/services.py`](../codebase_b/services.py) lines 172–184), raw `date_str` is queried against `BookingRepository` *before* any date parsing occurs:
  ```python
  # codebase_b/services.py (Lines 171-189) — DEFECTIVE SEQUENCE
  # 3. Collision validation (uses raw unnormalized string equality r.date_str == date_str!)
  existing_room_bookings = self.repo.find_by_room_and_date(room_id, date_str)
  if self.conflict.has_overlap(existing_room_bookings, start_hour, end_hour):
      raise SlotConflictError(...)

  # 4. Student quota validation (uses raw unnormalized string equality!)
  if user.is_student():
      user_bookings = self.repo.find_by_user_and_date(user_id, date_str)
      ...
  # 5. Date is only parsed AFTER collision and quota checks!
  breakdown = self.pricing.calculate(room, user, date_str, duration)
  # 6. Token date segment uses raw string replacement:
  clean_date = date_str.replace("-", "")
  ```
  Because Python's `datetime.strptime(date_str, "%Y-%m-%d")` inside `PricingService.calculate` (line 63) accepts single-digit months and days without error, four distinct strings—`"2026-01-05"`, `"2026-1-05"`, `"2026-01-5"`, and `"2026-1-5"`—all resolve to January 5, 2026! However, `BookingRepository.find_by_room_and_date` (line 132) tests raw string equality (`r.date_str == date_str`). Consequently:
  1. **Physical Room Double-Booking:** User A reserves `R-SR1` on `"2026-01-05"` (10:00–12:00) and User B reserves `R-SR1` on `"2026-1-5"` (10:00–12:00); both succeed without raising `SlotConflictError`!
  2. **4× Student Quota Bypass:** A student limited to 2 hours/day can reserve 8 hours on January 5 by submitting 2-hour bookings across each of the four string representations!
  3. **Specification-Violating Confirmation Token:** Passing `"2026-1-5"` generates `SKD-202615-XXXXXX` (17 characters, ambiguous 6-digit date), violating Milestone 1 Section 1.3's strict 19-character `SKD-YYYYMMDD-XXXXXX` token contract.

- **Defect 1B — Unhandled `ValueError` / `TypeError` Leak Violating Domain Exception Contract:**  
  [`codebase_b/models.py`](../codebase_b/models.py) (line 34) defines `BookingException` as the base exception for all domain errors so callers can catch domain failures uniformly. Yet passing an invalid calendar date such as `"2026-02-30"` or `"12/10/2026"` crashes deep inside `PricingService.calculate` with an uncaught Python `ValueError` instead of a `BookingException` subclass.

- **Defect 1C — Post-Persistence Crash & Corrupted State on Non-Integer Hours (`float` / `bool`):**  
  Python does not enforce type annotations at runtime, and `bool` is a subclass of `int` (`isinstance(True, int) == True`). If a caller passes `start_hour=10.5, end_hour=12` (float), numeric comparisons `10.5 < 8` and `12 > 22` evaluate to `False`, **`self.repo.save_reservation(reservation)` executes at line 204 (persisting the invalid record!)**, and line 208 (`f"{start_hour:02d}"`) subsequently crashes with `ValueError: Unknown format code 'd' for object of type 'float'`, leaving phantom corrupted state in memory!

#### 2. Proposed Corrective Modification & Category Justification
- **Category Proof (Corrective Maintenance):** Under ISO/IEC 14764, corrective maintenance rectifies discovered faults where software behavior deviates from established functional specifications. No new user features or external environment migrations are introduced; existing invariants (collision prevention, 2-hour quota, `SKD-YYYYMMDD-XXXXXX` token format, and `BookingException` encapsulation) are restored.
- **Technical Solution (Implemented in [`cr1_corrective/`](../cr1_corrective/)):**
  1. Introduce `InvalidDateError(BookingException)` and `InvalidTimeSlotError(BookingException)` in [`cr1_corrective/models.py`](../cr1_corrective/models.py).
  2. Implement `parse_and_normalize_date(date_str)` and `_validate_strict_integer_hours(start_hour, end_hour)` (`type(h) is int`, rejecting both `float` and `bool`) at the entry boundary of `BookingService.create_booking` ([`cr1_corrective/services.py`](../cr1_corrective/services.py)), normalizing all dates via `.isoformat()` (`"2026-1-5" -> "2026-01-05"`) *prior* to repository queries, pricing calculation, token generation, and persistence.

---

### 3.3 CR-02 (Adaptive Maintenance): Persistent SQLite3 Relational DBMS Adapter & `UTC+08:00` Server Runtime

#### 1. Environmental Change Identification & Codebase Gap Audit
Milestone 1 Section 5.3 ([`docs/milestone_1_system_design_and_codebases.md`](milestone_1_system_design_and_codebases.md) line 408) explicitly documented Codebase B's primary infrastructure constraint:
> *"In-Memory Volatility: In-memory dictionary storage is maintained for simplicity in Milestone 1; migrating to persistent relational databases (e.g. SQLite / PostgreSQL) will be addressed in subsequent milestones."*

Auditing Codebase B for deployment onto the university's **stateless containerized Linux application server (`ubuntu-latest` / Docker)** revealed two environmental incompatibilities:
1. **Volatile RAM Storage Environment ([`codebase_b/services.py`](../codebase_b/services.py) lines 100–136):** `BookingRepository` stores `_users`, `_rooms`, and `_reservations` inside process-local Python dictionaries. In a containerized microservice, serverless worker, or multi-invocation CLI environment where processes terminate or containers restart, **100% of reservation state is lost on exit**. Furthermore, `BookingService.__init__` is typed directly against the concrete `BookingRepository` class rather than an abstract storage port.
2. **Host-Dependent Naive Timestamp Drift ([`codebase_b/models.py`](../codebase_b/models.py) line 96):** `Reservation.created_at` uses `field(default_factory=datetime.now)`, producing **timezone-naive** timestamps tied to the host OS clock. While campus operating rules (`08:00–22:00`) are governed by Malaysian Campus Standard Time (`Asia/Kuala_Lumpur`, `UTC+08:00`), Linux Docker containers and GitHub Actions runners operate in `UTC+00:00`, introducing an 8-hour audit discrepancy across environments.

#### 2. Proposed Adaptive Modification & Category Justification
- **Category Proof (Adaptive Maintenance):** Under ISO/IEC 14764, adaptive maintenance modifies a software product after delivery to keep it usable in a **changed hardware, OS, cloud/container runtime, or data-storage DBMS environment**. All business policies (operating hours `08:00–22:00`, 2-hour student quota, USD 20 / USD 35 rates, 15% student discount, 20% weekend surcharge) remain 100% unchanged.
- **Technical Solution (Implemented in [`cr2_adaptive/`](../cr2_adaptive/)):**
  1. Define `AbstractBookingRepository(ABC)` in [`cr2_adaptive/services.py`](../cr2_adaptive/services.py) so `BookingService` depends purely on an abstraction (Dependency Inversion Principle, 0 `sqlite3` imports inside `BookingService`).
  2. Implement `SQLiteBookingRepository(AbstractBookingRepository)` utilizing Python's built-in `sqlite3` relational DBMS engine with `PRAGMA foreign_keys = ON`, idempotent schema initialization (`users`, `rooms`, `reservations`), composite relational indexes (`idx_res_room_date`, `idx_res_user_date`), ACID transaction context blocks, deterministic connection lifecycle (`close()` / context manager), and strictly parameterized `?` SQL statements immune to SQL injection.
  3. Define `CAMPUS_TIMEZONE = timezone(timedelta(hours=8), name="UTC+08:00")` and `campus_now()` in [`cr2_adaptive/models.py`](../cr2_adaptive/models.py), ensuring ISO-8601 `UTC+08:00` audit timestamps round-trip identically across Windows workstations and UTC Linux containers.

---

### 3.4 CR-03 (Perfective Maintenance): Attendee Capacity Enforcement, Best-Fit Space Discovery, `NotificationService` & $O(1)$ Indexing

#### 1. Enhancement & Internal Quality Audit of Codebase B
Inspection of Codebase B against stakeholder usability goals (inspired by Skedda) and internal ISO/IEC 25010 performance/maintainability attributes identified three high-value perfection opportunities:
1. **Dormant Domain Attribute (`Room.capacity`) & Missing Space Discovery ([`codebase_b/models.py`](../codebase_b/models.py) line 77):** `Room` encapsulates `capacity: int` (e.g., 15 seats for Computer Vision Lab, 30 seats for Seminar Room Alpha), yet `BookingService.create_booking` never accepts or validates party headcount (`attendees`), permitting unsafe over-capacity reservations. Moreover, users must guess `room_id` values blindly because no availability discovery query exists.
2. **$O(N)$ Full-Table Linear Repository Scans ([`codebase_b/services.py`](../codebase_b/services.py) lines 131–135):**
   ```python
   # codebase_b/services.py (Lines 131-135) — O(N) linear scan across ALL historical bookings
   def find_by_room_and_date(self, room_id: str, date_str: str) -> List[Reservation]:
       return [r for r in self._reservations.values() if r.room_id == room_id and r.date_str == date_str]
   ```
   As semester reservations accumulate ($N = 5,000+$), scanning every historical booking across all dates and rooms on every single conflict check, quota check, and multi-room availability search creates unnecessary quadratic $O(M \times N)$ scaling overhead.
3. **Residual SRP Console I/O Coupling ([`codebase_b/services.py`](../codebase_b/services.py) lines 206–209 & 219):** `BookingService` still executes hardcoded `print("[RECEIPT]...")` calls directly inside `create_booking` and `cancel_booking`, coupling domain orchestration to standard output formatting and polluting console logs during batch operations or automated testing.

#### 2. Proposed Perfective Modification & Category Justification
- **Category Proof (Perfective Maintenance):** Under ISO/IEC 14764 and Lientz & Swanson's taxonomy, perfective maintenance encompasses **user-oriented functional enhancements**, **algorithmic performance optimization**, and **structural maintainability/cohesion improvements**.
- **Technical Solution (Implemented in [`cr3_perfective/`](../cr3_perfective/)):**
  1. Add `CapacityExceededError(BookingException)` and optional `attendees: int = 1` validation against `room.capacity` (preserving 100% backward compatibility with 5-argument callers), alongside `BookingService.find_available_rooms(date_str, start_hour, end_hour, min_capacity=1, room_type=None)` returning conflict-free rooms sorted by best-fit capacity ascending, then hourly rate ascending.
  2. Replace $O(N)$ linear scans in `BookingRepository` with secondary composite hash indexes `_idx_room_date[(room_id, date_str)]` and `_idx_user_date[(user_id, date_str)]`, achieving $O(1)$ bucket lookup (**empirically benchmarked at 1,891× faster** at $N = 5,000$ reservations: `466.31 ms` $\to$ `0.247 ms` per 1,000 lookups).
  3. Extract console output into `AbstractNotificationService` (`ConsoleNotificationService` and `SilentNotificationService`), eliminating I/O coupling from `BookingService` and reducing `create_booking` boolean-branch cyclomatic complexity from $12 \to 9$ (`-25%`).

---

## 4. SMLC Phase Details for Corrective Maintenance (CR-01)

### 4.1 System & Operational Assumptions for CR-01
While detailing the CI-IMLC phase attributes for **CR-01 (`CR-2026-001`)**, the following explicit assumptions are established:
1. **Calendar System Assumption:** All reservation dates follow the proleptic Gregorian calendar represented in ISO-8601 extended date format (`YYYY-MM-DD`); non-zero-padded inputs (e.g., `"2026-1-5"`) and leading/trailing whitespace (`" 2026-01-05 "`) are assumed to be benign user formatting variations that must be canonicalized to `"2026-01-05"` rather than rejected, whereas non-existent calendar dates (`"2026-02-30"`) or non-ISO orderings (`"05/01/2026"`) must be rejected via `InvalidDateError`.
2. **Discrete Hourly Slot Policy Assumption:** Per Milestone 1 Section 1.3, campus facilities are scheduled strictly in discrete whole-hour blocks (`int` values in `[8, 22]`); fractional hours (`10.5`) and boolean literals (`True`/`False`) are assumed to be defective caller inputs rather than half-hour booking requests.
3. **Public Signature Backward-Compatibility Assumption:** Existing downstream consumers (including [`tests/test_booking.py`](../tests/test_booking.py)) invoke `create_booking(user_id, room_id, date_str, start_hour, end_hour)` and expect `BookingException` subclasses on domain validation failures; therefore, the method signature and return type (`Reservation`) must remain unchanged.
4. **In-Memory Baseline Isolation Assumption:** CR-01 is verified in isolation against Codebase B's single-process baseline so corrective defect resolution can be proven independently of CR-02's RDBMS adaptation.

### 4.2 Phase-by-Phase Inputs, Controls, Outputs, and Metrics (CR-01)

| CI-IMLC Phase | Inputs | Controls (Governance & Quality Gates) | Outputs | Quantitative Metrics & Empirical Results |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: CR/MR Triage, Classification & Prioritization** | - Defect report demonstrating double-booking & 4× student quota bypass using `"2026-1-5"` vs `"2026-01-05"`<br>- Stack trace of unhandled `ValueError` in [`codebase_b/services.py`](../codebase_b/services.py) (lines 63 & 208)<br>- Milestone 1 token spec (`SKD-YYYYMMDD-XXXXXX`) | - ISO/IEC 14764 classification checklist confirming *Corrective* category (deviation from existing spec)<br>- Severity rubric: **Critical / P1** (financial quota bypass & physical room double-booking) | - Approved Ticket `CR-2026-001` tagged `type:corrective`, `priority:P1-critical`<br>- Minimal reproducible failure script covering all 3 defect vectors | - **Triage Turnaround Time:** $< 1\text{ hr}$<br>- **Defect Reproducibility Rate:** $100\%$ ($3/3$ fault vectors deterministically reproduced on Codebase B) |
| **Phase 2: Architectural Impact & Ripple Analysis** | - Approved `CR-2026-001` ticket<br>- Baseline [`codebase_b/models.py`](../codebase_b/models.py) & [`codebase_b/services.py`](../codebase_b/services.py)<br>- Baseline 5 Codebase B unit tests in [`tests/test_booking.py`](../tests/test_booking.py) | - Clean Architecture dependency rule (`models.py` must not import `services.py`)<br>- Blast-radius containment: `ConflictDetector` & `User`/`Room` dataclasses must remain untouched ($0$ unnecessary edits) | - Layer Impact Assessment identifying modifications in `models.py` (+2 exception classes) and `services.py` (`parse_and_normalize_date`, `_validate_strict_integer_hours`, canonical repository lookup)<br>- Risk register confirming zero breaking API changes | - **Module Impact Ratio:** $2/3$ core files (`models.py`, `services.py`); `ConflictDetector` churn = $0\text{ SLOC}$<br>- **Public API Breaking Changes:** $0$ |
| **Phase 3: Evolutionary Contract Design & TDD Specification** | - Phase 2 Layer Impact Assessment<br>- `BookingException` hierarchy in `models.py` | - Exception hierarchy rule: all new validation errors (`InvalidDateError`, `InvalidTimeSlotError`) MUST inherit from `BookingException`<br>- Fail-fast validation ordering control: validate & normalize inputs *before* any repository query or state mutation<br>- TDD Red-Green-Refactor mandate | - Contract specification for `parse_and_normalize_date(date_str) -> date` and `type(h) is int` guard<br>- 4 automated TDD test methods in `TestCR1CorrectiveMaintenance` ([`tests/test_milestone2_crs.py`](../tests/test_milestone2_crs.py)) initially failing against baseline defects | - **Equivalence Partition Test Coverage:** $100\%$ across 4 partitions (non-padded ISO variants, invalid calendar dates, `float`/`bool`/`str` hours, token length invariant = $19\text{ chars}$) |
| **Phase 4: Modular Implementation & Static Quality Gate** | - Phase 3 contract design & TDD test specs<br>- Baseline Codebase B modules | - Atomic Git branch/package isolation ([`cr1_corrective/`](../cr1_corrective/))<br>- SonarCloud static gate: $0$ Bugs, $0$ Security Hotspots (`secrets.choice` retained for S2245), $\Delta V(G) \le +2$ on `create_booking` | - Implemented [`cr1_corrective/models.py`](../cr1_corrective/models.py), [`cr1_corrective/services.py`](../cr1_corrective/services.py), [`cr1_corrective/main.py`](../cr1_corrective/main.py)<br>- Clean static AST & SonarCloud inspection pass | - **SLOC Delta:** $354 \to 397\text{ SLOC}$ ($+43\text{ SLOC}$, $+12.1\%$)<br>- **`create_booking` Complexity Drift ($\Delta V(G)$):** $0$ (branch $V(G)$ held steady at $12$ via extracted helpers)<br>- **Phantom Persistence on Error:** $0\text{ records}$ |
| **Phase 5: Automated CI Matrix Regression & Acceptance** | - Phase 4 implemented `cr1_corrective` package<br>- Full `unittest` suite ([`tests/test_booking.py`](../tests/test_booking.py) + [`tests/test_milestone2_crs.py`](../tests/test_milestone2_crs.py))<br>- [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | - Zero-regression mandate: $100\%$ of existing 13 Milestone 1 tests and all CR-01 tests must pass across Python 3.10, 3.11, and 3.12+<br>- Token format invariant check (`^SKD-\d{8}-[A-Z0-9]{6}$`, length $= 19$) | - Passing CI validation log for `python cr1_corrective/main.py` and `unittest` discovery<br>- Verified acceptance sign-off confirming collision & quota bypasses are sealed | - **Automated Test Pass Rate:** $100\%$ ($17/17$ relevant baseline + CR-01 tests; $23/23$ total suite)<br>- **Suite Execution Latency:** $< 0.11\text{ s}$<br>- **Defect Escape Rate:** $0\%$ |
| **Phase 6: Release Delivery, Baseline Migration & Observability** | - Phase 5 CI-verified `cr1_corrective` package<br>- Commit staged on repository | - Semantic Conventional Commit standard (`fix(cr1-corrective): ...`)<br>- Post-release log format check verifying canonical `YYYY-MM-DD` dates in `[RECEIPT]` output | - Atomic Git commit `a06d206` merged to baseline<br>- Updated CI workflow executing CR-01 verification on every push/PR | - **Mean Time To Repair (MTTR):** Single iteration cycle<br>- **Post-Release Token Format Compliance:** $100\%$ ($19$-character `SKD-YYYYMMDD-XXXXXX`) |

---

## 5. SMLC Phase Details for Adaptive Maintenance (CR-02)

### 5.1 Environmental & Infrastructure Assumptions for CR-02
While detailing the CI-IMLC phase attributes for **CR-02 (`CR-2026-002`)**, the following explicit environmental and infrastructure assumptions are stated:
1. **Target Server Filesystem & Volume Assumption:** In production containerized Linux (`ubuntu-latest` / Docker) deployments, the SQLite database file path (e.g., `/var/lib/campus_booking/bookings.sqlite3`) resides on a persistent mounted POSIX/NTFS local volume with read/write file permissions—not an ephemeral container overlayfs or network-mounted NFS share where POSIX `fcntl` locking is unreliable.
2. **Campus Concurrency Envelope Assumption:** Campus facility reservation write throughput operates at moderate institutional concurrency (dozens of transactions per second, single application container writer), well within SQLite3's serialized ACID transaction locking envelope without requiring an external client-server RDBMS daemon such as PostgreSQL.
3. **Standard Library Runtime Availability Assumption:** All target Python 3.10, 3.11, 3.12, and 3.13 environments compile the standard-library C-extension `_sqlite3` with SQLite $\ge 3.35$, maintaining Milestone 1's zero external `pip` dependency constraint.
4. **Fixed Campus Timezone Assumption (`UTC+08:00`):** The university campus operates permanently within Malaysian Standard Time (`Asia/Kuala_Lumpur`, fixed `UTC+08:00` with zero Daylight Saving Time transitions since 1982), allowing `datetime.timezone(datetime.timedelta(hours=8))` to guarantee deterministic cross-OS behavior without requiring external `tzdata` OS packages on minimal container images.

### 5.2 Phase-by-Phase Inputs, Controls, Outputs, and Metrics (CR-02)

| CI-IMLC Phase | Inputs | Controls (Governance & Quality Gates) | Outputs | Quantitative Metrics & Empirical Results |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: CR/MR Triage, Classification & Prioritization** | - Container deployment readiness report & Milestone 1 Section 5.3 roadmap note (*in-memory volatility*)<br>- Audit discrepancy notice on UTC Linux runners vs `UTC+08:00` campus clock | - ISO/IEC 14764 classification check confirming *Adaptive* category (external DBMS storage & container OS clock environment adaptation; $0$ business rule changes)<br>- Priority assignment: **High / P1-Infrastructure** | - Approved Ticket `CR-2026-002` tagged `type:adaptive`, `env:sqlite3-container`<br>- Target environment specification (`Python 3.10-3.13`, `sqlite3`, `UTC+08:00`) | - **Business Policy Churn:** $0\%$ (rates, discounts, surcharges, and quotas strictly invariant)<br>- **External Dependency Count:** $0$ third-party packages |
| **Phase 2: Architectural Impact & Ripple Analysis** | - Approved `CR-2026-002` ticket<br>- Baseline [`codebase_b/models.py`](../codebase_b/models.py) & [`codebase_b/services.py`](../codebase_b/services.py) | - **Dependency Inversion Principle (DIP) Control:** `BookingService`, `PricingService`, and `ConflictDetector` are strictly forbidden from importing `sqlite3` or executing SQL<br>- Cross-OS file-handle control: Windows NTFS requires explicit `conn.close()` before temporary DB file unlinking | - Architectural Port-Adapter Impact Map introducing `AbstractBookingRepository(ABC)` port, `SQLiteBookingRepository` adapter, `InMemoryBookingRepository` adapter, and `CAMPUS_TIMEZONE` clock factory | - **Domain-to-DBMS Coupling:** $0$ `sqlite3` imports inside `BookingService`, `PricingService`, `ConflictDetector`, or `models.py`<br>- **Liskov Substitutability (LSP):** $100\%$ across 8 repository methods |
| **Phase 3: Evolutionary Contract Design & TDD Specification** | - Phase 2 Port-Adapter Impact Map<br>- Domain entity schemas (`User`, `Room`, `Reservation`) | - Relational normalization & referential integrity control (`PRAGMA foreign_keys = ON`, `PRIMARY KEY`, `UNIQUE(token)`, `FOREIGN KEY`)<br>- **Security Control (OWASP / SonarCloud S3649):** $100\%$ parameterized SQL (`?` placeholders); zero f-string SQL interpolation<br>- Schema idempotency control (`CREATE TABLE/INDEX IF NOT EXISTS`) | - Normalized 3-table DDL schema + 2 composite B-tree SQL indexes (`idx_res_room_date`, `idx_res_user_date`)<br>- Context-manager (`__enter__`/`__exit__`) lifecycle contract<br>- 3 TDD persistence, SQL-injection, and DIP parity tests in `TestCR2AdaptiveMaintenance` | - **SQL Parameterization Ratio:** $100\%$ ($9/9$ SQL statements parameterized)<br>- **Relational Index Coverage:** $100\%$ of filter predicates `(room_id, date_str)` and `(user_id, date_str)` indexed |
| **Phase 4: Modular Implementation & Static Quality Gate** | - Phase 3 DDL schema, `AbstractBookingRepository` contract & TDD tests | - Atomic package implementation ([`cr2_adaptive/`](../cr2_adaptive/))<br>- ACID transaction control (`with self._conn:` auto-commit/rollback blocks)<br>- SonarCloud static & security gate (`0` SQL injection vulnerabilities, `0` resource-leak warnings) | - Implemented [`cr2_adaptive/models.py`](../cr2_adaptive/models.py), [`cr2_adaptive/services.py`](../cr2_adaptive/services.py), [`cr2_adaptive/main.py`](../cr2_adaptive/main.py)<br>- `StoragePersistenceError(BookingException)` wrapping low-level `sqlite3.Error` | - **SLOC Delta:** $354 \to 625\text{ SLOC}$ ($+271\text{ SLOC}$ for full relational DDL/DML adapter while `BookingService` complexity $\Delta V(G) = 0$, remaining at $12$) |
| **Phase 5: Automated CI Matrix Regression & Acceptance** | - Phase 4 `cr2_adaptive` package<br>- [`tests/test_milestone2_crs.py`](../tests/test_milestone2_crs.py) & [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | - Cross-restart durability test gate: close Session 1 `sqlite3.Connection`, open fresh Session 2 connection to physical `.sqlite3` file, verify state recovery & cross-restart `SlotConflictError`<br>- Adversarial SQL injection payload test (`"U-999'; DROP TABLE reservations; --"`) | - Passing multi-session durability log (`cr2_adaptive/main.py`)<br>- Passing CI matrix verification across Python 3.10, 3.11, and 3.12+ on Linux & Windows | - **Cross-Restart State Durability:** $100\%$ recovery of bookings, cancellations & `UTC+08:00` offsets<br>- **Cold-Init + ACID Write + Reopen Read Latency:** $98.25\text{ ms}$ ($< 150\text{ ms}$ SLA)<br>- **SQL Injection Exploit Success:** $0\%$ |
| **Phase 6: Release Delivery, Baseline Migration & Observability** | - Phase 5 verified `cr2_adaptive` package<br>- [`.gitignore`](../.gitignore) (`*.sqlite3` exclusion rule) | - Git hygiene control: verify zero temporary `.sqlite3` binary artifacts pollute version control<br>- Semantic commit gate (`feat(cr2-adaptive): ...`) | - Atomic Git commit `cd7c1c3` integrated into repository<br>- Standardized ISO-8601 `+08:00` audit trail in receipt logs (`2026-11-01T...+08:00`) | - **Working Tree Artifact Leakage:** $0$ untracked DB files<br>- **Cross-Environment Timestamp Drift:** $0.0\text{ s}$ (`utcoffset() == +08:00` guaranteed) |

---

## 6. SMLC Phase Details for Perfective Maintenance (CR-03)

### 6.1 Domain, Compatibility & Performance Assumptions for CR-03
While detailing the CI-IMLC phase attributes for **CR-03 (`CR-2026-003`)**, the following explicit assumptions are considered:
1. **Backward-Compatible Default Headcount Assumption:** Legacy callers invoking `create_booking(user_id, room_id, date_str, start_hour, end_hour)` without specifying `attendees` are assumed to represent single-occupant reservations (`attendees: int = 1`), ensuring existing integrations continue functioning without modification so long as `room.capacity >= 1`.
2. **Best-Fit Space Allocation Preference Assumption:** When stakeholders search for available facilities via `find_available_rooms(..., min_capacity=k)`, campus space utilization policy assumes smaller qualifying rooms should be recommended before larger lecture halls (`key=lambda r: (r.capacity, r.hourly_rate, r.room_id)`) to prevent 10-person study groups from monopolizing 30-seat seminar rooms when 15-seat rooms are free.
3. **Synchronous In-Process Notification Assumption:** Consistent with Milestone 1 Section 1.4 (*Scope Shrinkage Rationale*), decoupled notifications via `AbstractNotificationService` execute synchronously in-process (`ConsoleNotificationService` or `SilentNotificationService`) rather than dispatching over external SMTP/webhook network sockets.
4. **Memory-vs-Speed Trade-off Assumption for Secondary Indexes:** Maintaining two secondary hash dictionaries (`_idx_room_date` and `_idx_user_date`) stores object references (pointers) rather than deep copies of `Reservation` dataclasses; the negligible $\sim O(N)$ pointer-reference RAM overhead is assumed acceptable in exchange for reducing slot query time complexity from $O(N)$ to $O(1)$.

### 6.2 Phase-by-Phase Inputs, Controls, Outputs, and Metrics (CR-03)

| CI-IMLC Phase | Inputs | Controls (Governance & Quality Gates) | Outputs | Quantitative Metrics & Empirical Results |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: CR/MR Triage, Classification & Prioritization** | - Stakeholder enhancement proposal for room capacity safety & space discovery<br>- Internal code audit flagging $O(N)$ list scans & `print()` coupling in [`codebase_b/services.py`](../codebase_b/services.py) | - ISO/IEC 14764 classification check confirming *Perfective* category (functional enhancement + algorithmic optimization + SRP structural refinement)<br>- Priority assignment: **Medium-High / P2-Enhancement** | - Approved Ticket `CR-2026-003` tagged `type:perfective`, `focus:ux-perf-srp`<br>- Prioritized acceptance stories for capacity bounds, best-fit search, and silent batch execution | - **Dormant Attribute Utilization:** `Room.capacity` promoted from $0\%$ active enforcement to $100\%$ enforced |
| **Phase 2: Architectural Impact & Ripple Analysis** | - Approved `CR-2026-003` ticket<br>- Baseline [`codebase_b/models.py`](../codebase_b/models.py) & [`codebase_b/services.py`](../codebase_b/services.py) | - **Open/Closed Principle (OCP) Control:** `create_booking` and `BookingService.__init__` must use default parameters (`attendees: int = 1`, `notifier: Optional[AbstractNotificationService] = None`) so existing 3-arg constructor and 5-arg booking calls never break | - Component Enhancement Matrix covering `models.py` (`CapacityExceededError`, `Reservation.attendees`), `NotificationService` hierarchy, indexed `BookingRepository`, and `BookingService.find_available_rooms` | - **Backward Signature Compatibility:** $100\%$ ($0$ existing call sites broken)<br>- **Pricing & Conflict Algorithm Churn:** $0\text{ SLOC}$ modified in `PricingService` or `ConflictDetector` |
| **Phase 3: Evolutionary Contract Design & TDD Specification** | - Phase 2 Component Enhancement Matrix<br>- Algorithmic complexity profile of `BookingRepository` | - Complexity reduction control: extract `_validate_operating_window` and `_validate_capacity` helpers so `create_booking` cyclomatic complexity *decreases* rather than grows<br>- Index consistency invariant: cancelled bookings remain referenced in `_idx_room_date` with `status == CANCELLED` so `r.is_active` filters accurately in $O(1)$ without stale cache desynchronization | - Interface contracts for `AbstractNotificationService`, `find_available_rooms(...) -> List[Room]`, and composite tuple keys `(room_id, date_str)`<br>- 3 TDD test methods in `TestCR3PerfectiveMaintenance` | - **Theoretical Time Complexity Improvement:** `find_by_room_and_date` & `find_by_user_and_date` improved from $O(N) \to O(1)$ amortized ($O(k)$ where $k \le 14$ daily slots) |
| **Phase 4: Modular Implementation & Static Quality Gate** | - Phase 3 interface specifications & TDD tests | - Atomic package implementation ([`cr3_perfective/`](../cr3_perfective/))<br>- SRP I/O control: $0$ `print()` calls permitted inside `BookingService`, `BookingRepository`, `PricingService`, or `ConflictDetector`<br>- SonarCloud static gate ($0$ smells, $0$ duplications) | - Implemented [`cr3_perfective/models.py`](../cr3_perfective/models.py), [`cr3_perfective/services.py`](../cr3_perfective/services.py), [`cr3_perfective/main.py`](../cr3_perfective/main.py) | - **SLOC Delta:** $354 \to 439\text{ SLOC}$ ($+85\text{ SLOC}$)<br>- **`create_booking` Complexity Reduction:** Branch $V(G)$ dropped from $12 \to 9$ (**$-25.0\%$ complexity improvement**)<br>- **Direct `print()` Calls in `BookingService`:** $2 \to 0$ (**$-100\%$ I/O coupling**) |
| **Phase 5: Automated CI Matrix Regression & Acceptance** | - Phase 4 `cr3_perfective` package<br>- [`tests/test_milestone2_crs.py`](../tests/test_milestone2_crs.py) & $N = 5,000$ synthetic benchmark dataset | - Functional acceptance checks: over-capacity rejection, best-fit ordering after booking & cancellation, `room_type` filtering, and $0$-byte `stdout` capture under `SilentNotificationService`<br>- Multi-version CI matrix gate | - Passing CI test run & empirical throughput benchmark comparing Codebase B $O(N)$ vs CR-03 $O(1)$ lookups | - **Empirical Lookup Benchmark ($1,000$ queries @ $N=5,000$ bookings):** $466.31\text{ ms}$ (Codebase B) $\to 0.247\text{ ms}$ (CR-03) = **$1,891\times$ speedup** ($-99.95\%$ latency)<br>- **Stdout Leakage in Silent Mode:** $0\text{ bytes}$ across $120$ bookings |
| **Phase 6: Release Delivery, Baseline Migration & Observability** | - Phase 5 verified `cr3_perfective` package & benchmark metrics | - Semantic commit gate (`feat(cr3-perfective): ...`)<br>- Documentation synchronization in [`README.md`](../README.md) & CI workflow | - Atomic Git commit `338e755` integrated into repository<br>- Enhanced receipt format displaying seat utilization (`Seats: 12/15`) for administrative capacity telemetry | - **End-to-End Automated Suite Health:** $23/23$ tests passing ($100\%$) in $0.109\text{ s}$ |

---

## 7. Cross-CR Synthesis & Empirical Verification Summary

By governing **Codebase B** through the **6-phase CI-Gated Iterative Maintenance Life Cycle (CI-IMLC)** rather than ad-hoc Quick-Fix patching, all three maintenance categories were delivered while actively resisting **Lehman's Second Law (Increasing Complexity)** and **Seventh Law (Declining Quality)**:

| Evaluation Dimension | Codebase B (Milestone 1 Baseline) | CR-01: Corrective (`cr1_corrective/`) | CR-02: Adaptive (`cr2_adaptive/`) | CR-03: Perfective (`cr3_perfective/`) |
| :--- | :--- | :--- | :--- | :--- |
| **ISO/IEC 14764 Category** | Baseline Clean Architecture | **Corrective** (Defect Resolution) | **Adaptive** (Environment Migration) | **Perfective** (UX, SRP & $O(1)$ Speed) |
| **Source Lines of Code (SLOC)** | $354\text{ SLOC}$ (451 total lines) | $397\text{ SLOC}$ ($+43$) | $625\text{ SLOC}$ ($+271$, full SQLite DDL/DML) | $439\text{ SLOC}$ ($+85$) |
| **`create_booking` Branch $V(G)$** | $12$ | $12$ ($\Delta V(G) = 0$) | $12$ ($\Delta V(G) = 0$, $0$ SQL coupling) | **$9$ ($-25.0\%$ complexity reduction)** |
| **Primary Quality / Capability Gain** | Modular SOLID baseline | Eliminates double-booking & 4× quota bypass; strict 19-char tokens & domain exceptions | $100\%$ ACID SQLite3 persistence across container restarts (`98.25 ms`); `UTC+08:00` audit clock | Enforces `Room.capacity`; best-fit room search; $0$ `print()` in `BookingService`; **$1,891\times$ faster lookups** |
| **Automated CI Verification** | 5 baseline Codebase B unit tests | +4 boundary & normalization tests (`OK`) | +3 restart durability, SQLi & DIP tests (`OK`) | +3 capacity, discovery & $O(1)$ load tests (`OK`) |

All **23 automated unit and regression tests** across Milestone 1 and Milestone 2 execute in **`0.109 seconds`** with a **100% pass rate (`OK`)** under Python `unittest` and GitHub Actions CI ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).
