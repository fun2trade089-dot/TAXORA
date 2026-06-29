"""
Deterministic Indian Income Tax slab calculator for FY 2024-25 (AY 2025-26).

This module implements the core tax computation pipeline:
    slab tax → Section 87A rebate → surcharge (with marginal relief) → cess

All calculations are per the Income Tax Act, 1961 as amended by
Finance (No. 2) Act, 2024.

Amounts are in INR (float).  All functions are pure / deterministic —
same inputs will always produce the same outputs.

References:
    - Section 115BAC : New Tax Regime slabs
    - Section 87A    : Rebate for resident individuals
    - Section 2(9)   : Surcharge
    - Section 2(11)  : Health & Education Cess
    - First Schedule : Old Regime slab rates
"""

from __future__ import annotations

from .models import TaxRegime, TaxResult


# =====================================================================
# Slab rate definitions
# =====================================================================

# Old Regime — First Schedule, Part I, Para A of Finance Act
# Categorised by age bracket as on 31-Mar of the FY.

_OLD_SLABS_BELOW_60: list[tuple[float, float, float]] = [
    # (upper_limit, rate, cumulative_tax_at_start_of_slab)
    (2_50_000,  0.00, 0.0),
    (5_00_000,  0.05, 0.0),
    (10_00_000, 0.20, 12_500.0),
    (float("inf"), 0.30, 1_12_500.0),
]

_OLD_SLABS_60_TO_80: list[tuple[float, float, float]] = [
    (3_00_000,  0.00, 0.0),
    (5_00_000,  0.05, 0.0),
    (10_00_000, 0.20, 10_000.0),
    (float("inf"), 0.30, 1_10_000.0),
]

_OLD_SLABS_ABOVE_80: list[tuple[float, float, float]] = [
    (5_00_000,  0.00, 0.0),
    (10_00_000, 0.20, 0.0),
    (float("inf"), 0.30, 1_00_000.0),
]

# New Regime — Section 115BAC(1A) as amended by Finance (No. 2) Act 2024
_NEW_SLABS: list[tuple[float, float, float]] = [
    (3_00_000,   0.00, 0.0),
    (7_00_000,   0.05, 0.0),
    (10_00_000,  0.10, 20_000.0),
    (12_00_000,  0.15, 50_000.0),
    (15_00_000,  0.20, 80_000.0),
    (float("inf"), 0.30, 1_40_000.0),
]


def _compute_slab_tax(
    taxable_income: float,
    slabs: list[tuple[float, float, float]],
) -> dict:
    """Compute tax using the supplied slab table.

    Args:
        taxable_income: Total taxable income in INR (≥ 0).
        slabs:          List of ``(upper_limit, rate, cumulative_tax)`` tuples
                        where *cumulative_tax* is the total tax owed at the
                        lower boundary of the slab.

    Returns:
        dict with keys:
            ``tax``       — total slab tax (float).
            ``slab_wise`` — list of dicts, each with ``slab``, ``rate``,
                            ``taxable_in_slab``, ``tax_in_slab``.
    """
    if taxable_income <= 0:
        return {"tax": 0.0, "slab_wise": []}

    tax = 0.0
    prev_limit = 0.0
    slab_details: list[dict] = []

    for upper, rate, _ in slabs:
        if taxable_income <= prev_limit:
            break

        slab_top = min(taxable_income, upper)
        taxable_in_slab = max(slab_top - prev_limit, 0.0)
        tax_in_slab = taxable_in_slab * rate

        if taxable_in_slab > 0:
            slab_details.append({
                "slab": f"{prev_limit:,.0f} – {upper:,.0f}" if upper != float("inf") else f"Above {prev_limit:,.0f}",
                "rate": f"{rate * 100:.0f}%",
                "taxable_in_slab": round(taxable_in_slab, 2),
                "tax_in_slab": round(tax_in_slab, 2),
            })

        tax += tax_in_slab
        prev_limit = upper

    return {"tax": round(tax, 2), "slab_wise": slab_details}


# =====================================================================
# Public API — Slab Tax Calculators
# =====================================================================

