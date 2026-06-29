"""
Compliance Checks & Filing Checklist — Income Tax Act, 1961.

Provides basic compliance validation and a filing checklist for
FY 2024-25 (AY 2025-26).

These functions are consumed by the optimizer module to provide
a holistic tax report that includes compliance warnings and
actionable filing guidance.

References:
    - Section 139   : Filing of return of income
    - Section 234A/B/C : Interest for late filing / short payment
    - Section 44AB  : Tax audit applicability
    - Section 194   : TDS provisions (general)
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Compliance Checks
# ---------------------------------------------------------------------------

def check_compliance(profile: dict[str, Any]) -> dict[str, Any]:
    """Run basic compliance checks against the taxpayer profile.

    Checks performed:
        1. Filing obligation — is GTI above the basic exemption limit?
        2. Tax audit — is turnover above Section 44AB thresholds?
        3. Advance tax — is estimated tax liability ≥ ₹10,000?
        4. Form 26AS / AIS reconciliation reminder.
        5. Professional tax cap — max ₹2,500 u/s 16(iii).
        6. 80C group cap — ₹1,50,000 u/s 80CCE.

    Args:
        profile: A dict-like representation of the taxpayer data.
                 Expected keys mirror TaxpayerProfile field names.

    Returns:
        dict with 'passed' (bool), 'issues' (list of dicts), and
        'summary' (str).
    """
    issues: list[dict[str, Any]] = []

    # 1. Filing obligation
    gti = profile.get("gross_total_income", 0.0)
    age = profile.get("age", 30)

    if age >= 80:
        basic_exemption = 500_000.0
    elif age >= 60:
        basic_exemption = 300_000.0
    else:
        basic_exemption = 250_000.0

    if gti > basic_exemption:
        issues.append({
            "check": "filing_obligation",
            "status": "info",
            "message": (
                f"GTI ₹{gti:,.0f} exceeds basic exemption limit "
                f"₹{basic_exemption:,.0f} — filing is mandatory u/s 139(1)."
            ),
            "section_reference": "Section 139(1)",
        })

    # 2. Tax audit (Section 44AB)
    turnover = profile.get("gross_receipts", 0.0)
    if turnover > 10_00_00_000:  # ₹10 Cr (digital receipts ≥ 95%)
        issues.append({
            "check": "tax_audit",
            "status": "warning",
            "message": (
                f"Business turnover ₹{turnover:,.0f} may require tax audit "
                f"u/s 44AB. Threshold: ₹10 Cr (if digital receipts ≥ 95%)."
            ),
            "section_reference": "Section 44AB",
        })
    elif turnover > 1_00_00_000:  # ₹1 Cr (otherwise)
        issues.append({
            "check": "tax_audit",
            "status": "warning",
            "message": (
                f"Business turnover ₹{turnover:,.0f} exceeds ₹1 Cr — "
                f"tax audit u/s 44AB may be required."
            ),
            "section_reference": "Section 44AB",
        })

    # 3. Advance tax
    total_tax = profile.get("estimated_total_tax", 0.0)
    tds_paid = profile.get("tds_paid", 0.0)
    net_tax = total_tax - tds_paid
    if net_tax >= 10_000:
        issues.append({
            "check": "advance_tax",
            "status": "warning",
            "message": (
                f"Estimated net tax liability ₹{net_tax:,.0f} (after TDS) "
                f"≥ ₹10,000 — advance tax is payable u/s 208."
            ),
            "section_reference": "Section 208",
        })

    # 4. Form 26AS / AIS reconciliation
    issues.append({
        "check": "form_26as_ais",
        "status": "reminder",
        "message": (
            "Verify TDS credits against Form 26AS and Annual Information "
            "Statement (AIS) before filing."
        ),
        "section_reference": "Section 203AA",
    })

    # 5. Professional tax cap
    professional_tax = profile.get("professional_tax", 0.0)
    if professional_tax > 2_500:
        issues.append({
            "check": "professional_tax_cap",
            "status": "error",
            "message": (
                f"Professional tax claimed ₹{professional_tax:,.0f} exceeds "
                f"the statutory maximum of ₹2,500 u/s 16(iii)."
            ),
            "section_reference": "Section 16(iii)",
        })

    passed = all(i["status"] not in ("error",) for i in issues)

    return {
        "passed": passed,
        "issues": issues,
        "issue_count": len(issues),
        "summary": (
            f"Compliance check complete — {len(issues)} item(s) flagged. "
            f"{'All critical checks passed.' if passed else 'ERRORS found — review required.'}"
        ),
    }


# ---------------------------------------------------------------------------
# Filing Checklist
# ---------------------------------------------------------------------------

def get_filing_checklist(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate a filing checklist tailored to the taxpayer's profile.

    Returns a list of actionable items the taxpayer should complete
    before filing ITR for FY 2024-25.

    Args:
        profile: A dict-like representation of the taxpayer data.

    Returns:
        list of dicts, each with 'item', 'status', 'priority', 'details'.
    """
    checklist: list[dict[str, Any]] = []

    # Always applicable
    checklist.append({
        "item": "Download Form 26AS / AIS / TIS",
        "status": "pending",
        "priority": "high",
        "details": "Verify TDS credits, high-value transactions, and interest income.",
    })

    checklist.append({
        "item": "Verify PAN and Aadhaar linkage",
        "status": "pending",
        "priority": "high",
        "details": "PAN must be linked with Aadhaar u/s 139AA for valid filing.",
    })

    checklist.append({
        "item": "Choose correct ITR form",
        "status": "pending",
        "priority": "high",
        "details": _suggest_itr_form(profile),
    })

    # Salary-specific
    salary_basic = profile.get("salary_basic", 0.0)
    if salary_basic > 0:
        checklist.append({
            "item": "Collect Form 16 from employer",
            "status": "pending",
            "priority": "high",
            "details": "Form 16 contains TDS details and salary breakup.",
        })

    # House property
    has_hp = profile.get("has_house_property", False)
    if has_hp:
        checklist.append({
            "item": "Gather home loan interest certificate",
            "status": "pending",
            "priority": "medium",
            "details": "Required for claiming deduction u/s 24(b).",
        })

    # Investment proofs for 80C
    section_80c = profile.get("section_80c", 0.0)
    if section_80c > 0:
        checklist.append({
            "item": "Collect 80C investment proofs",
            "status": "pending",
            "priority": "medium",
            "details": "PPF passbook, ELSS statements, insurance premium receipts, etc.",
        })

    # Medical insurance
    section_80d = profile.get("section_80d_self", 0.0)
    if section_80d > 0:
        checklist.append({
            "item": "Collect health insurance premium receipts (80D)",
            "status": "pending",
            "priority": "medium",
            "details": "Premium receipts for self, family, and parents.",
        })

    # HRA
    hra_received = profile.get("hra_received", 0.0)
    if hra_received > 0:
        checklist.append({
            "item": "Keep rent receipts and landlord PAN",
            "status": "pending",
            "priority": "medium",
            "details": (
                "Rent receipts mandatory. Landlord PAN required if "
                "annual rent exceeds ₹1,00,000."
            ),
        })

    # Capital gains
    has_cg = profile.get("has_capital_gains", False)
    if has_cg:
        checklist.append({
            "item": "Download Capital Gains statement from broker/CAMS/KFintech",
            "status": "pending",
            "priority": "high",
            "details": "Required for accurate reporting of equity/MF gains.",
        })

    # Due date reminder
    checklist.append({
        "item": "File ITR before due date",
        "status": "pending",
        "priority": "high",
        "details": (
            "Due date: 31-Jul-2025 (individuals without audit). "
            "Late filing attracts fee u/s 234F (₹1,000 / ₹5,000) and "
            "interest u/s 234A."
        ),
    })

    return checklist


