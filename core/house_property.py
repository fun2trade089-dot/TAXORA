"""
Income from House Property Calculator — Sections 22–27 of the Income Tax Act, 1961.

Implements deterministic computation of income (or loss) from house property
for FY 2024-25 (AY 2025-26).

Key provisions modelled:
    - Section 22  : Chargeability of income from house property
    - Section 23  : Annual value — self-occupied (deemed nil) vs let-out
    - Section 23(2): At most TWO properties may be declared self-occupied
                     (amendment effective from FY 2019-20)
    - Section 24(a): Standard deduction — 30 % of NAV (let-out only)
    - Section 24(b): Interest on borrowed capital
        • Self-occupied  — capped at ₹2,00,000
        • Let-out         — NO cap
    - Section 24(b) proviso: Pre-construction interest deductible in
                             five equal annual instalments from the year
                             of completion
    - Section 71(3A): Set-off of loss from house property against other
                      heads capped at ₹2,00,000 per year
    - Section 71B   : Unabsorbed loss carried forward for 8 AYs

Every function returns a dict containing at minimum:
    - amount            : net income / loss (float, INR)
    - section_reference : statutory citation (str)
    - explanation       : human-readable narrative (str)

References:
    - Income Tax Act, 1961 — Sections 22–27, 71(3A), 71B
    - Finance Act, 2017 (introduced ₹2 L set-off cap)
    - Finance Act, 2019 (allowed two SOPs from FY 2019-20)
    - Finance (No. 2) Act, 2024
"""

from __future__ import annotations

from typing import Any

from .models import HousePropertyIncome


# ---------------------------------------------------------------------------
# Constants — FY 2024-25
# ---------------------------------------------------------------------------

STANDARD_DEDUCTION_RATE: float = 0.30
"""Section 24(a): Standard deduction at 30 % of Net Annual Value."""

SELF_OCCUPIED_INTEREST_CAP: float = 200_000.0
"""Section 24(b): Interest cap for self-occupied property — ₹2,00,000.
   (₹30,000 if loan taken before 01-Apr-1999 or not for acquisition /
   construction, but we default to ₹2,00,000 for post-1999 acquisition.)"""

LOSS_SETOFF_CAP: float = 200_000.0
"""Section 71(3A): Maximum HP loss that may be set off against other
   income heads in a single year — ₹2,00,000."""

CARRY_FORWARD_YEARS: int = 8
"""Section 71B: Unabsorbed HP loss may be carried forward for 8 AYs."""

MAX_SELF_OCCUPIED: int = 2
"""Section 23(2) (post FY 2019-20): At most TWO properties may be
   treated as self-occupied. Any additional self-occupied property is
   deemed let-out for computation purposes."""

PRE_CONSTRUCTION_AMORTISATION_YEARS: int = 5
"""Section 24(b) proviso: Pre-construction interest is deductible in
   five equal annual instalments starting from the year of completion."""


# ---------------------------------------------------------------------------
# Validation & Normalisation
# ---------------------------------------------------------------------------

def _validate_and_parse(
    raw_properties: list[dict[str, Any]],
) -> list[HousePropertyIncome]:
    """Parse raw property dicts into validated Pydantic models.

    Also enforces the two-SOP limit under Section 23(2). If more than two
    properties are flagged ``self_occupied=True``, the excess are silently
    flipped to let-out (preserving the order — the first two remain SOP).

    Args:
        raw_properties: List of dicts matching ``HousePropertyIncome`` fields.

    Returns:
        List of validated ``HousePropertyIncome`` instances.
    """
    parsed: list[HousePropertyIncome] = []
    sop_count = 0

    for raw in raw_properties:
        prop = HousePropertyIncome(**raw)

        if prop.self_occupied:
            sop_count += 1
            if sop_count > MAX_SELF_OCCUPIED:
                # Excess SOP → treated as deemed let-out u/s 23(4)
                prop = prop.model_copy(update={"self_occupied": False})

        parsed.append(prop)

    return parsed


# ---------------------------------------------------------------------------
# Single-Property Computation
# ---------------------------------------------------------------------------

