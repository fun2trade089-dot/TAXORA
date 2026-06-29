"""
Pydantic data models for Indian Income Tax computation engine.

All models correspond to schedules and sections of the Income Tax Act, 1961
as applicable for Financial Year 2024-25 (Assessment Year 2025-26).

Monetary amounts are in INR (float). Booleans default to False.
All numeric fields default to 0.0 unless otherwise noted.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class TaxRegime(str, Enum):
    """Tax regime selection per Section 115BAC of the Income Tax Act, 1961.

    OLD — the regular / default regime with full deductions & exemptions.
    NEW — the simplified concessional regime introduced in Budget 2020 and
          made default from FY 2023-24 onwards.
    """
    OLD = "OLD"
    NEW = "NEW"


class ResidentialStatus(str, Enum):
    """Residential status as determined under Section 6 of the IT Act.

    RESIDENT       — Resident and Ordinarily Resident (ROR).
    NRI            — Non-Resident Indian.
    RNOR           — Resident but Not Ordinarily Resident.
    """
    RESIDENT = "RESIDENT"
    NRI = "NRI"
    RNOR = "RNOR"


class FinancialYear(str, Enum):
    """Supported financial years.

    Currently only FY 2024-25 (AY 2025-26) is implemented.
    """
    FY_2024_25 = "FY_2024_25"


# ---------------------------------------------------------------------------
# Income Head Models
# ---------------------------------------------------------------------------

class SalaryIncome(BaseModel):
    """Income under the head 'Salaries' — Section 15 to 17.

    Attributes:
        basic:                Basic salary received during the FY.
        da:                   Dearness Allowance (forms part of salary for
                              retirement-benefit computation).
        hra_received:         House Rent Allowance received — Section 10(13A).
        special_allowance:    Any special allowance that is fully taxable.
        lta:                  Leave Travel Allowance — Section 10(5).
                              Only the *taxable* portion should be entered here
                              (excess over exemption).
        perquisites:          Value of perquisites — Section 17(2).
        employer_nps:         Employer's contribution to NPS — exempt up to
                              10 % of salary under Section 80CCD(2).
        professional_tax:     Professional / employment tax paid — deductible
                              under Section 16(iii), max ₹2,500.
        standard_deduction:   Standard deduction under Section 16(ia).
                              ₹75,000 for FY 2024-25 (₹50,000 prior years).
    """
    basic: float = Field(default=0.0, ge=0, description="Basic salary (INR)")
    da: float = Field(default=0.0, ge=0, description="Dearness Allowance (INR)")
    hra_received: float = Field(default=0.0, ge=0, description="HRA received (INR)")
    special_allowance: float = Field(default=0.0, ge=0, description="Special allowance (INR)")
    lta: float = Field(default=0.0, ge=0, description="Taxable LTA (INR)")
    perquisites: float = Field(default=0.0, ge=0, description="Perquisites value (INR)")
    employer_nps: float = Field(default=0.0, ge=0, description="Employer NPS contribution (INR)")
    professional_tax: float = Field(default=0.0, ge=0, description="Professional tax paid (INR)")
    standard_deduction: float = Field(default=75_000.0, ge=0, description="Standard deduction u/s 16(ia) (INR)")


class HousePropertyIncome(BaseModel):
    """Income from House Property — Sections 22 to 27.

    Each instance represents ONE property. A taxpayer may hold multiple
    properties; ``TaxpayerProfile.house_property`` is therefore a list.

    Attributes:
        self_occupied:           True if the property is self-occupied (SOP).
                                 Only TWO properties may be claimed as SOP
                                 from FY 2019-20 onwards — Section 23(2).
        annual_rent:             Gross Annual Value (GAV) for let-out property.
                                 Zero for self-occupied property.
        municipal_taxes:         Municipal taxes actually paid during the FY.
        home_loan_interest:      Interest on housing loan — deductible under
                                 Section 24(b).  Limit ₹2,00,000 for SOP
                                 (₹30,000 if loan taken before 01-Apr-1999).
        pre_construction_interest: Interest for the pre-construction period —
                                 deductible in five equal instalments starting
                                 from the year of completion (Section 24(b)
                                 proviso).
    """
    self_occupied: bool = Field(default=True, description="Is the property self-occupied?")
    annual_rent: float = Field(default=0.0, ge=0, description="Gross annual rent received (INR)")
    municipal_taxes: float = Field(default=0.0, ge=0, description="Municipal taxes paid (INR)")
    home_loan_interest: float = Field(default=0.0, ge=0, description="Home loan interest u/s 24(b) (INR)")
    pre_construction_interest: float = Field(default=0.0, ge=0, description="Pre-construction interest (INR)")


class BusinessIncome(BaseModel):
    """Income from Business or Profession — Sections 28 to 44DB.

    Supports both regular computation and presumptive taxation.

    Attributes:
        gross_receipts:           Total gross receipts / turnover.
        expenses:                 Allowable business expenses (regular scheme).
        depreciation:             Depreciation under Section 32.
        presumptive_income_44AD:  Presumptive income for eligible businesses
                                  — Section 44AD (8 %/6 % of turnover, limit
                                  ₹3 Cr if digital receipts ≥ 95 %).
        presumptive_income_44ADA: Presumptive income for specified
                                  professions — Section 44ADA (50 % of gross
                                  receipts, limit ₹75 L).
    """
    gross_receipts: float = Field(default=0.0, ge=0, description="Gross receipts / turnover (INR)")
    expenses: float = Field(default=0.0, ge=0, description="Total allowable expenses (INR)")
    depreciation: float = Field(default=0.0, ge=0, description="Depreciation u/s 32 (INR)")
    presumptive_income_44AD: float = Field(default=0.0, ge=0, description="Presumptive income u/s 44AD (INR)")
    presumptive_income_44ADA: float = Field(default=0.0, ge=0, description="Presumptive income u/s 44ADA (INR)")


class CapitalGains(BaseModel):
    """Income from Capital Gains — Sections 45 to 55A.

    Post Finance Act 2024 amendments (effective 23-Jul-2024):
    - STCG on listed equity / equity MFs (Section 111A): 20 %
    - LTCG on listed equity / equity MFs (Section 112A): 12.5 % above ₹1.25 L
    - LTCG on other assets (Section 112): 12.5 % (no indexation)

    Attributes:
        stcg_equity:          STCG on equity — Section 111A.
        stcg_other:           STCG on non-equity assets — taxed at slab rate.
        ltcg_equity:          LTCG on listed equity / equity MFs — Section 112A.
        ltcg_other:           LTCG on other assets — Section 112.
        ltcg_exemption_54:    Exemption u/s 54 (sale of residential house).
        ltcg_exemption_54ec:  Exemption u/s 54EC (investment in bonds, max ₹50 L).
        ltcg_exemption_54f:   Exemption u/s 54F (sale of any asset other than house).
    """
    stcg_equity: float = Field(default=0.0, ge=0, description="STCG on equity u/s 111A (INR)")
    stcg_other: float = Field(default=0.0, ge=0, description="STCG on other assets (INR)")
    ltcg_equity: float = Field(default=0.0, ge=0, description="LTCG on equity u/s 112A (INR)")
    ltcg_other: float = Field(default=0.0, ge=0, description="LTCG on other assets u/s 112 (INR)")
    ltcg_exemption_54: float = Field(default=0.0, ge=0, description="Exemption u/s 54 (INR)")
    ltcg_exemption_54ec: float = Field(default=0.0, ge=0, description="Exemption u/s 54EC (INR)")
    ltcg_exemption_54f: float = Field(default=0.0, ge=0, description="Exemption u/s 54F (INR)")


class OtherIncome(BaseModel):
    """Income from Other Sources — Sections 56 to 59.

    Attributes:
        interest_savings:  Interest on savings bank accounts.
        interest_fd:       Interest on fixed deposits / recurring deposits.
        dividends:         Dividend income (taxable at slab rate from FY 2020-21).
        gifts:             Aggregate value of gifts received — Section 56(2)(x).
                           Taxable if > ₹50,000 in a year (subject to exemptions).
        other:             Any other income not classified above.
    """
    interest_savings: float = Field(default=0.0, ge=0, description="Savings account interest (INR)")
    interest_fd: float = Field(default=0.0, ge=0, description="FD / RD interest (INR)")
    dividends: float = Field(default=0.0, ge=0, description="Dividend income (INR)")
    gifts: float = Field(default=0.0, ge=0, description="Taxable gifts u/s 56(2)(x) (INR)")
    other: float = Field(default=0.0, ge=0, description="Other miscellaneous income (INR)")


# ---------------------------------------------------------------------------
# Deductions Model (Chapter VI-A)
# ---------------------------------------------------------------------------

class Deductions(BaseModel):
    """Deductions under Chapter VI-A — Sections 80C to 80U.

    These deductions are available ONLY under the Old Tax Regime.

    Limits (FY 2024-25):
        80C + 80CCC + 80CCD(1) aggregate cap : ₹1,50,000
        80CCD(1B)                              : additional ₹50,000
        80CCD(2)                               : no overall cap (10 % of salary)
        80D  self + family                     : ₹25,000 (₹50,000 if senior)
        80D  parents                           : ₹25,000 (₹50,000 if senior)
        80E                                    : no cap (interest only)
        80G  100 % / 50 %                      : as applicable
        80GG                                   : min of (rent − 10 % ATI, ₹5,000/month, 25 % ATI)
        80TTA                                  : ₹10,000 (non-senior)
        80TTB                                  : ₹50,000 (senior citizens only)
        80U                                    : ₹75,000 / ₹1,25,000
        80DD                                   : ₹75,000 / ₹1,25,000
        80DDB                                  : ₹40,000 / ₹1,00,000 (senior)

    Attributes follow the section naming convention.
    """
    # --- Section 80C / 80CCC / 80CCD ---
    section_80c: float = Field(default=0.0, ge=0, description="Investments u/s 80C (INR)")
    section_80ccc: float = Field(default=0.0, ge=0, description="Pension fund contribution u/s 80CCC (INR)")
    section_80ccd1: float = Field(default=0.0, ge=0, description="Employee NPS contribution u/s 80CCD(1) (INR)")
    section_80ccd1b: float = Field(default=0.0, ge=0, description="Additional NPS u/s 80CCD(1B) (INR)")
    section_80ccd2_employer: float = Field(default=0.0, ge=0, description="Employer NPS u/s 80CCD(2) (INR)")

    # --- Section 80D (Medical Insurance) ---
    section_80d_self: float = Field(default=0.0, ge=0, description="Mediclaim — self & family (INR)")
    section_80d_parents: float = Field(default=0.0, ge=0, description="Mediclaim — parents (INR)")
    section_80d_senior_self: bool = Field(default=False, description="Is self/spouse a senior citizen for 80D?")
    section_80d_senior_parents: bool = Field(default=False, description="Are parents senior citizens for 80D?")

    # --- Section 80E (Education Loan Interest) ---
    section_80e: float = Field(default=0.0, ge=0, description="Education loan interest u/s 80E (INR)")

    # --- Section 80G (Donations) ---
    section_80g_100pct: float = Field(default=0.0, ge=0, description="Donations eligible for 100% deduction u/s 80G (INR)")
    section_80g_50pct: float = Field(default=0.0, ge=0, description="Donations eligible for 50% deduction u/s 80G (INR)")

    # --- Section 80GG (Rent paid — no HRA) ---
    section_80gg: float = Field(default=0.0, ge=0, description="Rent deduction u/s 80GG (INR)")

    # --- Section 80TTA / 80TTB (Savings Interest) ---
    section_80tta: float = Field(default=0.0, ge=0, description="Savings interest deduction u/s 80TTA (INR)")
    section_80ttb: float = Field(default=0.0, ge=0, description="Senior citizen interest deduction u/s 80TTB (INR)")

    # --- Section 80U / 80DD / 80DDB (Disability / Medical) ---
    section_80u: float = Field(default=0.0, ge=0, description="Deduction for disability u/s 80U (INR)")
    section_80dd: float = Field(default=0.0, ge=0, description="Deduction for disabled dependent u/s 80DD (INR)")
    section_80ddb: float = Field(default=0.0, ge=0, description="Deduction for medical treatment u/s 80DDB (INR)")


# ---------------------------------------------------------------------------
# HRA Exemption Helper
# ---------------------------------------------------------------------------

class HRADetails(BaseModel):
    """Inputs required to compute HRA exemption under Section 10(13A)
    read with Rule 2A of the Income Tax Rules.

    HRA Exemption = minimum of:
        1. Actual HRA received
        2. Rent paid − 10 % of (Basic + DA)
        3. 50 % of (Basic + DA) for metro cities /
           40 % of (Basic + DA) for non-metro cities

    Attributes:
        basic_salary: Basic salary for the period.
        da:           Dearness Allowance forming part of salary.
        hra_received: HRA actually received from the employer.
        rent_paid:    Rent actually paid for accommodation.
        is_metro:     True if the city is a metro (Mumbai, Delhi,
                      Kolkata, Chennai).
    """
    basic_salary: float = Field(default=0.0, ge=0, description="Basic salary (INR)")
    da: float = Field(default=0.0, ge=0, description="Dearness Allowance (INR)")
    hra_received: float = Field(default=0.0, ge=0, description="HRA received (INR)")
    rent_paid: float = Field(default=0.0, ge=0, description="Rent paid (INR)")
    is_metro: bool = Field(default=False, description="Is the city a metro (Mumbai/Delhi/Kolkata/Chennai)?")


# ---------------------------------------------------------------------------
# Taxpayer Profile (Top-Level Input)
# ---------------------------------------------------------------------------

class TaxpayerProfile(BaseModel):
    """Complete taxpayer profile aggregating all income heads, deductions,
    and personal details required for a full tax computation.

    Attributes:
        name:               Taxpayer's full name.
        pan:                Permanent Account Number (10-character alphanumeric).
        age:                Age of the taxpayer as on 31-Mar of the FY.
                            Determines senior / super-senior slab eligibility.
        residential_status: Residential status under Section 6.
        financial_year:     The financial year for computation.
        salary:             Salary income details.
        house_property:     List of house property incomes (one per property).
        business:           Business / profession income details.
        capital_gains:      Capital gains details.
        other_income:       Income from other sources.
        deductions:         Chapter VI-A deductions.
        hra_details:        HRA exemption computation inputs (optional).
    """
    name: str = Field(default="", description="Taxpayer's full name")
    pan: str = Field(default="", description="PAN (10-char alphanumeric)")
    age: int = Field(default=30, ge=0, le=150, description="Age as on 31-Mar of the FY")
    residential_status: ResidentialStatus = Field(
        default=ResidentialStatus.RESIDENT,
        description="Residential status u/s 6",
    )
    financial_year: FinancialYear = Field(
        default=FinancialYear.FY_2024_25,
        description="Financial year for computation",
    )

    # Income heads
    salary: SalaryIncome = Field(default_factory=SalaryIncome)
    house_property: list[HousePropertyIncome] = Field(default_factory=list)
    business: BusinessIncome = Field(default_factory=BusinessIncome)
    capital_gains: CapitalGains = Field(default_factory=CapitalGains)
    other_income: OtherIncome = Field(default_factory=OtherIncome)

    # Deductions & exemptions
    deductions: Deductions = Field(default_factory=Deductions)
    hra_details: Optional[HRADetails] = Field(default=None, description="HRA exemption inputs")


# ---------------------------------------------------------------------------
# Tax Result Models (Output)
# ---------------------------------------------------------------------------

class TaxResult(BaseModel):
    """Output of a single-regime tax computation.

    Attributes:
        gross_total_income: Sum of all income heads before deductions.
        total_deductions:   Aggregate Chapter VI-A deductions allowed.
        taxable_income:     Gross total income minus deductions.
        tax_before_cess:    Tax on taxable income (after rebate + surcharge,
                            before cess).
        surcharge:          Surcharge on income tax (Section 2(9) read
                            with Finance Act).
        cess:               Health & Education Cess @ 4 % — Section 2(11).
        total_tax:          Final tax liability (tax + surcharge + cess).
        regime:             Which regime was used.
        breakdown:          Detailed slab-wise / component-wise breakdown.
    """
    gross_total_income: float = Field(default=0.0, description="Gross total income (INR)")
    total_deductions: float = Field(default=0.0, description="Total deductions (INR)")
    taxable_income: float = Field(default=0.0, description="Taxable income (INR)")
    tax_before_cess: float = Field(default=0.0, description="Tax after rebate & surcharge, before cess (INR)")
    surcharge: float = Field(default=0.0, description="Surcharge amount (INR)")
    cess: float = Field(default=0.0, description="Health & Education Cess (INR)")
    total_tax: float = Field(default=0.0, description="Total tax payable (INR)")
    regime: TaxRegime = Field(default=TaxRegime.NEW, description="Tax regime used")
    breakdown: dict = Field(default_factory=dict, description="Detailed slab-wise breakdown")


class RegimeComparison(BaseModel):
    """Side-by-side comparison of Old vs New regime tax outcomes.

    Attributes:
        old_regime:          TaxResult under the Old Regime.
        new_regime:          TaxResult under the New Regime.
        recommended_regime:  The regime with the lower total tax.
        savings_amount:      How much the recommended regime saves (INR).
    """
    old_regime: TaxResult = Field(description="Tax computation under Old Regime")
    new_regime: TaxResult = Field(description="Tax computation under New Regime")
    recommended_regime: TaxRegime = Field(description="Regime with lower total tax")
    savings_amount: float = Field(default=0.0, ge=0, description="Tax savings of recommended regime (INR)")
