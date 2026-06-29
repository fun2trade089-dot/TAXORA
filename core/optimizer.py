"""
Tax Optimization Engine — Income Tax Act, 1961 (FY 2024-25 / AY 2025-26).

This module is the **brain** of the tax engine.  It takes a complete
``TaxpayerProfile`` and determines the most tax-efficient strategy by:

    1. Computing Gross Total Income (GTI) across all five heads.
    2. Applying Chapter VI-A deductions under each regime's rules.
    3. Comparing Old vs New regime outcomes.
    4. Identifying underutilised deduction headroom.
    5. Running what-if scenarios for investment planning.
    6. Generating a comprehensive optimisation report.

All calculations are deterministic, pure-functional, and align with the
Income Tax Act, 1961 as amended by Finance (No. 2) Act, 2024.

References:
    - Sections 14–59 : Heads of income
    - Sections 80C–80U : Chapter VI-A deductions
    - Section 115BAC  : New Tax Regime
    - Section 87A     : Rebate for resident individuals
    - Section 10(13A) : HRA exemption
    - Section 16(ia)  : Standard deduction
    - Section 24(b)   : Interest on housing loan
"""

from __future__ import annotations

import copy
from typing import Any

from .models import (
    TaxpayerProfile,
    TaxRegime,
    TaxResult,
    RegimeComparison,
)
from .slabs import compute_total_tax
from .deductions import (
    calculate_total_deductions,
    calculate_80c_group,
    calculate_80ccd1b,
    calculate_80ccd2,
    calculate_80d,
    calculate_80e,
    calculate_80g,
    calculate_80gg,
    calculate_80tta,
    calculate_80ttb,
    CAP_80C_GROUP,
    CAP_80CCD1B,
    CAP_80D_NORMAL,
    CAP_80D_SENIOR,
    CAP_80TTA,
    CAP_80TTB,
)
from .exemptions import calculate_hra_exemption, calculate_standard_deduction
from .house_property import calculate_house_property_income
from .compliance import check_compliance, get_filing_checklist


# ---------------------------------------------------------------------------
# Section-wise deduction limits (for gap analysis)
# ---------------------------------------------------------------------------

_DEDUCTION_SECTIONS: list[dict[str, Any]] = [
    {
        "section": "80C/80CCC/80CCD(1)",
        "field": "section_80c",       # primary field to check
        "limit": 150_000.0,
        "section_reference": "Sections 80C, 80CCC, 80CCD(1) r/w 80CCE",
        "suggestion": (
            "Invest in PPF, ELSS, NSC, 5-yr FD, life insurance premium, "
            "tuition fees, or employee PF contribution to utilise the full "
            "₹1,50,000 limit."
        ),
        "regime": "OLD",
    },
    {
        "section": "80CCD(1B)",
        "field": "section_80ccd1b",
        "limit": 50_000.0,
        "section_reference": "Section 80CCD(1B)",
        "suggestion": (
            "Contribute up to ₹50,000 additionally to NPS (Tier I) for an "
            "extra deduction over and above the ₹1,50,000 80C cap."
        ),
        "regime": "OLD",
    },
    {
        "section": "80D (self & family)",
        "field": "section_80d_self",
        "limit": None,  # determined dynamically based on senior status
        "section_reference": "Section 80D",
        "suggestion": (
            "Purchase a comprehensive health insurance policy for self and "
            "family.  Senior citizens (≥60) get a higher cap of ₹50,000."
        ),
        "regime": "OLD",
    },
    {
        "section": "80D (parents)",
        "field": "section_80d_parents",
        "limit": None,  # dynamic
        "section_reference": "Section 80D",
        "suggestion": (
            "Insure your parents under a health policy.  If parents are "
            "senior citizens, the limit is ₹50,000 (else ₹25,000)."
        ),
        "regime": "OLD",
    },
    {
        "section": "80TTA",
        "field": "section_80tta",
        "limit": 10_000.0,
        "section_reference": "Section 80TTA",
        "suggestion": (
            "Savings account interest up to ₹10,000 is deductible.  "
            "Ensure you claim this if you have savings accounts."
        ),
        "regime": "OLD",
    },
]


# =====================================================================
# 1. Gross Total Income
# =====================================================================