def calculate_tax_old_regime(taxable_income: float, age: int) -> dict:
    """Calculate income tax under the **Old Regime** (First Schedule).

    Slab rates for FY 2024-25:

    **Below 60 years**
        ₹0 – ₹2,50,000       : Nil
        ₹2,50,001 – ₹5,00,000 : 5 %
        ₹5,00,001 – ₹10,00,000: 20 %
        Above ₹10,00,000      : 30 %

    **Senior Citizen (60–80 years)**
        ₹0 – ₹3,00,000       : Nil
        ₹3,00,001 – ₹5,00,000 : 5 %
        ₹5,00,001 – ₹10,00,000: 20 %
        Above ₹10,00,000      : 30 %

    **Super Senior Citizen (80+ years)**
        ₹0 – ₹5,00,000       : Nil
        ₹5,00,001 – ₹10,00,000: 20 %
        Above ₹10,00,000      : 30 %

    Args:
        taxable_income: Taxable income after all deductions (INR).
        age:            Age of the taxpayer as on 31-Mar of the FY.

    Returns:
        dict: ``{"tax": float, "slab_wise": [...], "category": str}``

    References:
        First Schedule, Part I, Paragraph A of the Finance Act.
    """
    if age >= 80:
        slabs = _OLD_SLABS_ABOVE_80
        category = "Super Senior Citizen (80+)"
    elif age >= 60:
        slabs = _OLD_SLABS_60_TO_80
        category = "Senior Citizen (60-80)"
    else:
        slabs = _OLD_SLABS_BELOW_60
        category = "Individual (Below 60)"

    result = _compute_slab_tax(taxable_income, slabs)
    result["category"] = category
    return result


def calculate_tax_new_regime(taxable_income: float) -> dict:
    """Calculate income tax under the **New Regime** — Section 115BAC(1A).

    Slab rates for FY 2024-25 (as amended by Finance (No. 2) Act, 2024):

        ₹0 – ₹3,00,000         : Nil
        ₹3,00,001 – ₹7,00,000   : 5 %
        ₹7,00,001 – ₹10,00,000  : 10 %
        ₹10,00,001 – ₹12,00,000 : 15 %
        ₹12,00,001 – ₹15,00,000 : 20 %
        Above ₹15,00,000        : 30 %

    Note:
        Age-based concessions do **not** apply under the new regime.
        The slabs are uniform for all individuals / HUFs.

    Args:
        taxable_income: Taxable income after standard deduction (INR).

    Returns:
        dict: ``{"tax": float, "slab_wise": [...]}``

    References:
        Section 115BAC(1A) of the Income Tax Act, 1961.
    """
    return _compute_slab_tax(taxable_income, _NEW_SLABS)


# =====================================================================
# Surcharge — Section 2(9) read with Finance Act
# =====================================================================

def calculate_surcharge(
    tax: float,
    total_income: float,
    regime: str = "OLD",
) -> float:
    """Calculate surcharge on income tax with **marginal relief**.

    Surcharge rates (applicable on income tax):
        Total income ₹50 L – ₹1 Cr   : 10 %
        Total income ₹1 Cr – ₹2 Cr   : 15 %
        Total income ₹2 Cr – ₹5 Cr   : 25 %
        Total income above ₹5 Cr      : 37 % (Old) / 25 % (New — capped)

    **Marginal Relief**:
        The surcharge is limited so that the *incremental* tax + surcharge
        does not exceed the *incremental* income above the threshold.
        i.e.  (tax + surcharge) ≤ tax_at_threshold + (income − threshold).

    Under the **New Regime**, the maximum surcharge rate is capped at
    25 % irrespective of total income (Section 115BAC proviso).

    Args:
        tax:          Income tax amount (before surcharge).
        total_income: Total income (before deductions) for surcharge-
                      bracket determination.
        regime:       ``"OLD"`` or ``"NEW"``.

    Returns:
        Surcharge amount in INR (float).

    References:
        Section 2(9) of the IT Act; Finance Act, 2024 — First Schedule,
        Part III (surcharge on income tax).
    """
    if tax <= 0 or total_income <= 50_00_000:
        return 0.0

    # Determine applicable surcharge rate
    if total_income <= 1_00_00_000:
        rate = 0.10
        threshold = 50_00_000
    elif total_income <= 2_00_00_000:
        rate = 0.15
        threshold = 1_00_00_000
    elif total_income <= 5_00_00_000:
        rate = 0.25
        threshold = 2_00_00_000
    else:
        # New regime caps surcharge at 25 %
        rate = 0.25 if regime == "NEW" else 0.37
        threshold = 5_00_00_000

    surcharge = round(tax * rate, 2)

    # --- Marginal Relief ---
    # Recompute tax at the threshold to check marginal relief
    if regime == "NEW":
        tax_at_threshold_result = calculate_tax_new_regime(threshold)
    else:
        # Use below-60 slabs for marginal-relief calculation
        # (conservative; actual age-based slabs would give same or lower tax)
        tax_at_threshold_result = calculate_tax_old_regime(threshold, age=50)

    tax_at_threshold = tax_at_threshold_result["tax"]

    # Surcharge on the threshold tax (recursive for lower brackets)
    surcharge_at_threshold = _surcharge_at_threshold(tax_at_threshold, threshold, regime)

    total_at_current = tax + surcharge
    total_at_threshold = tax_at_threshold + surcharge_at_threshold
    excess_income = total_income - threshold

    # Marginal relief: total liability should not exceed
    # threshold liability + excess income
    if total_at_current > total_at_threshold + excess_income:
        surcharge = round(total_at_threshold + excess_income - tax, 2)
        surcharge = max(surcharge, 0.0)

    return round(surcharge, 2)


