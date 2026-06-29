"""
Legal Reference Database — Indian Income Tax Act, 1961.

Structured legal metadata for all commonly used sections, enabling
programmatic lookup, keyword search, and regime-based filtering for
FY 2024-25 (AY 2025-26).

This module provides:
    - ``LEGAL_DATABASE`` : A dict mapping section IDs to their full
      legal metadata (limits, eligibility, regime availability, etc.).
    - ``get_section_info()``  : Direct lookup by section ID.
    - ``search_sections()``   : Case-insensitive keyword search across
      titles, notes, and eligible-investment lists.
    - ``get_deductions_available_in_regime()`` : Filter sections by
      their availability under OLD or NEW tax regime.

References:
    - Income Tax Act, 1961
    - Finance (No. 2) Act, 2024 (Budget 2024 amendments)
"""

from __future__ import annotations

from typing import Any


# =========================================================================
# Legal Database — Section → Metadata
# =========================================================================

LEGAL_DATABASE: dict[str, dict[str, Any]] = {

    # =====================================================================
    # CHAPTER VI-A DEDUCTIONS
    # =====================================================================

    "80C": {
        "section": "Section 80C",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of life insurance premia, deferred annuity, "
            "contributions to provident fund, subscription to certain equity shares "
            "or debentures, etc."
        ),
        "max_limit": 150_000,
        "aggregate_with": ["80CCC", "80CCD(1)"],
        "aggregate_cap_section": "80CCE",
        "aggregate_cap": 150_000,
        "eligible_investments": [
            "ELSS Mutual Funds",
            "PPF (Public Provident Fund)",
            "NSC (National Savings Certificate)",
            "Tax Saving FD (5-year lock-in)",
            "Life Insurance Premium",
            "Home Loan Principal Repayment",
            "SSY (Sukanya Samriddhi Yojana)",
            "NPS Tier-I (Employee contribution)",
            "SCSS (Senior Citizens Savings Scheme)",
            "Tuition Fees (max 2 children)",
            "Stamp Duty and Registration Charges",
        ],
        "available_in_new_regime": False,
        "notes": (
            "Aggregate of 80C + 80CCC + 80CCD(1) cannot exceed ₹1,50,000 "
            "under Section 80CCE. Deduction available only under the Old Regime."
        ),
    },

    "80CCC": {
        "section": "Section 80CCC",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of contribution to certain pension funds."
        ),
        "max_limit": 150_000,
        "aggregate_with": ["80C", "80CCD(1)"],
        "aggregate_cap_section": "80CCE",
        "aggregate_cap": 150_000,
        "eligible_investments": [
            "Annuity plan of LIC",
            "Annuity plan of any other insurer",
        ],
        "available_in_new_regime": False,
        "notes": (
            "Contribution to pension funds of LIC or any other insurer. "
            "Subject to aggregate cap of ₹1,50,000 under Section 80CCE "
            "along with 80C and 80CCD(1). Surrender value or pension "
            "received is taxable in the year of receipt."
        ),
    },

    "80CCD(1)": {
        "section": "Section 80CCD(1)",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of contribution to pension scheme of "
            "Central Government (NPS) — Employee's own contribution."
        ),
        "max_limit": 150_000,
        "salary_cap_pct": 0.10,
        "self_employed_cap_pct": 0.20,
        "aggregate_with": ["80C", "80CCC"],
        "aggregate_cap_section": "80CCE",
        "aggregate_cap": 150_000,
        "eligible_investments": [
            "NPS Tier-I (Employee's own contribution)",
            "Atal Pension Yojana (APY)",
        ],
        "available_in_new_regime": False,
        "notes": (
            "Employee's own contribution to NPS. Capped at 10% of salary "
            "(Basic + DA) for salaried individuals, or 20% of gross total "
            "income for self-employed. Subject to the aggregate ₹1,50,000 "
            "cap under Section 80CCE."
        ),
    },

    "80CCD(1B)": {
        "section": "Section 80CCD(1B)",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Additional deduction in respect of contribution to NPS — "
            "over and above Section 80CCE limit."
        ),
        "max_limit": 50_000,
        "eligible_investments": [
            "NPS Tier-I (additional contribution beyond 80CCE)",
        ],
        "available_in_new_regime": False,
        "notes": (
            "Additional ₹50,000 deduction over and above the ₹1,50,000 "
            "limit of 80CCE. Available only if 80CCD(1) is also claimed. "
            "Not available under the New Tax Regime from FY 2024-25."
        ),
    },

    "80CCD(2)": {
        "section": "Section 80CCD(2)",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of employer's contribution to pension "
            "scheme (NPS)."
        ),
        "max_limit": None,
        "salary_cap_pct_central_govt": 0.14,
        "salary_cap_pct_others": 0.10,
        "eligible_investments": [
            "Employer's contribution to NPS Tier-I",
        ],
        "available_in_new_regime": True,
        "notes": (
            "Employer's contribution to NPS. Capped at 14% of salary "
            "(Basic + DA) for Central Government employees, 10% for others. "
            "This is OUTSIDE the ₹1,50,000 cap of Section 80CCE. "
            "Available under BOTH Old and New tax regimes."
        ),
    },

    "80D": {
        "section": "Section 80D",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of health insurance premia."
        ),
        "max_limit_self_non_senior": 25_000,
        "max_limit_self_senior": 50_000,
        "max_limit_parents_non_senior": 25_000,
        "max_limit_parents_senior": 50_000,
        "preventive_health_checkup": 5_000,
        "eligible_investments": [
            "Health / Mediclaim insurance premium (self, spouse, children)",
            "Health insurance premium for parents",
            "Preventive health check-up (up to ₹5,000, within overall limit)",
            "Medical expenditure for senior citizens (no insurance)",
        ],
        "available_in_new_regime": False,
        "notes": (
            "Self/family: ₹25,000 (₹50,000 if senior citizen ≥ 60 years). "
            "Parents: ₹25,000 (₹50,000 if senior). Preventive health check-up "
            "of ₹5,000 is within the overall limit, not additional. Maximum "
            "combined deduction: ₹1,00,000 (if both self and parents are senior)."
        ),
    },

    "80DD": {
        "section": "Section 80DD",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of maintenance including medical "
            "treatment of a dependent who is a person with disability."
        ),
        "max_limit_normal": 75_000,
        "max_limit_severe": 125_000,
        "available_in_new_regime": False,
        "notes": (
            "Flat deduction for maintenance/medical treatment of a "
            "dependent (spouse, children, parents, siblings) with "
            "disability. Normal disability (40%-79%): ₹75,000. "
            "Severe disability (≥80%): ₹1,25,000. Certificate from "
            "medical authority required. Deduction is fixed — not "
            "dependent on actual expenditure."
        ),
    },

    "80DDB": {
        "section": "Section 80DDB",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of medical treatment of specified "
            "diseases."
        ),
        "max_limit_non_senior": 40_000,
        "max_limit_senior": 100_000,
        "eligible_diseases": [
            "Neurological diseases (dementia, dystonia musculorum, "
            "motor neuron disease, ataxia, chorea, aphasia)",
            "Malignant cancers",
            "AIDS",
            "Chronic renal failure",
            "Haematological disorders (haemophilia, thalassaemia)",
        ],
        "available_in_new_regime": False,
        "notes": (
            "For treatment of specified diseases for self or dependents. "
            "Non-senior: ₹40,000. Senior citizen (≥ 60): ₹1,00,000. "
            "Requires prescription from specialist in a government hospital. "
            "Amount is reduced by insurance reimbursement received."
        ),
    },

    "80E": {
        "section": "Section 80E",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of interest on loan taken for "
            "higher education."
        ),
        "max_limit": None,
        "duration_years": 8,
        "available_in_new_regime": False,
        "notes": (
            "Interest on education loan for higher education of self, "
            "spouse, or children. NO upper cap — the entire interest "
            "amount is deductible. Available for 8 assessment years "
            "starting from the year in which repayment begins, or until "
            "interest is fully repaid, whichever is earlier. "
            "Principal repayment qualifies under Section 80C."
        ),
    },

    "80G": {
        "section": "Section 80G",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of donations to certain funds, "
            "charitable institutions, etc."
        ),
        "max_limit": None,
        "categories": {
            "100_pct_no_limit": (
                "PM National Relief Fund, National Defence Fund, "
                "National Foundation for Communal Harmony, etc."
            ),
            "50_pct_with_limit": (
                "PM Drought Relief Fund, any other fund/institution "
                "approved u/s 80G(5) — limited to 10% of adjusted "
                "gross total income."
            ),
            "100_pct_with_limit": (
                "Local authority/institution for family planning — "
                "limited to 10% of adjusted GTI."
            ),
            "50_pct_no_limit": (
                "Jawaharlal Nehru Memorial Fund, PM Memorial Fund, etc."
            ),
        },
        "available_in_new_regime": False,
        "notes": (
            "Deduction depends on the category of the donee. Donations "
            "above ₹2,000 must be made via modes other than cash. "
            "For 50% category with qualifying limit, donation is "
            "restricted to 10% of adjusted gross total income."
        ),
    },

    "80GG": {
        "section": "Section 80GG",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of rent paid when HRA is not part "
            "of salary."
        ),
        "max_limit_monthly": 5_000,
        "formula": (
            "Least of: (a) ₹5,000/month (₹60,000/year); "
            "(b) 25% of total income; "
            "(c) Rent paid minus 10% of total income."
        ),
        "available_in_new_regime": False,
        "notes": (
            "Available ONLY when the assessee does NOT receive HRA. "
            "Mutually exclusive with HRA exemption under Section 10(13A). "
            "The assessee, spouse, or minor child must not own residential "
            "accommodation at the place of employment. Form 10BA must be "
            "filed."
        ),
    },

    "80TTA": {
        "section": "Section 80TTA",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of interest on deposits in "
            "savings account."
        ),
        "max_limit": 10_000,
        "available_in_new_regime": False,
        "notes": (
            "Interest on savings accounts (bank, co-operative society, "
            "post office) up to ₹10,000. Excludes FD/RD interest. "
            "Available to individuals and HUFs who are NOT senior "
            "citizens. Mutually exclusive with Section 80TTB."
        ),
    },

    "80TTB": {
        "section": "Section 80TTB",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in respect of interest on deposits for "
            "senior citizens."
        ),
        "max_limit": 50_000,
        "available_in_new_regime": False,
        "notes": (
            "Interest from savings accounts, fixed deposits, and "
            "recurring deposits up to ₹50,000. Available ONLY to "
            "senior citizens (age ≥ 60 years). Covers interest from "
            "banks, co-operative societies, and post offices. "
            "Mutually exclusive with Section 80TTA."
        ),
    },

    "80U": {
        "section": "Section 80U",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VI-A",
        "title": (
            "Deduction in case of a person with disability."
        ),
        "max_limit_normal": 75_000,
        "max_limit_severe": 125_000,
        "available_in_new_regime": False,
        "notes": (
            "Flat deduction for a RESIDENT INDIVIDUAL who is certified "
            "as a person with disability by the medical authority defined "
            "under the Persons with Disabilities Act, 1995. "
            "Normal disability (40%-79%): ₹75,000. "
            "Severe disability (≥80%): ₹1,25,000. "
            "Not dependent on any expenditure."
        ),
    },

    # =====================================================================
    # EXEMPTIONS — Section 10, Section 16
    # =====================================================================

    "10(13A)": {
        "section": "Section 10(13A)",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter III — Incomes which do not form part of total income",
        "title": (
            "House Rent Allowance (HRA) exemption."
        ),
        "rule": "Rule 2A of Income Tax Rules, 1962",
        "formula": (
            "Exempt = minimum of: "
            "(a) Actual HRA received; "
            "(b) 50% of (Basic + DA) for metro cities / 40% for non-metro; "
            "(c) Rent paid minus 10% of (Basic + DA)."
        ),
        "metro_cities": ["Delhi", "Mumbai", "Kolkata", "Chennai"],
        "available_in_new_regime": False,
        "notes": (
            "Available only to salaried employees who receive HRA as part "
            "of salary and actually pay rent. Mutually exclusive with "
            "Section 80GG. If annual rent exceeds ₹1,00,000, the landlord's "
            "PAN must be provided. Not available under the New Tax Regime."
        ),
    },

    "10(5)": {
        "section": "Section 10(5)",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter III — Incomes which do not form part of total income",
        "title": (
            "Leave Travel Allowance / Concession (LTA/LTC) exemption."
        ),
        "block_year": "2022-2025",
        "journeys_per_block": 2,
        "available_in_new_regime": False,
        "notes": (
            "Exempt to the extent of actual domestic travel expenditure. "
            "Only travel fare is covered — boarding, lodging, and local "
            "conveyance are excluded. Economy class air fare or AC first "
            "class rail fare is the upper limit. Available for 2 journeys "
            "in a block of 4 calendar years (current block: 2022-2025). "
            "Family includes spouse, children (max 2 born after 01-Oct-1998), "
            "and dependent parents/siblings."
        ),
    },

    "16(ia)": {
        "section": "Section 16(ia)",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter IV — Computation of Income — Salaries",
        "title": (
            "Standard Deduction from salary income."
        ),
        "amount_old_regime": 50_000,
        "amount_new_regime": 75_000,
        "available_in_new_regime": True,
        "notes": (
            "Flat standard deduction from salary/pension income. "
            "Old Regime: ₹50,000 (since FY 2018-19). "
            "New Regime: ₹75,000 (enhanced from ₹50,000 by Budget 2024). "
            "Available under BOTH regimes. No documentation required."
        ),
    },

    # =====================================================================
    # HOUSE PROPERTY — Section 24
    # =====================================================================

    "24(a)": {
        "section": "Section 24(a)",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter IV — Computation of Income — House Property",
        "title": (
            "Standard deduction from Net Annual Value of house property."
        ),
        "rate": 0.30,
        "available_in_new_regime": True,
        "notes": (
            "A flat 30% of Net Annual Value (NAV) is allowed as standard "
            "deduction for repairs, collection charges, etc. No actual "
            "expenditure need be proved. For self-occupied property, "
            "NAV is nil, so this deduction is effectively zero. "
            "Available under both regimes."
        ),
    },

    "24(b)": {
        "section": "Section 24(b)",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter IV — Computation of Income — House Property",
        "title": (
            "Deduction of interest on borrowed capital for house property."
        ),
        "max_limit_self_occupied": 200_000,
        "max_limit_let_out": None,
        "pre_1999_limit": 30_000,
        "available_in_new_regime": True,
        "notes": (
            "Self-occupied property: Interest capped at ₹2,00,000 per year "
            "(₹30,000 if loan taken before 01-Apr-1999 or not for "
            "acquisition/construction). Let-out property: No cap on "
            "interest deduction. Pre-construction interest is deductible "
            "in 5 equal annual instalments from the year of completion. "
            "Available under both regimes (but HP loss set-off capped at "
            "₹2,00,000 under Section 71(3A) in new regime as well)."
        ),
    },

    # =====================================================================
    # CAPITAL GAINS — Sections 54, 54EC, 54F, 111A, 112, 112A
    # =====================================================================

    "54": {
        "section": "Section 54",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter IV — Computation of Income — Capital Gains",
        "title": (
            "Exemption of LTCG on sale of residential house property "
            "on purchase/construction of another residential house."
        ),
        "max_limit": 10_00_00_000,
        "time_limit_purchase": "1 year before or 2 years after transfer",
        "time_limit_construction": "3 years after transfer",
        "available_in_new_regime": True,
        "notes": (
            "Exemption from LTCG arising on transfer of a residential "
            "house property, provided the assessee purchases or constructs "
            "another residential house within the specified time limits. "
            "The exemption is proportional if only part of the sale "
            "consideration is reinvested. Capped at ₹10 crore from "
            "FY 2023-24 onwards. If the new house is transferred within "
            "3 years, the exemption is reversed."
        ),
    },

    "54EC": {
        "section": "Section 54EC",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter IV — Computation of Income — Capital Gains",
        "title": (
            "Exemption of LTCG on investment in specified bonds."
        ),
        "max_limit": 50_00_000,
        "lock_in_years": 5,
        "eligible_bonds": ["NHAI", "REC", "IRFC", "PFC"],
        "time_limit": "Within 6 months from the date of transfer",
        "available_in_new_regime": True,
        "notes": (
            "Exemption on LTCG from transfer of land or building (or both) "
            "by investing in specified bonds (NHAI/REC/IRFC/PFC) within "
            "6 months. Maximum investment: ₹50,00,000. Lock-in period: "
            "5 years. If bonds are transferred/redeemed before 5 years, "
            "the exemption is reversed."
        ),
    },

    "54F": {
        "section": "Section 54F",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter IV — Computation of Income — Capital Gains",
        "title": (
            "Exemption of LTCG on transfer of any long-term capital asset "
            "(other than a residential house) on purchase/construction of "
            "a residential house."
        ),
        "max_limit": 10_00_00_000,
        "time_limit_purchase": "1 year before or 2 years after transfer",
        "time_limit_construction": "3 years after transfer",
        "available_in_new_regime": True,
        "notes": (
            "Full exemption if the entire net consideration is invested in "
            "a new residential house; proportional if partially invested. "
            "The assessee must not own more than one residential house "
            "(other than the new house) on the date of transfer. "
            "Capped at ₹10 crore from FY 2023-24. If the new house is "
            "sold within 3 years, exemption is reversed."
        ),
    },

    "111A": {
        "section": "Section 111A",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter XII — Special Provisions for tax on certain income",
        "title": (
            "Tax on short-term capital gains from transfer of listed "
            "equity shares / equity-oriented mutual funds (where STT paid)."
        ),
        "tax_rate": 0.20,
        "available_in_new_regime": True,
        "notes": (
            "STCG on listed equity shares or units of equity-oriented MFs "
            "on which STT is paid. Flat rate: 20% (increased from 15% by "
            "Finance (No. 2) Act, 2024, effective 23-Jul-2024). "
            "Surcharge and cess apply additionally. "
            "Available under both regimes."
        ),
    },

    "112": {
        "section": "Section 112",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter XII — Special Provisions for tax on certain income",
        "title": (
            "Tax on long-term capital gains (assets other than those "
            "covered under Section 112A)."
        ),
        "tax_rate": 0.125,
        "available_in_new_regime": True,
        "notes": (
            "Post-Budget 2024: LTCG on all assets (other than listed "
            "equity under 112A) taxed at 12.5% WITHOUT indexation "
            "(previously 20% with indexation). Grandfathering provisions "
            "apply for assets acquired before 23-Jul-2024. "
            "Surcharge and cess apply additionally."
        ),
    },

    "112A": {
        "section": "Section 112A",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter XII — Special Provisions for tax on certain income",
        "title": (
            "Tax on long-term capital gains from transfer of listed "
            "equity shares / equity-oriented mutual funds (where STT paid)."
        ),
        "tax_rate": 0.125,
        "exemption_threshold": 125_000,
        "available_in_new_regime": True,
        "notes": (
            "LTCG on listed equity shares or units of equity-oriented MFs "
            "on which STT is paid at both acquisition and transfer. "
            "Rate: 12.5% (increased from 10% by Budget 2024). "
            "Annual exemption: ₹1,25,000 (increased from ₹1,00,000). "
            "No indexation benefit. Surcharge and cess apply additionally."
        ),
    },

    # =====================================================================
    # REBATE — Section 87A
    # =====================================================================

    "87A": {
        "section": "Section 87A",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter VIII-A — Rebates and relief",
        "title": (
            "Rebate of income tax in case of certain individuals."
        ),
        "old_regime_income_limit": 500_000,
        "old_regime_max_rebate": 12_500,
        "new_regime_income_limit": 700_000,
        "new_regime_max_rebate": 25_000,
        "available_in_new_regime": True,
        "notes": (
            "Old Regime: If taxable income ≤ ₹5,00,000, rebate up to "
            "₹12,500 (effectively zero tax up to ₹5 L). "
            "New Regime: If taxable income ≤ ₹7,00,000, rebate up to "
            "₹25,000 (effectively zero tax up to ₹7 L). "
            "Available only to RESIDENT INDIVIDUALS. "
            "Rebate is applied before surcharge and cess."
        ),
    },

    # =====================================================================
    # TAX REGIME — Section 115BAC
    # =====================================================================

    "115BAC": {
        "section": "Section 115BAC",
        "act": "Income Tax Act, 1961",
        "chapter": "Chapter XII-A — Special rate of income tax",
        "title": (
            "Tax on income of individuals and HUFs under the New "
            "Tax Regime."
        ),
        "slabs_fy_2024_25": [
            {"range": "₹0 – ₹3,00,000", "rate": "Nil"},
            {"range": "₹3,00,001 – ₹7,00,000", "rate": "5%"},
            {"range": "₹7,00,001 – ₹10,00,000", "rate": "10%"},
            {"range": "₹10,00,001 – ₹12,00,000", "rate": "15%"},
            {"range": "₹12,00,001 – ₹15,00,000", "rate": "20%"},
            {"range": "Above ₹15,00,000", "rate": "30%"},
        ],
        "default_regime": True,
        "available_in_new_regime": True,
        "allowed_deductions_new_regime": [
            "16(ia) — Standard Deduction (₹75,000)",
            "80CCD(2) — Employer's NPS contribution",
            "80JJAA — Employment of new employees",
            "24(a) — Standard deduction on HP (30% of NAV)",
            "24(b) — Interest on home loan (for HP income computation)",
            "Section 57(iia) — Family pension deduction (₹15,000)",
        ],
        "notes": (
            "Default regime from FY 2023-24 onwards. Individuals must "
            "explicitly opt out to use the Old Regime. Most Chapter VI-A "
            "deductions and Section 10 exemptions (HRA, LTA) are NOT "
            "available. Key deductions still available: Standard Deduction "
            "u/s 16(ia) at ₹75,000 and employer NPS u/s 80CCD(2). "
            "Surcharge capped at 25% for income above ₹5 crore."
        ),
    },
}