def compute_gross_total_income(profile: TaxpayerProfile) -> dict[str, Any]:
    """Calculate income under each head and compute Gross Total Income.

    Head-wise computation (Section 14):
        1. **Salary** (Sections 15-17): Gross salary minus HRA exemption
           (Section 10(13A)), standard deduction (Section 16(ia)), and
           professional tax (Section 16(iii)).
        2. **House Property** (Sections 22-27): Net income/loss from all
           properties, with loss set-off capped at ₹2,00,000 (Section 71(3A)).
        3. **Profits & Gains of Business/Profession** (Sections 28-44):
           Gross receipts minus expenses, or presumptive income.
        4. **Capital Gains** (Sections 45-55): Separated into STCG and LTCG.
        5. **Other Sources** (Sections 56-59): Interest, dividends, gifts, etc.

    Args:
        profile: Complete ``TaxpayerProfile`` with all income details.

    Returns:
        dict with keys:
            ``head_wise_income`` — dict mapping each head to its amount.
            ``gross_total_income`` — aggregate GTI (float).
            ``salary_details`` — breakdown of salary computation.
            ``hp_details`` — house property computation result.
            ``capital_gains_details`` — STCG/LTCG breakdown.

    References:
        Section 14 (Heads of income), Sections 15-59.
    """
    sal = profile.salary

    # --- Gross salary ---
    gross_salary = (
        sal.basic
        + sal.da
        + sal.hra_received
        + sal.special_allowance
        + sal.lta
        + sal.perquisites
    )

    # --- HRA exemption (Section 10(13A)) ---
    hra_exemption = 0.0
    hra_details: dict[str, Any] = {}
    if profile.hra_details is not None and profile.hra_details.rent_paid > 0:
        hra_result = calculate_hra_exemption(
            basic=profile.hra_details.basic_salary,
            da=profile.hra_details.da,
            hra_received=profile.hra_details.hra_received,
            rent_paid=profile.hra_details.rent_paid,
            is_metro=profile.hra_details.is_metro,
        )
        hra_exemption = hra_result["amount"]
        hra_details = hra_result

    # --- Standard deduction (Section 16(ia)) ---
    # For GTI computation we use old-regime standard deduction (₹50,000)
    # as the baseline; regime-specific adjustments happen at taxable-income stage
    std_ded_result = calculate_standard_deduction("old")
    standard_deduction = min(std_ded_result["amount"], gross_salary)

    # --- Professional tax (Section 16(iii)) ---
    professional_tax = min(sal.professional_tax, 2_500.0)

    net_salary = max(
        0.0,
        gross_salary - hra_exemption - standard_deduction - professional_tax,
    )

    salary_details = {
        "gross_salary": gross_salary,
        "hra_exemption": hra_exemption,
        "standard_deduction": standard_deduction,
        "professional_tax": professional_tax,
        "net_salary": net_salary,
        "hra_details": hra_details,
    }

    # --- House Property (Sections 22-27) ---
    hp_properties = []
    for hp in profile.house_property:
        hp_properties.append({
            "property_type": "self_occupied" if hp.self_occupied else "let_out",
            "gross_annual_value": hp.annual_rent,
            "municipal_taxes": hp.municipal_taxes,
            "interest_on_loan": hp.home_loan_interest + hp.pre_construction_interest,
        })

    hp_result = calculate_house_property_income(hp_properties)
    hp_income = hp_result["amount"]

    # --- Business / Profession (Sections 28-44) ---
    biz = profile.business
    if biz.presumptive_income_44AD > 0:
        pgbp_income = biz.presumptive_income_44AD
    elif biz.presumptive_income_44ADA > 0:
        pgbp_income = biz.presumptive_income_44ADA
    elif biz.gross_receipts > 0:
        pgbp_income = max(0.0, biz.gross_receipts - biz.expenses - biz.depreciation)
    else:
        pgbp_income = 0.0

    # --- Capital Gains (Sections 45-55) ---
    cg = profile.capital_gains
    stcg_total = cg.stcg_equity + cg.stcg_other
    ltcg_total = max(
        0.0,
        cg.ltcg_equity + cg.ltcg_other
        - cg.ltcg_exemption_54
        - cg.ltcg_exemption_54ec
        - cg.ltcg_exemption_54f,
    )
    cg_income = stcg_total + ltcg_total

    cg_details = {
        "stcg_equity_111a": cg.stcg_equity,
        "stcg_other": cg.stcg_other,
        "ltcg_equity_112a": cg.ltcg_equity,
        "ltcg_other_112": cg.ltcg_other,
        "exemption_54": cg.ltcg_exemption_54,
        "exemption_54ec": cg.ltcg_exemption_54ec,
        "exemption_54f": cg.ltcg_exemption_54f,
        "total_stcg": stcg_total,
        "total_ltcg": ltcg_total,
        "total_cg": cg_income,
    }

    # --- Other Sources (Sections 56-59) ---
    oi = profile.other_income
    other_income = (
        oi.interest_savings
        + oi.interest_fd
        + oi.dividends
        + oi.gifts
        + oi.other
    )

    # --- Head-wise aggregation ---
    head_wise: dict[str, float] = {
        "salary": round(net_salary, 2),
        "house_property": round(hp_income, 2),
        "business_profession": round(pgbp_income, 2),
        "capital_gains": round(cg_income, 2),
        "other_sources": round(other_income, 2),
    }

    gti = round(sum(head_wise.values()), 2)

    return {
        "head_wise_income": head_wise,
        "gross_total_income": gti,
        "salary_details": salary_details,
        "hp_details": hp_result,
        "capital_gains_details": cg_details,
    }


