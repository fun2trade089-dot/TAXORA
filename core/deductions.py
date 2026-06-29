"""
Deduction Calculator — Chapter VI-A of the Income Tax Act, 1961.

Implements deterministic deduction computation for FY 2024-25 (AY 2025-26).
Every function returns a dict with at minimum:
    - amount         : the allowed deduction (float)
    - section_reference : statutory citation (str)
    - explanation    : human-readable narrative of the calculation (str)

References:
    - Sections 80C–80U of the Income Tax Act, 1961
    - Finance (No. 2) Act, 2024 (Budget 2024 amendments)
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Constants — FY 2024-25
# ---------------------------------------------------------------------------

CAP_80C_GROUP: float = 150_000.0
"""Section 80C + 80CCC + 80CCD(1) aggregate cap: ₹1,50,000."""

CAP_80CCD1B: float = 50_000.0
"""Section 80CCD(1B) additional NPS cap: ₹50,000."""

CAP_80CCD2_CENTRAL_PCT: float = 0.14
"""Section 80CCD(2) employer NPS cap for central govt employees: 14%."""

CAP_80CCD2_OTHERS_PCT: float = 0.10
"""Section 80CCD(2) employer NPS cap for other employees: 10%."""

CAP_80D_NORMAL: float = 25_000.0
"""Section 80D medical insurance cap (non-senior): ₹25,000."""

CAP_80D_SENIOR: float = 50_000.0
"""Section 80D medical insurance cap (senior citizen): ₹50,000."""

CAP_80D_PREVENTIVE: float = 5_000.0
"""Section 80D preventive health check-up: ₹5,000 (within overall limit)."""

CAP_80GG_MONTHLY: float = 5_000.0
"""Section 80GG per-month cap: ₹5,000."""

CAP_80TTA: float = 10_000.0
"""Section 80TTA savings interest cap: ₹10,000."""

CAP_80TTB: float = 50_000.0
"""Section 80TTB senior citizen interest cap: ₹50,000."""

DEDUCTION_80U_NORMAL: float = 75_000.0
"""Section 80U disability deduction (40%–79% disability): ₹75,000."""

DEDUCTION_80U_SEVERE: float = 125_000.0
"""Section 80U severe disability deduction (≥80%): ₹1,25,000."""


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _cap(value: float, limit: float) -> float:
    """Return the lower of *value* and *limit*, floored at zero."""
    return max(0.0, min(value, limit))


# ---------------------------------------------------------------------------
# Section 80C + 80CCC + 80CCD(1) — Combined Group
# ---------------------------------------------------------------------------

def calculate_80c_group(
    section_80c: float,
    section_80ccc: float,
    section_80ccd1: float,
) -> dict[str, Any]:
    """Calculate the combined deduction under Sections 80C, 80CCC, and 80CCD(1).

    Per Section 80CCE, the aggregate of deductions under 80C, 80CCC and
    80CCD(1) shall not exceed ₹1,50,000 in any assessment year.

    Section 80C   — Life insurance, PPF, ELSS, NSC, tuition fees, etc.
    Section 80CCC — Pension fund contributions (annuity plans of LIC / insurers).
    Section 80CCD(1) — Employee's own contribution to NPS (capped at 10% of
                       salary for salaried, 20% of GTI for self-employed, but
                       the aggregate is still limited by 80CCE).

    Args:
        section_80c:   Eligible investments / payments under 80C.
        section_80ccc: Contributions to pension funds under 80CCC.
        section_80ccd1: Employee's own NPS contribution under 80CCD(1).

    Returns:
        dict with keys: claimed, capped, gap_remaining, breakdown,
        amount, section_reference, explanation.
    """
    claimed = section_80c + section_80ccc + section_80ccd1
    capped = _cap(claimed, CAP_80C_GROUP)
    gap = max(0.0, CAP_80C_GROUP - claimed)

    return {
        "amount": capped,
        "claimed": claimed,
        "capped": capped,
        "gap_remaining": gap,
        "breakdown": {
            "section_80c": section_80c,
            "section_80ccc": section_80ccc,
            "section_80ccd1": section_80ccd1,
        },
        "section_reference": "Sections 80C, 80CCC, 80CCD(1) r/w 80CCE",
        "explanation": (
            f"Gross investments: ₹{claimed:,.0f} "
            f"(80C=₹{section_80c:,.0f}, 80CCC=₹{section_80ccc:,.0f}, "
            f"80CCD(1)=₹{section_80ccd1:,.0f}). "
            f"Aggregate cap u/s 80CCE: ₹{CAP_80C_GROUP:,.0f}. "
            f"Allowed deduction: ₹{capped:,.0f}. "
            f"Gap remaining under limit: ₹{gap:,.0f}."
        ),
    }


# ---------------------------------------------------------------------------
# Section 80CCD(1B) — Additional NPS
# ---------------------------------------------------------------------------

def calculate_80ccd1b(amount: float) -> dict[str, Any]:
    """Calculate additional NPS deduction under Section 80CCD(1B).

    This is over and above the ₹1,50,000 limit of Section 80CCE.
    Maximum additional deduction: ₹50,000.

    Note: From FY 2024-25, this deduction is NOT available under the
    new tax regime (Section 115BAC).

    Args:
        amount: Additional NPS contribution claimed under 80CCD(1B).

    Returns:
        dict with amount, section_reference, explanation.
    """
    capped = _cap(amount, CAP_80CCD1B)
    return {
        "amount": capped,
        "claimed": amount,
        "section_reference": "Section 80CCD(1B)",
        "explanation": (
            f"Additional NPS contribution: ₹{amount:,.0f}. "
            f"Cap: ₹{CAP_80CCD1B:,.0f}. "
            f"Allowed deduction: ₹{capped:,.0f}."
        ),
    }


# ---------------------------------------------------------------------------
# Section 80CCD(2) — Employer NPS
# ---------------------------------------------------------------------------

def calculate_80ccd2(
    employer_nps: float,
    basic_plus_da: float,
    is_central_govt: bool = False,
) -> dict[str, Any]:
    """Calculate employer NPS deduction under Section 80CCD(2).

    The employer's contribution to NPS is deductible subject to:
        - 14% of (Basic + DA) for Central Government employees
        - 10% of (Basic + DA) for all other employees

    IMPORTANT: This deduction is available under BOTH old and new regimes.
    It is outside the ₹1,50,000 cap of Section 80CCE.

    Args:
        employer_nps:    Employer's NPS contribution for the year.
        basic_plus_da:   Employee's Basic salary + Dearness Allowance.
        is_central_govt: True if the employee is a Central Government employee.

    Returns:
        dict with amount, section_reference, explanation.
    """
    pct = CAP_80CCD2_CENTRAL_PCT if is_central_govt else CAP_80CCD2_OTHERS_PCT
    ceiling = basic_plus_da * pct
    capped = _cap(employer_nps, ceiling)

    label = "Central Govt (14%)" if is_central_govt else "Others (10%)"
    return {
        "amount": capped,
        "claimed": employer_nps,
        "ceiling": ceiling,
        "section_reference": "Section 80CCD(2)",
        "explanation": (
            f"Employer NPS: ₹{employer_nps:,.0f}. "
            f"Basic+DA: ₹{basic_plus_da:,.0f}. "
            f"Category: {label} → ceiling = ₹{ceiling:,.0f}. "
            f"Allowed deduction: ₹{capped:,.0f}. "
            f"Available under both Old and New tax regimes."
        ),
    }


# ---------------------------------------------------------------------------
# Section 80D — Medical Insurance
# ---------------------------------------------------------------------------

def calculate_80d(
    premium_self: float,
    premium_parents: float,
    is_senior_self: bool = False,
    is_senior_parents: bool = False,
    preventive_health_checkup: float = 0.0,
) -> dict[str, Any]:
    """Calculate medical insurance deduction under Section 80D.

    Limits (FY 2024-25):
        Self/Family:
            - Non-senior: ₹25,000 (includes preventive health check-up up to ₹5,000)
            - Senior citizen (≥60): ₹50,000
        Parents:
            - Non-senior: ₹25,000
            - Senior citizen: ₹50,000

    Preventive health check-up expenditure (up to ₹5,000) is allowed
    *within* the overall self/family limit, NOT in addition to it.

    Args:
        premium_self:    Health insurance premium for self, spouse, children.
        premium_parents: Health insurance premium for parents.
        is_senior_self:  True if the assessee or spouse is ≥ 60 years.
        is_senior_parents: True if either parent is ≥ 60 years.
        preventive_health_checkup: Preventive health check-up expenditure.

    Returns:
        dict with amount, section_reference, explanation, breakdown.
    """
    cap_self = CAP_80D_SENIOR if is_senior_self else CAP_80D_NORMAL
    cap_parents = CAP_80D_SENIOR if is_senior_parents else CAP_80D_NORMAL

    # Preventive health check-up is within the self/family limit
    phc = _cap(preventive_health_checkup, CAP_80D_PREVENTIVE)
    self_total = premium_self + phc
    allowed_self = _cap(self_total, cap_self)

    allowed_parents = _cap(premium_parents, cap_parents)

    total = allowed_self + allowed_parents

    return {
        "amount": total,
        "breakdown": {
            "self_family": {
                "premium": premium_self,
                "preventive_health_checkup": phc,
                "total_claimed": self_total,
                "cap": cap_self,
                "allowed": allowed_self,
            },
            "parents": {
                "premium": premium_parents,
                "cap": cap_parents,
                "allowed": allowed_parents,
            },
        },
        "section_reference": "Section 80D",
        "explanation": (
            f"Self/family premium ₹{premium_self:,.0f} + "
            f"preventive check-up ₹{phc:,.0f} = ₹{self_total:,.0f}, "
            f"cap ₹{cap_self:,.0f} → allowed ₹{allowed_self:,.0f}. "
            f"Parents premium ₹{premium_parents:,.0f}, "
            f"cap ₹{cap_parents:,.0f} → allowed ₹{allowed_parents:,.0f}. "
            f"Total 80D deduction: ₹{total:,.0f}."
        ),
    }


# ---------------------------------------------------------------------------
# Section 80E — Education Loan Interest
# ---------------------------------------------------------------------------

def calculate_80e(education_loan_interest: float) -> dict[str, Any]:
    """Calculate education loan interest deduction under Section 80E.

    The ENTIRE interest paid during the year is deductible — there is NO
    upper cap. The deduction is available for 8 assessment years starting
    from the year in which the assessee begins repaying the loan, or until
    the interest is fully repaid, whichever is earlier.

    This deduction is for interest only; principal repayment falls under 80C.

    Args:
        education_loan_interest: Interest paid on education loan during FY.

    Returns:
        dict with amount, section_reference, explanation.
    """
    allowed = max(0.0, education_loan_interest)
    return {
        "amount": allowed,
        "claimed": education_loan_interest,
        "section_reference": "Section 80E",
        "explanation": (
            f"Education loan interest paid: ₹{education_loan_interest:,.0f}. "
            f"No upper cap — full amount deductible. "
            f"Available for 8 years from the year repayment starts."
        ),
    }


# ---------------------------------------------------------------------------
# Section 80G — Donations
# ---------------------------------------------------------------------------

def calculate_80g(
    donations_100pct: float,
    donations_50pct: float,
    gti: float,
) -> dict[str, Any]:
    """Calculate donation deduction under Section 80G.

    Two categories of donations:
        1. 100% deduction WITHOUT qualifying limit — e.g., PM National
           Relief Fund, National Defence Fund (no cap).
        2. 50% deduction subject to qualifying limit — the deduction is
           50% of the donated amount, further restricted to 10% of
           Adjusted Gross Total Income (GTI after all other Chapter VI-A
           deductions except 80G).

    Args:
        donations_100pct: Donations eligible for 100% deduction without cap.
        donations_50pct:  Donations eligible for 50% deduction (subject to
                          10% of adjusted GTI qualifying limit).
        gti:              Gross Total Income (adjusted) for qualifying limit.

    Returns:
        dict with amount, section_reference, explanation, breakdown.
    """
    # 100% category — no cap
    deduction_100 = max(0.0, donations_100pct)

    # 50% category — 50% of donated amount, subject to 10% of adj GTI
    qualifying_limit = max(0.0, gti * 0.10)
    eligible_50 = max(0.0, donations_50pct)
    # The qualifying limit caps the donation amount, not the deduction
    capped_donation_50 = min(eligible_50, qualifying_limit)
    deduction_50 = capped_donation_50 * 0.50

    total = deduction_100 + deduction_50

    return {
        "amount": total,
        "breakdown": {
            "donations_100pct": {
                "donated": donations_100pct,
                "deduction": deduction_100,
            },
            "donations_50pct": {
                "donated": donations_50pct,
                "qualifying_limit_10pct_gti": qualifying_limit,
                "capped_donation": capped_donation_50,
                "deduction": deduction_50,
            },
        },
        "section_reference": "Section 80G",
        "explanation": (
            f"100% donations: ₹{donations_100pct:,.0f} → "
            f"deduction ₹{deduction_100:,.0f}. "
            f"50% donations: ₹{donations_50pct:,.0f}, "
            f"qualifying limit (10% of GTI ₹{gti:,.0f}) = ₹{qualifying_limit:,.0f}, "
            f"capped donation ₹{capped_donation_50:,.0f} → "
            f"deduction ₹{deduction_50:,.0f}. "
            f"Total 80G deduction: ₹{total:,.0f}."
        ),
    }


# ---------------------------------------------------------------------------
# Section 80GG — Rent (when no HRA received)
# ---------------------------------------------------------------------------

def calculate_80gg(
    rent_paid: float,
    total_income: float,
) -> dict[str, Any]:
    """Calculate rent deduction under Section 80GG.

    Available ONLY when the assessee does NOT receive HRA from an employer.
    Also requires that the assessee, spouse, or minor child does not own
    residential accommodation at the place of employment.

    Deduction = MINIMUM of:
        (a) ₹5,000 per month (₹60,000 per annum)
        (b) 25% of Total Income (before this deduction)
        (c) Rent paid − 10% of Total Income

    Args:
        rent_paid:    Total rent paid during the financial year.
        total_income: Total income before 80GG deduction.

    Returns:
        dict with amount, section_reference, explanation.
    """
    annual_cap = CAP_80GG_MONTHLY * 12  # ₹60,000
    option_a = annual_cap
    option_b = total_income * 0.25
    option_c = rent_paid - (total_income * 0.10)

    allowed = max(0.0, min(option_a, option_b, option_c))

    return {
        "amount": allowed,
        "claimed": rent_paid,
        "formula": {
            "a_monthly_cap_annual": option_a,
            "b_25pct_total_income": option_b,
            "c_rent_minus_10pct_ti": option_c,
        },
        "section_reference": "Section 80GG",
        "explanation": (
            f"Rent paid: ₹{rent_paid:,.0f}. Total income: ₹{total_income:,.0f}. "
            f"(a) ₹5,000/month = ₹{option_a:,.0f}; "
            f"(b) 25% of TI = ₹{option_b:,.0f}; "
            f"(c) Rent − 10% TI = ₹{option_c:,.0f}. "
            f"Minimum of (a),(b),(c) = ₹{allowed:,.0f}."
        ),
    }


# ---------------------------------------------------------------------------
# Section 80TTA — Savings Interest (Non-Senior)
# ---------------------------------------------------------------------------

def calculate_80tta(savings_interest: float) -> dict[str, Any]:
    """Calculate savings account interest deduction under Section 80TTA.

    Available to individuals and HUFs who are NOT senior citizens.
    Covers interest from savings accounts in banks, co-operative societies,
    and post offices. Fixed deposit / recurring deposit interest is excluded.

    Cap: ₹10,000.

    NOTE: Mutually exclusive with Section 80TTB — a senior citizen (≥60)
    must use 80TTB instead.

    Args:
        savings_interest: Interest earned on savings accounts during FY.

    Returns:
        dict with amount, section_reference, explanation.
    """
    capped = _cap(savings_interest, CAP_80TTA)
    return {
        "amount": capped,
        "claimed": savings_interest,
        "section_reference": "Section 80TTA",
        "explanation": (
            f"Savings interest: ₹{savings_interest:,.0f}. "
            f"Cap: ₹{CAP_80TTA:,.0f}. "
            f"Allowed: ₹{capped:,.0f}. "
            f"(Only for non-senior citizens; mutually exclusive with 80TTB.)"
        ),
    }


# ---------------------------------------------------------------------------
# Section 80TTB — Interest Income (Senior Citizens)
# ---------------------------------------------------------------------------

def calculate_80ttb(savings_interest: float) -> dict[str, Any]:
    """Calculate interest income deduction under Section 80TTB.

    Available ONLY to senior citizens (age ≥ 60 years).
    Covers interest from savings accounts, fixed deposits, and recurring
    deposits in banks, co-operative societies, and post offices.

    Cap: ₹50,000.

    NOTE: Mutually exclusive with Section 80TTA.

    Args:
        savings_interest: Total interest from deposits during FY.

    Returns:
        dict with amount, section_reference, explanation.
    """
    capped = _cap(savings_interest, CAP_80TTB)
    return {
        "amount": capped,
        "claimed": savings_interest,
        "section_reference": "Section 80TTB",
        "explanation": (
            f"Deposit interest (senior citizen): ₹{savings_interest:,.0f}. "
            f"Cap: ₹{CAP_80TTB:,.0f}. "
            f"Allowed: ₹{capped:,.0f}. "
            f"(Only for senior citizens ≥ 60; mutually exclusive with 80TTA.)"
        ),
    }


# ---------------------------------------------------------------------------
# Section 80U — Disability
# ---------------------------------------------------------------------------

def calculate_80u(
    disability: bool,
    severe: bool = False,
) -> dict[str, Any]:
    """Calculate disability deduction under Section 80U.

    A flat deduction for a resident individual who is certified as a person
    with disability by the medical authority.

        - Disability (40%–79%): ₹75,000
        - Severe disability (≥ 80%): ₹1,25,000

    This is a flat deduction, not dependent on any expenditure.

    Args:
        disability: True if the assessee has a certified disability.
        severe:     True if the disability is 80% or more (severe).

    Returns:
        dict with amount, section_reference, explanation.
    """
    if not disability:
        return {
            "amount": 0.0,
            "section_reference": "Section 80U",
            "explanation": "No disability certified — deduction not applicable.",
        }

    amount = DEDUCTION_80U_SEVERE if severe else DEDUCTION_80U_NORMAL
    label = "severe (≥80%)" if severe else "normal (40%–79%)"

    return {
        "amount": amount,
        "disability_type": label,
        "section_reference": "Section 80U",
        "explanation": (
            f"Certified disability: {label}. "
            f"Flat deduction: ₹{amount:,.0f}."
        ),
    }


# ---------------------------------------------------------------------------
# Aggregator — Total Deductions
# ---------------------------------------------------------------------------

def calculate_total_deductions(profile: dict[str, Any]) -> dict[str, Any]:
    """Compute all applicable Chapter VI-A deductions for a taxpayer.

    This function acts as the orchestrator: it reads the taxpayer profile
    dict, calls individual section calculators, enforces mutual exclusions
    (80GG vs HRA, 80TTA vs 80TTB), and returns an itemized breakdown
    with the overall total.

    Expected keys in *profile* (all optional, default to 0 / False):
        Financial:
            section_80c, section_80ccc, section_80ccd1, section_80ccd1b,
            employer_nps, basic_plus_da, is_central_govt,
            premium_self, premium_parents, preventive_health_checkup,
            education_loan_interest,
            donations_100pct, donations_50pct, gti,
            rent_paid, total_income,
            savings_interest
        Personal:
            is_senior (bool) — True if ≥ 60 years
            is_senior_parents (bool)
            receives_hra (bool) — True if HRA is part of salary
            disability (bool), severe_disability (bool)

    Args:
        profile: A dict (or dict-like) with taxpayer financial data.

    Returns:
        dict with 'deductions' (itemized), 'total_deduction', and metadata.
    """
    g = profile.get  # shorthand

    deductions: dict[str, dict[str, Any]] = {}

    # --- 80C group ---
    result_80c = calculate_80c_group(
        section_80c=g("section_80c", 0.0),
        section_80ccc=g("section_80ccc", 0.0),
        section_80ccd1=g("section_80ccd1", 0.0),
    )
    deductions["80C_group"] = result_80c

    # --- 80CCD(1B) ---
    result_80ccd1b = calculate_80ccd1b(g("section_80ccd1b", 0.0))
    deductions["80CCD_1B"] = result_80ccd1b

    # --- 80CCD(2) ---
    if g("employer_nps", 0.0) > 0:
        result_80ccd2 = calculate_80ccd2(
            employer_nps=g("employer_nps", 0.0),
            basic_plus_da=g("basic_plus_da", 0.0),
            is_central_govt=g("is_central_govt", False),
        )
        deductions["80CCD_2"] = result_80ccd2

    # --- 80D ---
    is_senior = g("is_senior", False)
    result_80d = calculate_80d(
        premium_self=g("premium_self", 0.0),
        premium_parents=g("premium_parents", 0.0),
        is_senior_self=is_senior,
        is_senior_parents=g("is_senior_parents", False),
        preventive_health_checkup=g("preventive_health_checkup", 0.0),
    )
    deductions["80D"] = result_80d

    # --- 80E ---
    if g("education_loan_interest", 0.0) > 0:
        result_80e = calculate_80e(g("education_loan_interest", 0.0))
        deductions["80E"] = result_80e

    # --- 80G ---
    if g("donations_100pct", 0.0) > 0 or g("donations_50pct", 0.0) > 0:
        result_80g = calculate_80g(
            donations_100pct=g("donations_100pct", 0.0),
            donations_50pct=g("donations_50pct", 0.0),
            gti=g("gti", 0.0),
        )
        deductions["80G"] = result_80g

    # --- 80GG vs HRA (mutual exclusion) ---
    receives_hra = g("receives_hra", False)
    if not receives_hra and g("rent_paid", 0.0) > 0:
        result_80gg = calculate_80gg(
            rent_paid=g("rent_paid", 0.0),
            total_income=g("total_income", 0.0),
        )
        deductions["80GG"] = result_80gg

    # --- 80TTA vs 80TTB (mutual exclusion) ---
    if is_senior:
        result_interest = calculate_80ttb(g("savings_interest", 0.0))
        deductions["80TTB"] = result_interest
    else:
        result_interest = calculate_80tta(g("savings_interest", 0.0))
        deductions["80TTA"] = result_interest

    # --- 80U ---
    if g("disability", False):
        result_80u = calculate_80u(
            disability=True,
            severe=g("severe_disability", False),
        )
        deductions["80U"] = result_80u

    # --- Aggregate ---
    total = sum(d["amount"] for d in deductions.values())

    return {
        "deductions": deductions,
        "total_deduction": total,
        "section_reference": "Chapter VI-A (Sections 80C–80U)",
        "explanation": (
            f"Total Chapter VI-A deductions: ₹{total:,.0f}. "
            f"Sections applied: {', '.join(deductions.keys())}."
        ),
    }


# ---------------------------------------------------------------------------
# Quick-Test Harness
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 72)
    print("CHAPTER VI-A DEDUCTION CALCULATOR — Test Cases (FY 2024-25)")
    print("=" * 72)

    # --- Test 1: 80C group — within cap ---
    r = calculate_80c_group(80_000, 20_000, 30_000)
    assert r["amount"] == 130_000.0, f"FAIL: expected 130000, got {r['amount']}"
    assert r["gap_remaining"] == 20_000.0
    print(f"[PASS] 80C group (under cap): {r['explanation']}")

    # --- Test 2: 80C group — exceeds cap ---
    r = calculate_80c_group(100_000, 30_000, 50_000)
    assert r["amount"] == 150_000.0
    assert r["gap_remaining"] == 0.0
    print(f"[PASS] 80C group (over cap):  {r['explanation']}")

    # --- Test 3: 80CCD(1B) ---
    r = calculate_80ccd1b(70_000)
    assert r["amount"] == 50_000.0
    print(f"[PASS] 80CCD(1B): {r['explanation']}")

    # --- Test 4: 80CCD(2) central govt ---
    r = calculate_80ccd2(84_000, 600_000, is_central_govt=True)
    assert r["amount"] == 84_000.0  # 14% of 6L = 84K
    print(f"[PASS] 80CCD(2) central: {r['explanation']}")

    # --- Test 5: 80CCD(2) others ---
    r = calculate_80ccd2(84_000, 600_000, is_central_govt=False)
    assert r["amount"] == 60_000.0  # 10% of 6L = 60K
    print(f"[PASS] 80CCD(2) others:  {r['explanation']}")

    # --- Test 6: 80D non-senior ---
    r = calculate_80d(20_000, 30_000, is_senior_self=False, is_senior_parents=False)
    assert r["amount"] == 45_000.0  # 20K + 25K
    print(f"[PASS] 80D non-senior: {r['explanation']}")

    # --- Test 7: 80D senior + preventive ---
    r = calculate_80d(
        45_000, 55_000,
        is_senior_self=True, is_senior_parents=True,
        preventive_health_checkup=8_000,
    )
    # Self: 45000 + 5000(capped PHC) = 50000 capped at 50000
    # Parents: 55000 capped at 50000
    assert r["amount"] == 100_000.0
    print(f"[PASS] 80D senior:     {r['explanation']}")

    # --- Test 8: 80E ---
    r = calculate_80e(200_000)
    assert r["amount"] == 200_000.0
    print(f"[PASS] 80E: {r['explanation']}")

    # --- Test 9: 80G ---
    r = calculate_80g(50_000, 100_000, gti=800_000)
    # 100%: 50K. 50%: min(100K, 10% of 8L=80K) → 80K * 50% = 40K
    assert r["amount"] == 90_000.0
    print(f"[PASS] 80G: {r['explanation']}")

    # --- Test 10: 80GG ---
    r = calculate_80gg(180_000, 500_000)
    # (a) 60K, (b) 125K, (c) 180K - 50K = 130K → min = 60K
    assert r["amount"] == 60_000.0
    print(f"[PASS] 80GG: {r['explanation']}")

    # --- Test 11: 80TTA ---
    r = calculate_80tta(15_000)
    assert r["amount"] == 10_000.0
    print(f"[PASS] 80TTA: {r['explanation']}")

    # --- Test 12: 80TTB ---
    r = calculate_80ttb(60_000)
    assert r["amount"] == 50_000.0
    print(f"[PASS] 80TTB: {r['explanation']}")

    # --- Test 13: 80U severe ---
    r = calculate_80u(disability=True, severe=True)
    assert r["amount"] == 125_000.0
    print(f"[PASS] 80U severe: {r['explanation']}")

    # --- Test 14: 80U normal ---
    r = calculate_80u(disability=True, severe=False)
    assert r["amount"] == 75_000.0
    print(f"[PASS] 80U normal: {r['explanation']}")

    # --- Test 15: Total deductions (composite profile) ---
    profile = {
        "section_80c": 100_000,
        "section_80ccc": 0,
        "section_80ccd1": 50_000,
        "section_80ccd1b": 30_000,
        "employer_nps": 50_000,
        "basic_plus_da": 600_000,
        "is_central_govt": False,
        "premium_self": 20_000,
        "premium_parents": 25_000,
        "is_senior": False,
        "is_senior_parents": False,
        "education_loan_interest": 0,
        "donations_100pct": 0,
        "donations_50pct": 0,
        "gti": 800_000,
        "receives_hra": True,
        "rent_paid": 120_000,
        "total_income": 800_000,
        "savings_interest": 12_000,
        "disability": False,
    }
    r = calculate_total_deductions(profile)
    print(f"\n[PASS] Total deductions: ₹{r['total_deduction']:,.0f}")
    for section, detail in r["deductions"].items():
        print(f"       {section:12s} → ₹{detail['amount']:>10,.0f}")

    print("\n✅ All deduction tests passed.")