# =========================================================================
# Lookup Functions
# =========================================================================

def get_section_info(section_id: str) -> dict[str, Any] | None:
    """Retrieve legal metadata for a given section ID.

    Args:
        section_id: The section identifier, e.g. ``"80C"``, ``"10(13A)"``,
                    ``"112A"``, ``"87A"``. Case-sensitive match against
                    the ``LEGAL_DATABASE`` keys.

    Returns:
        The metadata dict for the section, or ``None`` if not found.

    Example::

        >>> info = get_section_info("80C")
        >>> info["max_limit"]
        150000
    """
    return LEGAL_DATABASE.get(section_id)


def search_sections(keyword: str) -> list[dict[str, Any]]:
    """Search across all sections for a keyword (case-insensitive).

    Searches within:
        - ``title``
        - ``notes``
        - ``eligible_investments`` (if present)

    Args:
        keyword: The search term. Must be non-empty.

    Returns:
        A list of matching section metadata dicts. Each dict includes
        an additional ``"_section_id"`` key for identification.

    Example::

        >>> results = search_sections("NPS")
        >>> len(results) >= 3
        True
    """
    if not keyword or not keyword.strip():
        return []

    keyword_lower = keyword.strip().lower()
    matches: list[dict[str, Any]] = []

    for section_id, info in LEGAL_DATABASE.items():
        found = False

        # Search in title
        if keyword_lower in info.get("title", "").lower():
            found = True

        # Search in notes
        if not found and keyword_lower in info.get("notes", "").lower():
            found = True

        # Search in eligible_investments
        if not found:
            investments = info.get("eligible_investments", [])
            for inv in investments:
                if keyword_lower in inv.lower():
                    found = True
                    break

        if found:
            result = dict(info)
            result["_section_id"] = section_id
            matches.append(result)

    return matches