# =====================================================================
# 2. Taxable Income — Old Regime
# =====================================================================

def compute_taxable_income_old_regime(
    profile: TaxpayerProfile,
) -> dict[str, Any]:
    """Compute taxable income under the **Old Tax Regime**.

    Steps:
        1. Compute GTI (with old-regime standard deduction of ₹50,000).
        2. Apply ALL Chapter VI-A deductions (Sections 80C–80U) with
           statutory caps and validations.
        3. Taxable income = GTI − total deductions (floored at 0).

    Args:
        profile: Complete ``TaxpayerProfile``.

    Returns:
        dict with ``taxable_income``, ``deductions_breakdown``,
        ``gross_total_income``, and ``deductions_total``.

    References:
        Chapter VI-A (Sections 80C–80U), Section 16(ia).
    """
    gti_result = compute_gross_total_income(profile)
    gti = gti_result["gross_total_income"]

    # Build the flat dict expected by calculate_total_deductions
    ded = profile.deductions
    is_senior = profile.age >= 60

    deduction_profile: dict[str, Any] = {
        "section_80c": ded.section_80c,
        "section_80ccc": ded.section_80ccc,
        "section_80ccd1": ded.section_80ccd1,
        "section_80ccd1b": ded.section_80ccd1b,
        "employer_nps": ded.section_80ccd2_employer,
        "basic_plus_da": profile.salary.basic + profile.salary.da,
        "is_central_govt": False,
        "premium_self": ded.section_80d_self,
        "premium_parents": ded.section_80d_parents,
        "is_senior": is_senior,
        "is_senior_parents": ded.section_80d_senior_parents,
        "education_loan_interest": ded.section_80e,
        "donations_100pct": ded.section_80g_100pct,
        "donations_50pct": ded.section_80g_50pct,
        "gti": gti,
        "receives_hra": (
            profile.hra_details is not None
            and profile.hra_details.hra_received > 0
        ),
        "rent_paid": ded.section_80gg * 12 if ded.section_80gg > 0 else 0.0,
        "total_income": gti,
        "savings_interest": profile.other_income.interest_savings,
        "disability": ded.section_80u > 0,
        "severe_disability": ded.section_80u >= 125_000,
    }

    ded_result = calculate_total_deductions(deduction_profile)
    total_deductions = ded_result["total_deduction"]

    taxable_income = max(0.0, round(gti - total_deductions, 2))

    return {
        "taxable_income": taxable_income,
        "gross_total_income": gti,
        "deductions_total": total_deductions,
        "deductions_breakdown": ded_result["deductions"],
        "gti_details": gti_result,
    }


# =====================================================================
# 3. Taxable Income — New Regime
# =====================================================================