def _surcharge_at_threshold(
    tax: float,
    threshold: float,
    regime: str,
) -> float:
    """Compute surcharge applicable at the exact threshold income.

    This is a helper for marginal relief computation.  At the threshold
    boundary, no surcharge of the *current* bracket applies — only
    lower-bracket surcharges.
    """
    if threshold <= 50_00_000:
        return 0.0
    if threshold <= 1_00_00_000:
        # At ₹50 L threshold, no surcharge
        return 0.0
    if threshold <= 2_00_00_000:
        # At ₹1 Cr threshold, the applicable bracket is 10 %
        return round(tax * 0.10, 2)
    if threshold <= 5_00_00_000:
        # At ₹2 Cr threshold, the applicable bracket is 15 %
        return round(tax * 0.15, 2)
    # At ₹5 Cr threshold, the applicable bracket is 25 %
    return round(tax * 0.25, 2)


# =====================================================================
# Health & Education Cess — Section 2(11)
# =====================================================================

def calculate_cess(tax_plus_surcharge: float) -> float:
    """Calculate Health & Education Cess at **4 %**.

    Cess is levied on (income tax + surcharge).

    Args:
        tax_plus_surcharge: Sum of income tax and surcharge (INR).

    Returns:
        Cess amount in INR (float).

    References:
        Section 2(11) of the IT Act; Finance Act, 2018 — Section 3
        (introduced 4 % H&E Cess replacing 3 % Cess).
    """
    if tax_plus_surcharge <= 0:
        return 0.0
    return round(tax_plus_surcharge * 0.04, 2)


# =====================================================================
# Section 87A Rebate
# =====================================================================

def apply_section_87a_rebate(
    tax: float,
    taxable_income: float,
    regime: str,
) -> float:
    """Apply rebate under **Section 87A** of the Income Tax Act.

    Eligibility & limits for FY 2024-25:

    **Old Regime**:
        - Available if taxable income ≤ ₹5,00,000.
        - Maximum rebate: ₹12,500.

    **New Regime** (Section 115BAC):
        - Available if taxable income ≤ ₹7,00,000.
        - Maximum rebate: ₹25,000.

    The rebate cannot exceed the actual tax payable.

    Note:
        Rebate is available only to **Resident Individuals**.
        (This function does not check residency; the caller must ensure.)

    Args:
        tax:             Slab tax before rebate (INR).
        taxable_income:  Total taxable income after deductions (INR).
        regime:          ``"OLD"`` or ``"NEW"``.

    Returns:
        Tax after applying the rebate (INR, ≥ 0).

    References:
        Section 87A of the Income Tax Act, 1961.
    """
    if regime == "NEW":
        if taxable_income <= 7_00_000:
            rebate = min(tax, 25_000)
            return round(max(tax - rebate, 0.0), 2)
    else:  # OLD
        if taxable_income <= 5_00_000:
            rebate = min(tax, 12_500)
            return round(max(tax - rebate, 0.0), 2)

    return round(tax, 2)


# =====================================================================
# Orchestrator — Full Tax Computation Pipeline
# =====================================================================