def get_deductions_available_in_regime(regime: str) -> list[dict[str, Any]]:
    """Filter sections by their availability under a given tax regime.

    Args:
        regime: ``"OLD"`` or ``"NEW"`` (case-insensitive).

    Returns:
        A list of section metadata dicts available under the specified
        regime. Each dict includes an additional ``"_section_id"`` key.

    Raises:
        ValueError: If *regime* is not ``"OLD"`` or ``"NEW"``.

    Example::

        >>> new_regime_sections = get_deductions_available_in_regime("NEW")
        >>> any(s["_section_id"] == "80CCD(2)" for s in new_regime_sections)
        True
        >>> any(s["_section_id"] == "80C" for s in new_regime_sections)
        False
    """
    regime_upper = regime.strip().upper()
    if regime_upper not in ("OLD", "NEW"):
        raise ValueError(
            f"Invalid regime '{regime}'. Must be 'OLD' or 'NEW'."
        )

    results: list[dict[str, Any]] = []

    for section_id, info in LEGAL_DATABASE.items():
        available_in_new = info.get("available_in_new_regime", False)

        if regime_upper == "NEW" and available_in_new:
            result = dict(info)
            result["_section_id"] = section_id
            results.append(result)
        elif regime_upper == "OLD":
            # Under old regime, ALL sections are available
            result = dict(info)
            result["_section_id"] = section_id
            results.append(result)

    return results