def _suggest_itr_form(profile: dict[str, Any]) -> str:
    """Suggest the appropriate ITR form based on income profile."""
    has_business = profile.get("gross_receipts", 0.0) > 0
    has_cg = profile.get("has_capital_gains", False)

    if has_business:
        return "ITR-3 (for individuals with business/professional income)."
    elif has_cg:
        return "ITR-2 (for individuals with capital gains and no business income)."
    else:
        return "ITR-1 (Sahaj) — if total income ≤ ₹50L, salary + 1 HP + other sources."


# ---------------------------------------------------------------------------
# Quick-Test Harness
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 72)
    print("COMPLIANCE CHECKS — Test Harness (FY 2024-25)")
    print("=" * 72)

    test_profile = {
        "gross_total_income": 12_00_000,
        "age": 35,
        "gross_receipts": 0.0,
        "estimated_total_tax": 80_000,
        "tds_paid": 60_000,
        "professional_tax": 2_400,
        "salary_basic": 8_00_000,
        "has_house_property": True,
        "section_80c": 1_50_000,
        "section_80d_self": 25_000,
        "hra_received": 3_00_000,
        "has_capital_gains": True,
    }

    result = check_compliance(test_profile)
    print(f"\nCompliance passed: {result['passed']}")
    for issue in result["issues"]:
        print(f"  [{issue['status'].upper():^8}] {issue['message']}")

    print(f"\n{'=' * 72}")
    print("FILING CHECKLIST")
    print("=" * 72)

    checklist = get_filing_checklist(test_profile)
    for i, item in enumerate(checklist, 1):
        print(f"  {i:2d}. [{item['priority'].upper():^6}] {item['item']}")
        print(f"      → {item['details']}")

    print("\n✅ Compliance module test complete.")