def compute_taxable_income_new_regime(
    profile: TaxpayerProfile,
) -> dict[str, Any]:
    """Compute taxable income under the **New Tax Regime** (Section 115BAC).

    Under the new regime, most Chapter VI-A deductions are NOT available.
    Only the following are allowed:
        - Standard deduction of ₹75,000 (Section 16(ia), Budget 2024).
        - Employer NPS contribution u/s 80CCD(2) (up to 10%/14% of Basic+DA).

    Steps:
        1. Recompute GTI with new-regime standard deduction (₹75,000).
        2. Allow only 80CCD(2) as deduction.
        3. Taxable income = GTI − allowed deductions.

    Args:
        profile: Complete ``TaxpayerProfile``.

    Returns:
        dict with ``taxable_income``, ``deductions_breakdown``,
        ``gross_total_income``, and ``deductions_total``.

    References:
        Section 115BAC(1A), Section 16(ia), Section 80CCD(2).
    """
    sal = profile.salary

    # --- Gross salary ---
    gross_salary = (
        sal.basic + sal.da + sal.hra_received
        + sal.special_allowance + sal.lta + sal.perquisites
    )

    # New-regime standard deduction is ₹75,000
    std_ded_new = calculate_standard_deduction("new")
    standard_deduction = min(std_ded_new["amount"], gross_salary)

    # Professional tax — still deductible u/s 16(iii)
    professional_tax = min(sal.professional_tax, 2_500.0)

    # NO HRA exemption under new regime
    net_salary = max(
        0.0,
        gross_salary - standard_deduction - professional_tax,
    )

    # House property — same computation
    hp_properties = []
    for hp in profile.house_property:
        hp_properties.append({
            "property_type": "self_occupied" if hp.self_occupied else "let_out",
            "gross_annual_value": hp.annual_rent,
            "municipal_taxes": hp.municipal_taxes,
            "interest_on_loan": hp.home_loan_interest + hp.pre_construction_interest,
        })
    hp_result = calculate_house_property_income(hp_properties)
    hp_income = hp_result["amount"]

    # Business income
    biz = profile.business
    if biz.presumptive_income_44AD > 0:
        pgbp_income = biz.presumptive_income_44AD
    elif biz.presumptive_income_44ADA > 0:
        pgbp_income = biz.presumptive_income_44ADA
    elif biz.gross_receipts > 0:
        pgbp_income = max(0.0, biz.gross_receipts - biz.expenses - biz.depreciation)
    else:
        pgbp_income = 0.0

    # Capital gains
    cg = profile.capital_gains
    stcg_total = cg.stcg_equity + cg.stcg_other
    ltcg_total = max(
        0.0,
        cg.ltcg_equity + cg.ltcg_other
        - cg.ltcg_exemption_54 - cg.ltcg_exemption_54ec - cg.ltcg_exemption_54f,
    )
    cg_income = stcg_total + ltcg_total

    # Other sources
    oi = profile.other_income
    other_income = oi.interest_savings + oi.interest_fd + oi.dividends + oi.gifts + oi.other

    gti = round(
        net_salary + hp_income + pgbp_income + cg_income + other_income, 2,
    )

    # --- Deductions (only 80CCD(2) allowed) ---
    deductions_breakdown: dict[str, Any] = {}
    total_deductions = 0.0

    employer_nps = profile.deductions.section_80ccd2_employer
    if employer_nps > 0:
        basic_plus_da = sal.basic + sal.da
        ccd2_result = calculate_80ccd2(
            employer_nps=employer_nps,
            basic_plus_da=basic_plus_da,
            is_central_govt=False,
        )
        deductions_breakdown["80CCD(2)"] = ccd2_result
        total_deductions += ccd2_result["amount"]

    deductions_breakdown["standard_deduction_new_regime"] = {
        "amount": standard_deduction,
        "section_reference": "Section 16(ia)",
        "explanation": f"Standard deduction (new regime): ₹{standard_deduction:,.0f}.",
    }

    taxable_income = max(0.0, round(gti - total_deductions, 2))

    return {
        "taxable_income": taxable_income,
        "gross_total_income": gti,
        "deductions_total": total_deductions,
        "deductions_breakdown": deductions_breakdown,
        "standard_deduction_applied": standard_deduction,
    }


# =====================================================================
# 4. Regime Comparison
# =====================================================================

def compare_regimes(profile: TaxpayerProfile) -> RegimeComparison:
    """Compare tax liability under Old vs New regime and recommend the optimal one.

    Pipeline:
        1. Compute taxable income under both regimes.
        2. Compute total tax (slab → rebate → surcharge → cess) for each.
        3. Determine which regime has the lower total tax.
        4. Calculate the savings amount.

    Args:
        profile: Complete ``TaxpayerProfile``.

    Returns:
        ``RegimeComparison`` with ``old_regime``, ``new_regime``,
        ``recommended_regime``, and ``savings_amount``.

    References:
        Section 115BAC (regime choice), Section 87A (rebate).
    """
    # Old regime
    old_result = compute_taxable_income_old_regime(profile)
    old_tax = compute_total_tax(
        taxable_income=old_result["taxable_income"],
        total_income=old_result["gross_total_income"],
        age=profile.age,
        regime="OLD",
    )

    # New regime
    new_result = compute_taxable_income_new_regime(profile)
    new_tax = compute_total_tax(
        taxable_income=new_result["taxable_income"],
        total_income=new_result["gross_total_income"],
        age=profile.age,
        regime="NEW",
    )

    # Determine recommendation
    if old_tax.total_tax <= new_tax.total_tax:
        recommended = TaxRegime.OLD
        savings = round(new_tax.total_tax - old_tax.total_tax, 2)
    else:
        recommended = TaxRegime.NEW
        savings = round(old_tax.total_tax - new_tax.total_tax, 2)

    return RegimeComparison(
        old_regime=old_tax,
        new_regime=new_tax,
        recommended_regime=recommended,
        savings_amount=savings,
    )