# =========================================================================
# Quick-Test Harness
# =========================================================================

if __name__ == "__main__":
    print("=" * 72)
    print("LEGAL DATABASE — Test Cases")
    print("=" * 72)

    # --- Test 1: Direct lookup ---
    info = get_section_info("80C")
    assert info is not None
    assert info["max_limit"] == 150_000
    assert info["available_in_new_regime"] is False
    print(f"[PASS] get_section_info('80C'): {info['title'][:60]}...")

    # --- Test 2: Lookup non-existent section ---
    assert get_section_info("99Z") is None
    print("[PASS] get_section_info('99Z'): returns None")

    # --- Test 3: Lookup HRA ---
    info = get_section_info("10(13A)")
    assert info is not None
    assert "HRA" in info["title"]
    print(f"[PASS] get_section_info('10(13A)'): {info['title']}")

    # --- Test 4: Search for 'NPS' ---
    results = search_sections("NPS")
    section_ids = [r["_section_id"] for r in results]
    assert "80CCD(1)" in section_ids
    assert "80CCD(1B)" in section_ids
    assert "80CCD(2)" in section_ids
    print(f"[PASS] search_sections('NPS'): found {len(results)} sections — {section_ids}")

    # --- Test 5: Search for 'senior' ---
    results = search_sections("senior")
    assert len(results) >= 3  # 80TTB, 80DDB, 80U, etc.
    print(f"[PASS] search_sections('senior'): found {len(results)} sections")

    # --- Test 6: Search for 'PPF' ---
    results = search_sections("PPF")
    assert any(r["_section_id"] == "80C" for r in results)
    print(f"[PASS] search_sections('PPF'): found in 80C eligible investments")

    # --- Test 7: Search empty keyword ---
    assert search_sections("") == []
    assert search_sections("   ") == []
    print("[PASS] search_sections(''): returns empty list")

    # --- Test 8: NEW regime sections ---
    new_sections = get_deductions_available_in_regime("NEW")
    new_ids = [s["_section_id"] for s in new_sections]
    assert "80CCD(2)" in new_ids       # allowed in new
    assert "16(ia)" in new_ids          # allowed in new
    assert "87A" in new_ids             # allowed in new
    assert "80C" not in new_ids         # NOT allowed in new
    assert "80D" not in new_ids         # NOT allowed in new
    assert "10(13A)" not in new_ids     # NOT allowed in new
    print(f"[PASS] NEW regime sections: {len(new_sections)} available — {new_ids}")

    # --- Test 9: OLD regime sections (all available) ---
    old_sections = get_deductions_available_in_regime("OLD")
    assert len(old_sections) == len(LEGAL_DATABASE)
    print(f"[PASS] OLD regime sections: all {len(old_sections)} available")

    # --- Test 10: Invalid regime ---
    try:
        get_deductions_available_in_regime("HYBRID")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("[PASS] Invalid regime raises ValueError")

    # --- Test 11: All sections present ---
    expected_sections = [
        "80C", "80CCC", "80CCD(1)", "80CCD(1B)", "80CCD(2)",
        "80D", "80DD", "80DDB", "80E", "80G", "80GG",
        "80TTA", "80TTB", "80U",
        "10(13A)", "10(5)", "16(ia)",
        "24(a)", "24(b)",
        "54", "54EC", "54F", "111A", "112", "112A",
        "87A", "115BAC",
    ]
    for sec in expected_sections:
        assert sec in LEGAL_DATABASE, f"Missing section: {sec}"
    print(f"[PASS] All {len(expected_sections)} expected sections present")

    print(f"\n✅ All legal_db tests passed. Database has {len(LEGAL_DATABASE)} sections.")
