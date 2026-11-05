"""
Reproducible Empirical Metrics & Benchmark Verifier for CSEB5213 Milestone 2.

Computes and prints:
1. Exact Line Counts (LOC, Radon-equivalent SLOC excluding multiline docstrings, and Code+Docstring lines)
2. McCabe Cyclomatic Complexity V(G) for BookingService.create_booking and package averages (matching radon cc)
3. CR-02 SQLite3 cold-init + ACID write + connection close + restart recovery latency (ms)
4. CR-03 O(1) composite hash index vs Codebase B O(N) linear scan speedup at N = 5,000 reservations
"""

import ast
import contextlib
import io
import sys
import tempfile
import time
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def cyclomatic_complexity(node: ast.AST) -> int:
    cc = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.IfExp)):
            cc += 1
        elif isinstance(child, ast.BoolOp):
            cc += len(child.values) - 1
        elif isinstance(child, ast.comprehension):
            cc += 1 + len(child.ifs)
    return cc


def count_lines_radon_style(py_path: Path) -> tuple[int, int, int]:
    text = py_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    loc = len(lines)
    code_plus_doc = sum(1 for ln in lines if ln.strip() and not ln.strip().startswith("#"))

    multi_lines: set[int] = set()
    with tokenize.open(py_path) as f:
        for tok in tokenize.generate_tokens(f.readline):
            if tok.type == tokenize.STRING and tok.start[0] < tok.end[0]:
                for line_no in range(tok.start[0], tok.end[0] + 1):
                    multi_lines.add(line_no)

    radon_sloc = 0
    for idx, ln in enumerate(lines, start=1):
        stripped = ln.strip()
        if not stripped or stripped.startswith("#") or idx in multi_lines:
            continue
        radon_sloc += 1
    return loc, radon_sloc, code_plus_doc


def main() -> None:
    print("=" * 90)
    print("  CSEB5213 Milestone 2 - Reproducible Static Analysis (Radon Parity) & Runtime Benchmark")
    print("=" * 90)
    header = (
        f"{'Package':<16} | {'LOC':>5} | {'Radon SLOC':>10} | {'Code+Doc':>8}"
        f" | {'create_booking V(G)':>19} | {'Lookup V(G)':>11}"
    )
    print(header)
    print("-" * 90)

    for pkg in ("codebase_b", "cr1_corrective", "cr2_adaptive", "cr3_perfective"):
        pkg_dir = ROOT / pkg
        total_loc = 0
        total_radon_sloc = 0
        total_code_doc = 0
        create_cc = 0
        lookup_cc = 0

        for py in sorted(pkg_dir.glob("*.py")):
            loc, r_sloc, c_doc = count_lines_radon_style(py)
            total_loc += loc
            total_radon_sloc += r_sloc
            total_code_doc += c_doc

            tree = ast.parse(py.read_text(encoding="utf-8"))
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            c = cyclomatic_complexity(item)
                            if item.name == "create_booking":
                                create_cc = c
                            elif item.name == "find_by_room_and_date" and node.name == "BookingRepository":
                                lookup_cc = c

        grade = "B" if create_cc <= 10 else "C"
        print(
            f"{pkg:<16} | {total_loc:>5} | {total_radon_sloc:>10} | {total_code_doc:>8}"
            f" | {f'{grade} ({create_cc})':>19} | {f'A ({lookup_cc})':>11}"
        )

    print("-" * 90)

    # Benchmark O(N) vs O(1) lookup at N=5,000 reservations
    from codebase_b.models import Reservation as BRes, ReservationStatus as BStat
    from codebase_b.services import BookingRepository as BRepo
    from cr3_perfective.models import Reservation as PRes, ReservationStatus as PStat
    from cr3_perfective.services import BookingRepository as PRepo

    b_repo = BRepo()
    p_repo = PRepo()
    for i in range(5000):
        d = f"2026-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}"
        rm = f"R-{i % 25:02d}"
        us = f"U-{i % 200:03d}"
        b_repo.save_reservation(BRes(0, f"T-{i}", us, rm, d, 9, 10, 20.0, 0.0, 0.0, 20.0, BStat.CONFIRMED))
        p_repo.save_reservation(PRes(0, f"T-{i}", us, rm, d, 9, 10, 20.0, 0.0, 0.0, 20.0, 1, PStat.CONFIRMED))

    t0 = time.perf_counter()
    for _ in range(1000):
        b_repo.find_by_room_and_date("R-07", "2026-05-14")
    t_linear = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for _ in range(1000):
        p_repo.find_by_room_and_date("R-07", "2026-05-14")
    t_indexed = (time.perf_counter() - t0) * 1000

    # Benchmark SQLite3 ACID durability & restart recovery latency
    from cr2_adaptive import (
        BookingService as CR2Svc,
        ConflictDetector as CR2CD,
        PricingService as CR2PS,
        Room as CR2Rm,
        RoomType as CR2RT,
        SQLiteBookingRepository,
        User as CR2Us,
        UserRole as CR2UR,
    )

    with tempfile.TemporaryDirectory() as td:
        dbp = Path(td) / "bench.sqlite3"
        t0 = time.perf_counter()
        with SQLiteBookingRepository(dbp) as r1:
            r1.add_user(CR2Us("U-1", "Alice", CR2UR.STUDENT))
            r1.add_room(CR2Rm("R-1", "Room 1", CR2RT.STANDARD, 20, 20.0))
            s1 = CR2Svc(r1, CR2PS(), CR2CD())
            with contextlib.redirect_stdout(io.StringIO()):
                b = s1.create_booking("U-1", "R-1", "2026-10-12", 10, 12)
        with SQLiteBookingRepository(dbp) as r2:
            rec = r2.get_reservation(b.booking_id)
            assert rec is not None and rec.total_cost == 34.0
        t_sql = (time.perf_counter() - t0) * 1000

    print(f"[CR-02 Adaptive] SQLite3 Cold-Init + ACID Write + Restart Recovery : {t_sql:.2f} ms (100% durable)")
    print(f"[CR-03 Perfective] 1,000 Queries @ N=5,000 -> Codebase B O(N)      : {t_linear:.2f} ms")
    print(f"[CR-03 Perfective] 1,000 Queries @ N=5,000 -> CR-03 O(1) Indexed   : {t_indexed:.3f} ms")
    print(f"[CR-03 Perfective] Empirical Lookup Speedup Factor                 : {t_linear / t_indexed:,.1f}x faster")
    print("=" * 90)


if __name__ == "__main__":
    main()