def _compute_single_property(
    prop: HousePropertyIncome,
    index: int,
) -> dict[str, Any]:
    """Compute income from a single house property.

    Args:
        prop:  Validated ``HousePropertyIncome`` model instance.
        index: 0-based property index (for display purposes).

    Returns:
        dict with full computation breakdown for ONE property.
    """
    # Pre-construction interest — 1/5th instalment for the current year
    pre_construction_yearly = prop.pre_construction_interest / PRE_CONSTRUCTION_AMORTISATION_YEARS

    if prop.self_occupied:
        # -----------------------------------------------------------------
        # Self-Occupied Property — Section 23(2)
        # -----------------------------------------------------------------
        nav = 0.0
        standard_deduction = 0.0  # 30 % of 0

        # Total interest claim = regular interest + 1/5th pre-construction
        total_interest_claimed = prop.home_loan_interest + pre_construction_yearly

        # Section 24(b) cap of ₹2,00,000 for self-occupied
        interest_deduction = min(total_interest_claimed, SELF_OCCUPIED_INTEREST_CAP)

        net_income = nav - interest_deduction  # always ≤ 0

        return {
            "property_index": index,
            "property_type": "self_occupied",
            "gross_annual_value": 0.0,
            "municipal_taxes": 0.0,
            "net_annual_value": nav,
            "standard_deduction_24a": standard_deduction,
            "home_loan_interest_claimed": prop.home_loan_interest,
            "pre_construction_interest_total": prop.pre_construction_interest,
            "pre_construction_interest_yearly": round(pre_construction_yearly, 2),
            "total_interest_claimed": round(total_interest_claimed, 2),
            "interest_deduction_24b": round(interest_deduction, 2),
            "net_income": round(net_income, 2),
            "amount": round(net_income, 2),
            "section_reference": "Sections 23(2), 24(a), 24(b)",
            "explanation": (
                f"Property #{index + 1} (self-occupied): "
                f"NAV = ₹0 (deemed nil u/s 23(2)). "
                f"Home-loan interest: ₹{prop.home_loan_interest:,.0f}, "
                f"pre-construction interest (1/5th of "
                f"₹{prop.pre_construction_interest:,.0f}): "
                f"₹{pre_construction_yearly:,.0f}. "
                f"Total interest claimed: ₹{total_interest_claimed:,.0f}, "
                f"capped at ₹{SELF_OCCUPIED_INTEREST_CAP:,.0f} u/s 24(b). "
                f"Allowed interest deduction: ₹{interest_deduction:,.0f}. "
                f"Net HP income = ₹{net_income:,.0f}."
            ),
        }

    else:
        # -----------------------------------------------------------------
        # Let-Out (or Deemed Let-Out) Property — Section 23(1) / 23(4)
        # -----------------------------------------------------------------
        gav = prop.annual_rent
        municipal_taxes = prop.municipal_taxes
        nav = max(0.0, gav - municipal_taxes)

        standard_deduction = nav * STANDARD_DEDUCTION_RATE

        # Total interest — NO cap for let-out u/s 24(b)
        total_interest_claimed = prop.home_loan_interest + pre_construction_yearly
        interest_deduction = total_interest_claimed

        net_income = nav - standard_deduction - interest_deduction

        return {
            "property_index": index,
            "property_type": "let_out",
            "gross_annual_value": gav,
            "municipal_taxes": municipal_taxes,
            "net_annual_value": round(nav, 2),
            "standard_deduction_24a": round(standard_deduction, 2),
            "home_loan_interest_claimed": prop.home_loan_interest,
            "pre_construction_interest_total": prop.pre_construction_interest,
            "pre_construction_interest_yearly": round(pre_construction_yearly, 2),
            "total_interest_claimed": round(total_interest_claimed, 2),
            "interest_deduction_24b": round(interest_deduction, 2),
            "net_income": round(net_income, 2),
            "amount": round(net_income, 2),
            "section_reference": "Sections 23(1), 24(a), 24(b)",
            "explanation": (
                f"Property #{index + 1} (let-out): "
                f"GAV = ₹{gav:,.0f}, Municipal taxes = ₹{municipal_taxes:,.0f}, "
                f"NAV = ₹{nav:,.0f}. "
                f"Standard deduction u/s 24(a) (30 %) = "
                f"₹{standard_deduction:,.0f}. "
                f"Home-loan interest: ₹{prop.home_loan_interest:,.0f}, "
                f"pre-construction interest (1/5th of "
                f"₹{prop.pre_construction_interest:,.0f}): "
                f"₹{pre_construction_yearly:,.0f}. "
                f"Interest u/s 24(b) = ₹{interest_deduction:,.0f} "
                f"(no cap for let-out). "
                f"Net HP income = ₹{net_income:,.0f}."
            ),
        }