def compute_total_tax(
    taxable_income: float,
    total_income: float,
    age: int,
    regime: str,
) -> TaxResult:
    """End-to-end tax computation for a single regime.

    Pipeline:
        1. **Slab tax** — ``calculate_tax_old_regime`` or
           ``calculate_tax_new_regime`` based on ``regime``.
        2. **Section 87A rebate** — reduces slab tax to zero if income
           is within rebate thresholds.
        3. **Surcharge** — computed on the post-rebate tax with marginal
           relief.
        4. **Health & Education Cess** — 4 % on (tax + surcharge).
        5. **Total** — tax + surcharge + cess.

    Args:
        taxable_income: Income after deductions / exemptions (INR).
        total_income:   Total income *before* deductions — used for
                        surcharge bracket determination.
        age:            Age as on 31-Mar of the FY.
        regime:         ``"OLD"`` or ``"NEW"``.

    Returns:
        ``TaxResult`` with the complete computation breakdown.

    Example::

        >>> result = compute_total_tax(
        ...     taxable_income=12_00_000,
        ...     total_income=15_00_000,
        ...     age=35,
        ...     regime="NEW",
        ... )
        >>> result.total_tax  # doctest: +SKIP
        ...

    References:
        Sections 115BAC, 87A, 2(9), 2(11) of the IT Act.
    """
    # ------------------------------------------------------------------
    # Step 1: Slab tax
    # ------------------------------------------------------------------
    if regime == "NEW":
        slab_result = calculate_tax_new_regime(taxable_income)
    else:
        slab_result = calculate_tax_old_regime(taxable_income, age)

    slab_tax = slab_result["tax"]

    # ------------------------------------------------------------------
    # Step 2: Section 87A rebate
    # ------------------------------------------------------------------
    tax_after_rebate = apply_section_87a_rebate(slab_tax, taxable_income, regime)
    rebate_amount = round(slab_tax - tax_after_rebate, 2)

    # ------------------------------------------------------------------
    # Step 3: Surcharge (with marginal relief)
    # ------------------------------------------------------------------
    surcharge = calculate_surcharge(tax_after_rebate, total_income, regime)
    tax_plus_surcharge = round(tax_after_rebate + surcharge, 2)

    # ------------------------------------------------------------------
    # Step 4: Health & Education Cess @ 4 %
    # ------------------------------------------------------------------
    cess = calculate_cess(tax_plus_surcharge)

    # ------------------------------------------------------------------
    # Step 5: Total tax payable
    # ------------------------------------------------------------------
    total_tax = round(tax_plus_surcharge + cess, 2)

    # Build breakdown dict
    breakdown: dict = {
        "slab_wise": slab_result.get("slab_wise", []),
        "slab_tax": slab_tax,
        "rebate_87a": rebate_amount,
        "tax_after_rebate": tax_after_rebate,
        "surcharge": surcharge,
        "tax_plus_surcharge": tax_plus_surcharge,
        "cess": cess,
        "total_tax": total_tax,
    }

    if "category" in slab_result:
        breakdown["category"] = slab_result["category"]

    return TaxResult(
        gross_total_income=round(total_income, 2),
        total_deductions=round(max(total_income - taxable_income, 0.0), 2),
        taxable_income=round(taxable_income, 2),
        tax_before_cess=tax_plus_surcharge,
        surcharge=surcharge,
        cess=cess,
        total_tax=total_tax,
        regime=TaxRegime(regime),
        breakdown=breakdown,
    )


# =====================================================================
# Test harness
# =====================================================================