# =====================================================================
# 5. Deduction Gap Finder
# =====================================================================

def _get_marginal_slab_rate(taxable_income: float, age: int) -> float:
    """Return the marginal slab rate under the Old Regime for gap analysis.

    Args:
        taxable_income: Taxable income under old regime.
        age:            Age as on 31-Mar of the FY.

    Returns:
        Marginal tax rate (float, 0.0 to 0.30).
    """
    if age >= 80:
        # Super senior: 0 up to 5L, 20% up to 10L, 30% above
        if taxable_income <= 5_00_000:
            return 0.0
        elif taxable_income <= 10_00_000:
            return 0.20
        else:
            return 0.30
    elif age >= 60:
        # Senior: 0 up to 3L, 5% up to 5L, 20% up to 10L, 30% above
        if taxable_income <= 3_00_000:
            return 0.0
        elif taxable_income <= 5_00_000:
            return 0.05
        elif taxable_income <= 10_00_000:
            return 0.20
        else:
            return 0.30
    else:
        # Normal: 0 up to 2.5L, 5% up to 5L, 20% up to 10L, 30% above
        if taxable_income <= 2_50_000:
            return 0.0
        elif taxable_income <= 5_00_000:
            return 0.05
        elif taxable_income <= 10_00_000:
            return 0.20
        else:
            return 0.30


def find_deduction_gaps(profile: TaxpayerProfile) -> list[dict[str, Any]]:
    """Identify missed or underutilised deductions under the Old Regime.

    For each major deduction section, compares the amount claimed against
    the statutory limit and computes the potential tax savings if the
    limit were fully utilised (at the taxpayer's marginal slab rate).

    The result is sorted by potential tax savings in descending order.

    Args:
        profile: Complete ``TaxpayerProfile``.

    Returns:
        list of dicts, each with:
            ``section``, ``current_claim``, ``limit``, ``gap``,
            ``potential_tax_savings``, ``suggestion``, ``section_reference``.

    References:
        Sections 80C–80U, 80CCE (aggregate cap).
    """
    ded = profile.deductions
    is_senior = profile.age >= 60

    # Compute old-regime taxable income for marginal rate
    old_result = compute_taxable_income_old_regime(profile)
    marginal_rate = _get_marginal_slab_rate(
        old_result["taxable_income"], profile.age,
    )

    gaps: list[dict[str, Any]] = []

    # --- 80C group ---
    claimed_80c = ded.section_80c + ded.section_80ccc + ded.section_80ccd1
    limit_80c = CAP_80C_GROUP
    gap_80c = max(0.0, limit_80c - claimed_80c)
    if gap_80c > 0:
        gaps.append({
            "section": "80C/80CCC/80CCD(1)",
            "current_claim": claimed_80c,
            "limit": limit_80c,
            "gap": gap_80c,
            "potential_tax_savings": round(gap_80c * marginal_rate, 2),
            "suggestion": (
                "Invest in PPF, ELSS, NSC, 5-yr FD, life insurance premium, "
                "tuition fees, or employee PF contribution."
            ),
            "section_reference": "Sections 80C, 80CCC, 80CCD(1) r/w 80CCE",
        })

    # --- 80CCD(1B) ---
    claimed_1b = ded.section_80ccd1b
    limit_1b = CAP_80CCD1B
    gap_1b = max(0.0, limit_1b - claimed_1b)
    if gap_1b > 0:
        gaps.append({
            "section": "80CCD(1B)",
            "current_claim": claimed_1b,
            "limit": limit_1b,
            "gap": gap_1b,
            "potential_tax_savings": round(gap_1b * marginal_rate, 2),
            "suggestion": (
                "Contribute additionally to NPS (Tier I) for an extra "
                "₹50,000 deduction over and above 80C limits."
            ),
            "section_reference": "Section 80CCD(1B)",
        })

    # --- 80D self ---
    claimed_80d_self = ded.section_80d_self
    limit_80d_self = CAP_80D_SENIOR if is_senior else CAP_80D_NORMAL
    gap_80d_self = max(0.0, limit_80d_self - claimed_80d_self)
    if gap_80d_self > 0:
        gaps.append({
            "section": "80D (self & family)",
            "current_claim": claimed_80d_self,
            "limit": limit_80d_self,
            "gap": gap_80d_self,
            "potential_tax_savings": round(gap_80d_self * marginal_rate, 2),
            "suggestion": (
                "Purchase or top-up a health insurance policy for self "
                "and family.  Include preventive health check-up (₹5,000)."
            ),
            "section_reference": "Section 80D",
        })

    # --- 80D parents ---
    claimed_80d_par = ded.section_80d_parents
    limit_80d_par = (
        CAP_80D_SENIOR if ded.section_80d_senior_parents else CAP_80D_NORMAL
    )
    gap_80d_par = max(0.0, limit_80d_par - claimed_80d_par)
    if gap_80d_par > 0:
        gaps.append({
            "section": "80D (parents)",
            "current_claim": claimed_80d_par,
            "limit": limit_80d_par,
            "gap": gap_80d_par,
            "potential_tax_savings": round(gap_80d_par * marginal_rate, 2),
            "suggestion": (
                "Insure your parents under a health policy.  Senior-citizen "
                "parents get a higher cap of ₹50,000."
            ),
            "section_reference": "Section 80D",
        })

    # --- 80TTA / 80TTB ---
    if is_senior:
        claimed_int = ded.section_80ttb
        limit_int = CAP_80TTB
        label = "80TTB"
    else:
        claimed_int = ded.section_80tta
        limit_int = CAP_80TTA
        label = "80TTA"

    gap_int = max(0.0, limit_int - claimed_int)
    if gap_int > 0:
        gaps.append({
            "section": label,
            "current_claim": claimed_int,
            "limit": limit_int,
            "gap": gap_int,
            "potential_tax_savings": round(gap_int * marginal_rate, 2),
            "suggestion": (
                f"Claim the full {label} deduction on savings/deposit interest."
            ),
            "section_reference": f"Section {label}",
        })

    # Sort by potential savings descending
    gaps.sort(key=lambda g: g["potential_tax_savings"], reverse=True)

    return gaps