# ---------------------------------------------------------------------------
# Main Entry Point — Multiple Properties
# ---------------------------------------------------------------------------

def calculate_house_property_income(
    properties: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate total income from house property for all properties held.

    Handles multiple properties, validates via the ``HousePropertyIncome``
    Pydantic model, enforces the two-SOP limit, aggregates income / loss,
    and applies the set-off cap under Section 71(3A).

    Rules applied:
        1. At most TWO properties may be treated as self-occupied
           (Section 23(2), effective FY 2019-20). Excess self-occupied
           properties are deemed let-out.
        2. Pre-construction interest is amortised over 5 equal annual
           instalments starting from the year of completion.
        3. Loss from house property may be set off against other heads
           only up to ₹2,00,000 per year (Section 71(3A)).
        4. Remaining (unabsorbed) loss is carried forward for 8 AYs
           under Section 71B.

    Args:
        properties: List of property dicts.  Each dict must have:
            - self_occupied            (bool)
            - annual_rent              (float) — GAV for let-out
            - municipal_taxes          (float)
            - home_loan_interest       (float)
            - pre_construction_interest (float)

    Returns:
        dict with keys:
            - total_hp_income         : aggregate income / loss across all
            - property_wise_breakdown : list of per-property detail dicts
            - set_off_allowed         : loss allowed for current-year set-off
            - carry_forward           : unabsorbed loss for carry-forward
            - carry_forward_years     : number of AYs (8 if carry-forward > 0)
            - amount                  : net HP income feeding into GTI
            - section_reference       : statutory citations
            - explanation             : narrative summary
    """
    if not properties:
        return {
            "amount": 0.0,
            "total_hp_income": 0.0,
            "property_wise_breakdown": [],
            "set_off_allowed": 0.0,
            "carry_forward": 0.0,
            "carry_forward_years": 0,
            "section_reference": "Sections 22–27",
            "explanation": "No house properties declared.",
        }

    # Validate, parse, and enforce the two-SOP cap
    parsed = _validate_and_parse(properties)

    # Compute each property
    breakdown: list[dict[str, Any]] = []
    for i, prop in enumerate(parsed):
        detail = _compute_single_property(prop, i)
        breakdown.append(detail)

    total_hp_income = round(sum(d["net_income"] for d in breakdown), 2)

    # Section 71(3A) — loss set-off cap
    if total_hp_income < 0:
        loss = abs(total_hp_income)
        set_off_allowed = min(loss, LOSS_SETOFF_CAP)
        carry_forward = round(max(0.0, loss - LOSS_SETOFF_CAP), 2)
    else:
        set_off_allowed = 0.0
        carry_forward = 0.0

    # "amount" is what feeds into GTI.
    # If there is a loss, only the set-off-allowed portion is claimed now.
    amount = total_hp_income if total_hp_income >= 0 else -set_off_allowed

    section_refs = ["Sections 22–27"]
    if total_hp_income < 0:
        section_refs.append("Section 71(3A)")
    if carry_forward > 0:
        section_refs.append("Section 71B")

    return {
        "amount": round(amount, 2),
        "total_hp_income": total_hp_income,
        "property_wise_breakdown": breakdown,
        "set_off_allowed": round(set_off_allowed, 2),
        "carry_forward": carry_forward,
        "carry_forward_years": CARRY_FORWARD_YEARS if carry_forward > 0 else 0,
        "section_reference": ", ".join(section_refs),
        "explanation": (
            f"Total HP income across {len(properties)} propert(ies): "
            f"₹{total_hp_income:,.0f}. "
            + (
                f"Loss set-off against other heads (u/s 71(3A)): "
                f"₹{set_off_allowed:,.0f}. "
                f"Carry forward to next {CARRY_FORWARD_YEARS} AYs (u/s 71B): "
                f"₹{carry_forward:,.0f}."
                if total_hp_income < 0
                else "No loss — full income added to GTI."
            )
        ),
    }


# ---------------------------------------------------------------------------
# Quick-Test Harness
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 76)
    print("HOUSE PROPERTY INCOME CALCULATOR — Test Cases (FY 2024-25)")
    print("=" * 76)

    # -----------------------------------------------------------------------
    # Test 1: Self-occupied, interest within cap, no pre-construction
    # -----------------------------------------------------------------------
    result = calculate_house_property_income([
        {
            "self_occupied": True,
            "annual_rent": 0.0,
            "municipal_taxes": 0.0,
            "home_loan_interest": 180_000,
            "pre_construction_interest": 0.0,
        },
    ])
    assert result["total_hp_income"] == -180_000.0
    assert result["set_off_allowed"] == 180_000.0
    assert result["carry_forward"] == 0.0
    print(f"[PASS] Test 1 — SOP (interest < cap):  {result['explanation']}")

    # -----------------------------------------------------------------------
    # Test 2: Self-occupied, interest exceeds cap
    # -----------------------------------------------------------------------
    result = calculate_house_property_income([
        {
            "self_occupied": True,
            "annual_rent": 0.0,
            "municipal_taxes": 0.0,
            "home_loan_interest": 350_000,
            "pre_construction_interest": 0.0,
        },
    ])
    assert result["total_hp_income"] == -200_000.0  # capped at 2L
    assert result["set_off_allowed"] == 200_000.0
    assert result["carry_forward"] == 0.0
    print(f"[PASS] Test 2 — SOP (interest > cap):  {result['explanation']}")

    # -----------------------------------------------------------------------
    # Test 3: Let-out property with profit
    # -----------------------------------------------------------------------
    result = calculate_house_property_income([
        {
            "self_occupied": False,
            "annual_rent": 600_000,
            "municipal_taxes": 20_000,
            "home_loan_interest": 100_000,
            "pre_construction_interest": 0.0,
        },
    ])
    # NAV = 580K, Std ded = 174K, Interest = 100K → Net = 306K
    assert result["total_hp_income"] == 306_000.0
    assert result["amount"] == 306_000.0
    print(f"[PASS] Test 3 — Let-out (profit):      {result['explanation']}")

    # -----------------------------------------------------------------------
    # Test 4: Let-out property with loss exceeding ₹2L
    # -----------------------------------------------------------------------
    result = calculate_house_property_income([
        {
            "self_occupied": False,
            "annual_rent": 240_000,
            "municipal_taxes": 10_000,
            "home_loan_interest": 500_000,
            "pre_construction_interest": 0.0,
        },
    ])
    # NAV = 230K, Std ded = 69K, Interest = 500K → Net = -339K
    assert result["total_hp_income"] == -339_000.0
    assert result["set_off_allowed"] == 200_000.0
    assert result["carry_forward"] == 139_000.0
    print(f"[PASS] Test 4 — Let-out (loss > 2L):   {result['explanation']}")

    # -----------------------------------------------------------------------
    # Test 5: Mixed — SOP + let-out
    # -----------------------------------------------------------------------
    result = calculate_house_property_income([
        {
            "self_occupied": True,
            "annual_rent": 0.0,
            "municipal_taxes": 0.0,
            "home_loan_interest": 200_000,
            "pre_construction_interest": 0.0,
        },
        {
            "self_occupied": False,
            "annual_rent": 360_000,
            "municipal_taxes": 10_000,
            "home_loan_interest": 50_000,
            "pre_construction_interest": 0.0,
        },
    ])
    # SOP: 0 - 200K = -200K
    # Let-out: NAV = 350K, Std = 105K, Int = 50K → 195K
    # Total = -200K + 195K = -5K
    assert result["total_hp_income"] == -5_000.0
    assert result["set_off_allowed"] == 5_000.0
    assert result["carry_forward"] == 0.0
    print(f"[PASS] Test 5 — Mixed SOP + LO:        {result['explanation']}")

    # -----------------------------------------------------------------------
    # Test 6: Pre-construction interest amortisation
    # -----------------------------------------------------------------------
    result = calculate_house_property_income([
        {
            "self_occupied": True,
            "annual_rent": 0.0,
            "municipal_taxes": 0.0,
            "home_loan_interest": 100_000,
            "pre_construction_interest": 250_000,  # 1/5th = 50K
        },
    ])
    # Total interest claimed = 100K + 50K = 150K (under 2L cap)
    assert result["total_hp_income"] == -150_000.0
    det = result["property_wise_breakdown"][0]
    assert det["pre_construction_interest_yearly"] == 50_000.0
    assert det["total_interest_claimed"] == 150_000.0
    print(f"[PASS] Test 6 — Pre-construction (SOP): {result['explanation']}")

    # -----------------------------------------------------------------------
    # Test 7: Pre-construction interest + regular interest exceeds SOP cap
    # -----------------------------------------------------------------------
    result = calculate_house_property_income([
        {
            "self_occupied": True,
            "annual_rent": 0.0,
            "municipal_taxes": 0.0,
            "home_loan_interest": 180_000,
            "pre_construction_interest": 500_000,  # 1/5th = 100K
        },
    ])
    # Total interest = 180K + 100K = 280K → capped at 200K
    assert result["total_hp_income"] == -200_000.0
    det = result["property_wise_breakdown"][0]
    assert det["total_interest_claimed"] == 280_000.0
    assert det["interest_deduction_24b"] == 200_000.0
    print(f"[PASS] Test 7 — Pre-constr exceeds cap: {result['explanation']}")

    # -----------------------------------------------------------------------
    # Test 8: Pre-construction interest on let-out (no cap)
    # -----------------------------------------------------------------------
    result = calculate_house_property_income([
        {
            "self_occupied": False,
            "annual_rent": 300_000,
            "municipal_taxes": 10_000,
            "home_loan_interest": 200_000,
            "pre_construction_interest": 500_000,  # 1/5th = 100K
        },
    ])
    # NAV = 290K, Std = 87K, Interest = 200K + 100K = 300K → Net = -97K
    assert result["total_hp_income"] == -97_000.0
    print(f"[PASS] Test 8 — Pre-constr let-out:    {result['explanation']}")

    # -----------------------------------------------------------------------
    # Test 9: Three self-occupied → third becomes deemed let-out
    # -----------------------------------------------------------------------
    result = calculate_house_property_income([
        {
            "self_occupied": True,
            "annual_rent": 0.0,
            "municipal_taxes": 0.0,
            "home_loan_interest": 50_000,
            "pre_construction_interest": 0.0,
        },
        {
            "self_occupied": True,
            "annual_rent": 0.0,
            "municipal_taxes": 0.0,
            "home_loan_interest": 50_000,
            "pre_construction_interest": 0.0,
        },
        {
            # This third SOP will be deemed let-out
            "self_occupied": True,
            "annual_rent": 0.0,
            "municipal_taxes": 0.0,
            "home_loan_interest": 50_000,
            "pre_construction_interest": 0.0,
        },
    ])
    brkdn = result["property_wise_breakdown"]
    # First two remain self-occupied
    assert brkdn[0]["property_type"] == "self_occupied"
    assert brkdn[1]["property_type"] == "self_occupied"
    # Third is flipped to let-out
    assert brkdn[2]["property_type"] == "let_out"
    print(f"[PASS] Test 9 — 3 SOPs (cap at 2):    third deemed let-out")

    # -----------------------------------------------------------------------
    # Test 10: No properties
    # -----------------------------------------------------------------------
    result = calculate_house_property_income([])
    assert result["amount"] == 0.0
    assert result["property_wise_breakdown"] == []
    print(f"[PASS] Test 10 — No properties:        {result['explanation']}")

    print("\n✅ All house property tests passed.")