if __name__ == "__main__":
    import json

    SEPARATOR = "=" * 72

    def _print_result(label: str, result: TaxResult) -> None:
        print(f"\n{SEPARATOR}")
        print(f"  {label}")
        print(SEPARATOR)
        print(f"  Regime             : {result.regime.value}")
        print(f"  Gross Total Income : ₹{result.gross_total_income:>14,.2f}")
        print(f"  Deductions         : ₹{result.total_deductions:>14,.2f}")
        print(f"  Taxable Income     : ₹{result.taxable_income:>14,.2f}")
        print(f"  Slab Tax           : ₹{result.breakdown.get('slab_tax', 0):>14,.2f}")
        print(f"  Rebate u/s 87A     : ₹{result.breakdown.get('rebate_87a', 0):>14,.2f}")
        print(f"  Tax after Rebate   : ₹{result.breakdown.get('tax_after_rebate', 0):>14,.2f}")
        print(f"  Surcharge          : ₹{result.surcharge:>14,.2f}")
        print(f"  Cess (4%)          : ₹{result.cess:>14,.2f}")
        print(f"  TOTAL TAX          : ₹{result.total_tax:>14,.2f}")
        print()
        print("  Slab-wise breakdown:")
        for slab in result.breakdown.get("slab_wise", []):
            print(f"    {slab['slab']:>30s}  @{slab['rate']:>4s}  "
                  f"= ₹{slab['tax_in_slab']:>12,.2f}")
        print()

    # ------------------------------------------------------------------
    # Test Case 1: Salaried individual, ₹10 L income, age 35
    # ------------------------------------------------------------------
    r1_new = compute_total_tax(
        taxable_income=10_00_000,
        total_income=12_00_000,
        age=35,
        regime="NEW",
    )
    _print_result("Test 1 — ₹10 L Taxable, Age 35, NEW Regime", r1_new)

    r1_old = compute_total_tax(
        taxable_income=10_00_000,
        total_income=12_00_000,
        age=35,
        regime="OLD",
    )
    _print_result("Test 1 — ₹10 L Taxable, Age 35, OLD Regime", r1_old)

    # ------------------------------------------------------------------
    # Test Case 2: Income within rebate limit — ₹7 L (NEW), ₹5 L (OLD)
    # ------------------------------------------------------------------
    r2_new = compute_total_tax(
        taxable_income=7_00_000,
        total_income=7_00_000,
        age=30,
        regime="NEW",
    )
    _print_result("Test 2 — ₹7 L Taxable, Age 30, NEW Regime (Rebate)", r2_new)
    assert r2_new.total_tax == 0.0, f"Expected zero tax, got {r2_new.total_tax}"

    r2_old = compute_total_tax(
        taxable_income=5_00_000,
        total_income=5_00_000,
        age=30,
        regime="OLD",
    )
    _print_result("Test 2 — ₹5 L Taxable, Age 30, OLD Regime (Rebate)", r2_old)
    assert r2_old.total_tax == 0.0, f"Expected zero tax, got {r2_old.total_tax}"

    # ------------------------------------------------------------------
    # Test Case 3: Senior Citizen, ₹8 L, OLD Regime
    # ------------------------------------------------------------------
    r3 = compute_total_tax(
        taxable_income=8_00_000,
        total_income=8_00_000,
        age=65,
        regime="OLD",
    )
    _print_result("Test 3 — ₹8 L Taxable, Age 65 (Senior), OLD Regime", r3)

    # ------------------------------------------------------------------
    # Test Case 4: Super Senior Citizen, ₹12 L, OLD Regime
    # ------------------------------------------------------------------
    r4 = compute_total_tax(
        taxable_income=12_00_000,
        total_income=12_00_000,
        age=85,
        regime="OLD",
    )
    _print_result("Test 4 — ₹12 L Taxable, Age 85 (Super Senior), OLD Regime", r4)

    # ------------------------------------------------------------------
    # Test Case 5: High income — ₹60 L, surcharge bracket
    # ------------------------------------------------------------------
    r5_old = compute_total_tax(
        taxable_income=60_00_000,
        total_income=60_00_000,
        age=45,
        regime="OLD",
    )
    _print_result("Test 5 — ₹60 L Taxable, Age 45, OLD Regime (Surcharge)", r5_old)

    r5_new = compute_total_tax(
        taxable_income=60_00_000,
        total_income=60_00_000,
        age=45,
        regime="NEW",
    )
    _print_result("Test 5 — ₹60 L Taxable, Age 45, NEW Regime (Surcharge)", r5_new)

    # ------------------------------------------------------------------
    # Test Case 6: Zero income
    # ------------------------------------------------------------------
    r6 = compute_total_tax(
        taxable_income=0,
        total_income=0,
        age=30,
        regime="NEW",
    )
    _print_result("Test 6 — Zero Income", r6)
    assert r6.total_tax == 0.0, f"Expected zero tax, got {r6.total_tax}"

    # ------------------------------------------------------------------
    # Test Case 7: ₹1.5 Cr income — higher surcharge bracket
    # ------------------------------------------------------------------
    r7_old = compute_total_tax(
        taxable_income=1_50_00_000,
        total_income=1_50_00_000,
        age=40,
        regime="OLD",
    )
    _print_result("Test 7 — ₹1.5 Cr Taxable, Age 40, OLD Regime", r7_old)

    r7_new = compute_total_tax(
        taxable_income=1_50_00_000,
        total_income=1_50_00_000,
        age=40,
        regime="NEW",
    )
    _print_result("Test 7 — ₹1.5 Cr Taxable, Age 40, NEW Regime", r7_new)

    print(f"\n{SEPARATOR}")
    print("  ✅ All test cases executed successfully.")
    print(SEPARATOR)