# =====================================================================
# 6. What-If Scenario Engine
# =====================================================================

def what_if_scenario(
    profile: TaxpayerProfile,
    changes: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate the tax impact of hypothetical changes to the profile.

    Creates a deep copy of the profile, applies the specified changes,
    recalculates tax under both regimes, and reports the difference.

    Supported change keys (examples):
        ``section_80c``       — change 80C investment amount.
        ``section_80ccd1b``   — change additional NPS amount.
        ``section_80d_self``  — change health insurance premium.
        ``section_80d_parents`` — change parents' premium.
        ``home_loan_interest`` — change home loan interest (first property).
        ``interest_fd``       — change FD interest income.

    Args:
        profile: Original ``TaxpayerProfile``.
        changes: Dict of field → new_value pairs.

    Returns:
        dict with:
            ``original_tax`` — tax under recommended regime (original).
            ``modified_tax`` — tax under recommended regime (modified).
            ``savings``      — difference (positive = saved).
            ``regime_change`` — True if recommended regime changed.
            ``details``      — per-regime breakdown for both scenarios.
    """
    # Deep copy so the original is untouched
    modified = profile.model_copy(deep=True)

    # Apply changes
    for key, value in changes.items():
        if hasattr(modified.deductions, key):
            setattr(modified.deductions, key, float(value))
        elif hasattr(modified.other_income, key):
            setattr(modified.other_income, key, float(value))
        elif key == "home_loan_interest" and modified.house_property:
            modified.house_property[0].home_loan_interest = float(value)
        elif hasattr(modified.salary, key):
            setattr(modified.salary, key, float(value))

    # Compute original
    original_comparison = compare_regimes(profile)
    original_recommended = original_comparison.recommended_regime
    original_tax = (
        original_comparison.old_regime.total_tax
        if original_recommended == TaxRegime.OLD
        else original_comparison.new_regime.total_tax
    )

    # Compute modified
    modified_comparison = compare_regimes(modified)
    modified_recommended = modified_comparison.recommended_regime
    modified_tax = (
        modified_comparison.old_regime.total_tax
        if modified_recommended == TaxRegime.OLD
        else modified_comparison.new_regime.total_tax
    )

    return {
        "original_tax": original_tax,
        "modified_tax": modified_tax,
        "savings": round(original_tax - modified_tax, 2),
        "regime_change": original_recommended != modified_recommended,
        "original_regime": original_recommended.value,
        "modified_regime": modified_recommended.value,
        "details": {
            "original": {
                "old_regime_tax": original_comparison.old_regime.total_tax,
                "new_regime_tax": original_comparison.new_regime.total_tax,
                "recommended": original_recommended.value,
            },
            "modified": {
                "old_regime_tax": modified_comparison.old_regime.total_tax,
                "new_regime_tax": modified_comparison.new_regime.total_tax,
                "recommended": modified_recommended.value,
            },
        },
        "changes_applied": changes,
    }


# =====================================================================
# 7. Master Optimisation Report
# =====================================================================

def generate_optimization_report(
    profile: TaxpayerProfile,
) -> dict[str, Any]:
    """Generate a comprehensive tax optimisation report.

    Orchestrates every analysis function in the engine:
        1. Gross Total Income computation.
        2. Old vs New regime comparison.
        3. Deduction gap analysis (missed savings opportunities).
        4. Compliance checks (filing obligation, audit, advance tax).
        5. Filing checklist.

    Args:
        profile: Complete ``TaxpayerProfile``.

    Returns:
        dict with sections:
            ``gross_total_income`` — head-wise income breakdown.
            ``regime_comparison``  — ``RegimeComparison`` model dict.
            ``deduction_gaps``     — list of underutilised deductions.
            ``compliance``         — compliance check results.
            ``filing_checklist``   — actionable filing items.
            ``summary``            — executive summary dict.
    """
    # 1. GTI
    gti_result = compute_gross_total_income(profile)

    # 2. Regime comparison
    comparison = compare_regimes(profile)

    # 3. Deduction gaps
    gaps = find_deduction_gaps(profile)

    # 4. Compliance checks
    compliance_profile: dict[str, Any] = {
        "gross_total_income": gti_result["gross_total_income"],
        "age": profile.age,
        "gross_receipts": profile.business.gross_receipts,
        "estimated_total_tax": min(
            comparison.old_regime.total_tax,
            comparison.new_regime.total_tax,
        ),
        "tds_paid": 0.0,  # TDS not modelled in TaxpayerProfile
        "professional_tax": profile.salary.professional_tax,
        "salary_basic": profile.salary.basic,
        "has_house_property": len(profile.house_property) > 0,
        "section_80c": profile.deductions.section_80c,
        "section_80d_self": profile.deductions.section_80d_self,
        "hra_received": profile.salary.hra_received,
        "has_capital_gains": (
            profile.capital_gains.stcg_equity > 0
            or profile.capital_gains.stcg_other > 0
            or profile.capital_gains.ltcg_equity > 0
            or profile.capital_gains.ltcg_other > 0
        ),
    }
    compliance_result = check_compliance(compliance_profile)

    # 5. Filing checklist
    checklist = get_filing_checklist(compliance_profile)

    # Executive summary
    rec = comparison.recommended_regime.value
    rec_tax = (
        comparison.old_regime.total_tax
        if comparison.recommended_regime == TaxRegime.OLD
        else comparison.new_regime.total_tax
    )
    total_gap_savings = sum(g["potential_tax_savings"] for g in gaps)

    summary = {
        "taxpayer_name": profile.name,
        "financial_year": profile.financial_year.value,
        "gross_total_income": gti_result["gross_total_income"],
        "recommended_regime": rec,
        "tax_under_recommended_regime": rec_tax,
        "regime_savings": comparison.savings_amount,
        "deduction_gaps_count": len(gaps),
        "potential_additional_savings": total_gap_savings,
        "compliance_passed": compliance_result["passed"],
        "compliance_issues": compliance_result["issue_count"],
    }

    return {
        "summary": summary,
        "gross_total_income": gti_result,
        "regime_comparison": comparison.model_dump(),
        "deduction_gaps": gaps,
        "compliance": compliance_result,
        "filing_checklist": checklist,
    }


# =====================================================================
# Test harness
# =====================================================================

if __name__ == "__main__":
    import json

    from .models import (
        TaxpayerProfile,
        SalaryIncome,
        HousePropertyIncome,
        CapitalGains,
        OtherIncome,
        Deductions,
        HRADetails,
    )

    SEPARATOR = "=" * 76

    # ------------------------------------------------------------------
    # Build a sample TaxpayerProfile
    # ------------------------------------------------------------------
    profile = TaxpayerProfile(
        name="Aarav Sharma",
        pan="ABCDE1234F",
        age=32,
        salary=SalaryIncome(
            basic=8_00_000,
            da=1_00_000,
            hra_received=3_00_000,
            special_allowance=2_00_000,
            professional_tax=2_400,
        ),
        house_property=[
            HousePropertyIncome(
                self_occupied=True,
                home_loan_interest=1_50_000,
            ),
        ],
        capital_gains=CapitalGains(
            ltcg_equity=2_00_000,
        ),
        other_income=OtherIncome(
            interest_fd=40_000,
        ),
        deductions=Deductions(
            section_80c=1_20_000,
            section_80d_self=20_000,
        ),
        hra_details=HRADetails(
            basic_salary=8_00_000,
            da=1_00_000,
            hra_received=3_00_000,
            rent_paid=15_000 * 12,    # ₹15,000/month
            is_metro=True,
        ),
    )

    # ------------------------------------------------------------------
    # Generate the full optimisation report
    # ------------------------------------------------------------------
    report = generate_optimization_report(profile)

    # ------------------------------------------------------------------
    # Pretty-print results
    # ------------------------------------------------------------------
    print(f"\n{SEPARATOR}")
    print("  TAX OPTIMISATION REPORT — FY 2024-25 (AY 2025-26)")
    print(SEPARATOR)

    # Executive summary
    s = report["summary"]
    print(f"\n  Taxpayer           : {s['taxpayer_name']}")
    print(f"  Financial Year     : {s['financial_year']}")
    print(f"  Gross Total Income : ₹{s['gross_total_income']:>14,.2f}")
    print(f"  Recommended Regime : {s['recommended_regime']}")
    print(f"  Tax (Recommended)  : ₹{s['tax_under_recommended_regime']:>14,.2f}")
    print(f"  Regime Savings     : ₹{s['regime_savings']:>14,.2f}")
    print(f"  Compliance Passed  : {'✅ Yes' if s['compliance_passed'] else '❌ No'}")
    print(f"  Compliance Issues  : {s['compliance_issues']}")
    print(f"  Deduction Gaps     : {s['deduction_gaps_count']}")
    print(f"  Potential Savings  : ₹{s['potential_additional_savings']:>14,.2f}")

    # Head-wise income
    print(f"\n{SEPARATOR}")
    print("  HEAD-WISE INCOME")
    print(SEPARATOR)
    for head, amount in report["gross_total_income"]["head_wise_income"].items():
        print(f"    {head:<25s} : ₹{amount:>14,.2f}")

    # Regime comparison
    print(f"\n{SEPARATOR}")
    print("  REGIME COMPARISON")
    print(SEPARATOR)
    rc = report["regime_comparison"]
    old = rc["old_regime"]
    new = rc["new_regime"]
    print(f"    {'':30s} {'OLD':>14s}   {'NEW':>14s}")
    print(f"    {'Taxable Income':30s} ₹{old['taxable_income']:>13,.2f}   ₹{new['taxable_income']:>13,.2f}")
    print(f"    {'Total Tax':30s} ₹{old['total_tax']:>13,.2f}   ₹{new['total_tax']:>13,.2f}")
    print(f"    {'Recommended':30s} → {rc['recommended_regime']}")
    print(f"    {'Savings':30s}   ₹{rc['savings_amount']:>13,.2f}")

    # Deduction gaps
    print(f"\n{SEPARATOR}")
    print("  DEDUCTION GAPS (Old Regime)")
    print(SEPARATOR)
    if report["deduction_gaps"]:
        for gap in report["deduction_gaps"]:
            print(f"\n    Section: {gap['section']}")
            print(f"      Current claim  : ₹{gap['current_claim']:>12,.0f}")
            print(f"      Limit          : ₹{gap['limit']:>12,.0f}")
            print(f"      Gap            : ₹{gap['gap']:>12,.0f}")
            print(f"      Tax savings    : ₹{gap['potential_tax_savings']:>12,.2f}")
            print(f"      💡 {gap['suggestion']}")
    else:
        print("    No deduction gaps — all limits fully utilised! 🎉")

    # Compliance
    print(f"\n{SEPARATOR}")
    print("  COMPLIANCE CHECKS")
    print(SEPARATOR)
    for issue in report["compliance"]["issues"]:
        status = issue["status"].upper()
        icon = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "REMINDER": "🔔"}.get(
            status, "•"
        )
        print(f"    {icon} [{status:^8}] {issue['message']}")

    # Filing checklist
    print(f"\n{SEPARATOR}")
    print("  FILING CHECKLIST")
    print(SEPARATOR)
    for i, item in enumerate(report["filing_checklist"], 1):
        priority = item["priority"].upper()
        print(f"    {i:2d}. [{priority:^6}] {item['item']}")
        print(f"        → {item['details']}")

    # What-if scenario demo
    print(f"\n{SEPARATOR}")
    print("  WHAT-IF SCENARIO: Max out 80C to ₹1,50,000")
    print(SEPARATOR)
    scenario = what_if_scenario(profile, {"section_80c": 150_000})
    print(f"    Original tax     : ₹{scenario['original_tax']:>14,.2f}")
    print(f"    Modified tax     : ₹{scenario['modified_tax']:>14,.2f}")
    print(f"    Savings          : ₹{scenario['savings']:>14,.2f}")
    print(f"    Regime changed?  : {'Yes' if scenario['regime_change'] else 'No'}")

    print(f"\n{SEPARATOR}")
    print("  ✅ Full optimisation report generated successfully.")
    print(SEPARATOR)
