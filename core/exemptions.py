"""
Exemption Calculator — Section 10 of the Income Tax Act, 1961.

Implements deterministic computation of salary-related exemptions
for FY 2024-25 (AY 2025-26).

Every function returns a dict with at minimum:
    - amount            : the exempt amount (float)
    - section_reference : statutory citation (str)
    - explanation       : human-readable narrative (str)

References:
    - Section 10(13A) read with Rule 2A — HRA exemption
    - Section 10(5) — Leave Travel Allowance / Concession
    - Section 16(ia) — Standard Deduction (technically under Section 16,
      included here for convenience as a salary deduction)
    - Finance (No. 2) Act, 2024 (Budget 2024 amendments)
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Constants — FY 2024-25
# ---------------------------------------------------------------------------

STANDARD_DEDUCTION_OLD: float = 50_000.0
"""Standard deduction under OLD regime: ₹50,000 (Section 16(ia))."""

STANDARD_DEDUCTION_NEW: float = 75_000.0
"""Standard deduction under NEW regime: ₹75,000 (w.e.f. FY 2024-25, Budget 2024)."""

HRA_METRO_PCT: float = 0.50
"""HRA exemption percentage for metro cities (Delhi, Mumbai, Kolkata, Chennai): 50%."""

HRA_NON_METRO_PCT: float = 0.40
"""HRA exemption percentage for non-metro cities: 40%."""


# ---------------------------------------------------------------------------
# Section 10(13A) r/w Rule 2A — HRA Exemption
# ---------------------------------------------------------------------------

def calculate_hra_exemption(
    basic: float,
    da: float,
    hra_received: float,
    rent_paid: float,
    is_metro: bool,
) -> dict[str, Any]:
    """Calculate HRA exemption under Section 10(13A) read with Rule 2A.

    The exempt portion of House Rent Allowance is the MINIMUM of:
        (a) Actual HRA received from the employer
        (b) 50% of (Basic + DA) if the employee resides in a metro city
            (Delhi, Mumbai, Kolkata, Chennai); 40% otherwise
        (c) Rent paid minus 10% of (Basic + DA)

    The taxable HRA = HRA received − exempt amount.

    Pre-conditions (not enforced in this function):
        - The assessee must be a salaried employee receiving HRA.
        - The assessee must actually pay rent for a residential accommodation.
        - An assessee claiming HRA exemption CANNOT simultaneously claim
          deduction under Section 80GG.

    Args:
        basic:        Basic salary for the financial year.
        da:           Dearness Allowance for the financial year.
        hra_received: Actual HRA received from the employer.
        rent_paid:    Total rent paid during the financial year.
        is_metro:     True if the employee resides in a metro city.

    Returns:
        dict with exempt_amount, taxable_hra, formula_breakdown,
        amount, section_reference, explanation.
    """
    basic_plus_da = basic + da
    pct = HRA_METRO_PCT if is_metro else HRA_NON_METRO_PCT

    option_a = hra_received
    option_b = basic_plus_da * pct
    option_c = rent_paid - (basic_plus_da * 0.10)

    # Exempt amount cannot be negative
    exempt = max(0.0, min(option_a, option_b, option_c))
    taxable = max(0.0, hra_received - exempt)

    metro_label = "metro (50%)" if is_metro else "non-metro (40%)"

    return {
        "amount": exempt,
        "exempt_amount": exempt,
        "taxable_hra": taxable,
        "formula_breakdown": {
            "basic": basic,
            "da": da,
            "basic_plus_da": basic_plus_da,
            "hra_received": hra_received,
            "rent_paid": rent_paid,
            "is_metro": is_metro,
            "a_actual_hra": option_a,
            "b_pct_of_basic_da": option_b,
            "c_rent_minus_10pct": option_c,
            "minimum": exempt,
        },
        "section_reference": "Section 10(13A) read with Rule 2A",
        "explanation": (
            f"Basic+DA: ₹{basic_plus_da:,.0f}. HRA received: ₹{hra_received:,.0f}. "
            f"Rent paid: ₹{rent_paid:,.0f}. City: {metro_label}. "
            f"(a) Actual HRA = ₹{option_a:,.0f}; "
            f"(b) {pct:.0%} of Basic+DA = ₹{option_b:,.0f}; "
            f"(c) Rent − 10% of Basic+DA = ₹{option_c:,.0f}. "
            f"Exempt (minimum) = ₹{exempt:,.0f}. "
            f"Taxable HRA = ₹{taxable:,.0f}."
        ),
    }


# ---------------------------------------------------------------------------
# Section 16(ia) — Standard Deduction
# ---------------------------------------------------------------------------

def calculate_standard_deduction(regime: str) -> dict[str, Any]:
    """Return the standard deduction on salary income.

    FY 2024-25 values (post-Budget 2024):
        - Old regime: ₹50,000  (Section 16(ia), introduced FY 2018-19)
        - New regime: ₹75,000  (enhanced from ₹50,000 by Budget 2024)

    The standard deduction is available to all salaried employees and
    pensioners irrespective of actual expenditure.

    Args:
        regime: Tax regime — must be one of ``"old"`` or ``"new"``
                (case-insensitive).

    Returns:
        dict with amount, section_reference, explanation.

    Raises:
        ValueError: If *regime* is not ``"old"`` or ``"new"``.
    """
    regime_lower = regime.strip().lower()
    if regime_lower == "old":
        amount = STANDARD_DEDUCTION_OLD
    elif regime_lower == "new":
        amount = STANDARD_DEDUCTION_NEW
    else:
        raise ValueError(
            f"Invalid regime '{regime}'. Must be 'old' or 'new'."
        )

    return {
        "amount": amount,
        "regime": regime_lower,
        "section_reference": "Section 16(ia)",
        "explanation": (
            f"Standard deduction under {regime_lower} regime: ₹{amount:,.0f}. "
            f"{'(Enhanced to ₹75,000 by Budget 2024)' if regime_lower == 'new' else '(₹50,000 since FY 2018-19)'}"
        ),
    }


# ---------------------------------------------------------------------------
# Section 10(5) — Leave Travel Allowance / Concession
# ---------------------------------------------------------------------------

def calculate_lta_exemption(
    lta_received: float,
    actual_travel: float,
) -> dict[str, Any]:
    """Calculate LTA exemption under Section 10(5).

    Leave Travel Allowance (LTA) / Leave Travel Concession (LTC) is
    exempt to the extent of ACTUAL travel expenditure incurred on
    domestic travel (within India only).

    Key rules:
        - Only travel fare is covered (boarding, lodging, local conveyance
          are NOT exempt).
        - Economy class air fare / AC first class rail fare is the upper
          limit for travel by those modes.
        - Available for 2 journeys in a block of 4 calendar years.
          Block year 2022-25 is the current block.
        - Family includes spouse, children (max 2 born after 01-Oct-1998),
          and dependent parents/siblings.

    The exempt amount = minimum of LTA received and actual travel cost.

    Args:
        lta_received:  LTA component received from the employer.
        actual_travel: Actual eligible domestic travel cost incurred.

    Returns:
        dict with amount, section_reference, explanation.
    """
    exempt = max(0.0, min(lta_received, actual_travel))
    taxable = max(0.0, lta_received - exempt)

    return {
        "amount": exempt,
        "exempt_amount": exempt,
        "taxable_lta": taxable,
        "lta_received": lta_received,
        "actual_travel": actual_travel,
        "section_reference": "Section 10(5)",
        "explanation": (
            f"LTA received: ₹{lta_received:,.0f}. "
            f"Actual travel cost: ₹{actual_travel:,.0f}. "
            f"Exempt = min(received, actual) = ₹{exempt:,.0f}. "
            f"Taxable LTA = ₹{taxable:,.0f}. "
            f"(Current block: 2022-25. Only domestic travel fare is eligible.)"
        ),
    }


# ---------------------------------------------------------------------------
# Quick-Test Harness
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 72)
    print("SECTION 10 EXEMPTION CALCULATOR — Test Cases (FY 2024-25)")
    print("=" * 72)

    # --- Test 1: HRA metro ---
    r = calculate_hra_exemption(
        basic=600_000, da=60_000, hra_received=300_000,
        rent_paid=360_000, is_metro=True,
    )
    # (a) 300K, (b) 50% of 660K = 330K, (c) 360K - 66K = 294K → min = 294K
    assert r["exempt_amount"] == 294_000.0, f"FAIL: {r['exempt_amount']}"
    assert r["taxable_hra"] == 6_000.0
    print(f"[PASS] HRA metro:     {r['explanation']}")

    # --- Test 2: HRA non-metro ---
    r = calculate_hra_exemption(
        basic=600_000, da=60_000, hra_received=300_000,
        rent_paid=360_000, is_metro=False,
    )
    # (a) 300K, (b) 40% of 660K = 264K, (c) 294K → min = 264K
    assert r["exempt_amount"] == 264_000.0, f"FAIL: {r['exempt_amount']}"
    print(f"[PASS] HRA non-metro: {r['explanation']}")

    # --- Test 3: HRA with low rent ---
    r = calculate_hra_exemption(
        basic=500_000, da=0, hra_received=200_000,
        rent_paid=60_000, is_metro=True,
    )
    # (a) 200K, (b) 250K, (c) 60K - 50K = 10K → min = 10K
    assert r["exempt_amount"] == 10_000.0, f"FAIL: {r['exempt_amount']}"
    print(f"[PASS] HRA low rent:  {r['explanation']}")

    # --- Test 4: Standard deduction old ---
    r = calculate_standard_deduction("old")
    assert r["amount"] == 50_000.0
    print(f"[PASS] Std ded old:   {r['explanation']}")

    # --- Test 5: Standard deduction new ---
    r = calculate_standard_deduction("new")
    assert r["amount"] == 75_000.0
    print(f"[PASS] Std ded new:   {r['explanation']}")

    # --- Test 6: LTA fully exempt ---
    r = calculate_lta_exemption(40_000, 55_000)
    assert r["exempt_amount"] == 40_000.0
    print(f"[PASS] LTA full:      {r['explanation']}")

    # --- Test 7: LTA partially taxable ---
    r = calculate_lta_exemption(50_000, 30_000)
    assert r["exempt_amount"] == 30_000.0
    assert r["taxable_lta"] == 20_000.0
    print(f"[PASS] LTA partial:   {r['explanation']}")

    print("\n✅ All exemption tests passed.")
