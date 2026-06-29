"""
Capital Gains Tax Calculator — Sections 45–55, 111A, 112, 112A of the
Income Tax Act, 1961.

Implements deterministic computation of capital gains tax for
FY 2024-25 (AY 2025-26), incorporating **post-Budget 2024 amendments**
(Finance (No. 2) Act, 2024, effective 23-Jul-2024).

Key Budget 2024 changes:
    - STCG u/s 111A (listed equity / equity MFs, STT paid): **20 %**
      (previously 15 %)
    - LTCG u/s 112A (listed equity / equity MFs): **12.5 %** on gains
      exceeding **₹1,25,000** (previously 10 % on gains > ₹1,00,000)
    - LTCG u/s 112 (unlisted shares, real estate, gold, etc.):
      **12.5 %** flat **without indexation** (previously 20 % with CII)
    - Indexation benefit REMOVED for all post-23-Jul-2024 transfers
    - Holding period: listed equity 12 months, unlisted assets 24 months

Exemptions modelled:
    - Section 54   : Reinvestment in residential house (LTCG on property)
    - Section 54EC : Investment in specified bonds (cap ₹50 L, 5-year lock-in)
    - Section 54F  : Reinvestment of net consideration (non-house assets)

Every function returns a dict containing at minimum:
    - amount            : computed tax / gain / exemption (float, INR)
    - section_reference : statutory citation (str)
    - explanation       : human-readable narrative (str)

References:
    - Income Tax Act, 1961 — Sections 45–55, 111A, 112, 112A
    - Finance (No. 2) Act, 2024
    - Sections 54, 54EC, 54F
"""

from __future__ import annotations

from typing import Any

from .models import CapitalGains


# ---------------------------------------------------------------------------
# Constants — FY 2024-25 (post-Budget 2024)
# ---------------------------------------------------------------------------

STCG_111A_RATE: float = 0.20
"""STCG u/s 111A on listed equity / equity-oriented MFs: 20 %."""

LTCG_112A_RATE: float = 0.125
"""LTCG u/s 112A on listed equity / equity-oriented MFs: 12.5 %."""

LTCG_112A_EXEMPTION: float = 125_000.0
"""LTCG u/s 112A annual exemption threshold: ₹1,25,000 (raised from
   ₹1,00,000 by Budget 2024)."""

LTCG_112_RATE: float = 0.125
"""LTCG u/s 112 on other capital assets: 12.5 % (without indexation,
   indexation removed by Budget 2024)."""

CAP_54EC_INVESTMENT: float = 5_000_000.0
"""Section 54EC: Maximum investment in specified bonds: ₹50,00,000."""

SECTION_54EC_LOCK_IN: int = 5
"""Section 54EC bonds must be held for 5 years."""


# ---------------------------------------------------------------------------
# Input Validation
# ---------------------------------------------------------------------------

def _validate_and_parse(cg_dict: dict[str, Any]) -> CapitalGains:
    """Parse and validate the raw capital-gains dict through Pydantic.

    Maps the user-facing field names to the ``CapitalGains`` model.
    Unknown keys are silently ignored (Pydantic default).

    Args:
        cg_dict: Raw input dict with capital-gains data.

    Returns:
        Validated ``CapitalGains`` model instance.
    """
    # Map aliases so callers can use either ltcg_equity or ltcg_112a etc.
    mapped = {
        "stcg_equity": cg_dict.get("stcg_equity", cg_dict.get("stcg_111a", 0.0)),
        "stcg_other": cg_dict.get("stcg_other", 0.0),
        "ltcg_equity": cg_dict.get("ltcg_equity", cg_dict.get("ltcg_112a", 0.0)),
        "ltcg_other": cg_dict.get("ltcg_other", cg_dict.get("ltcg_112", 0.0)),
        "ltcg_exemption_54": cg_dict.get("ltcg_exemption_54", 0.0),
        "ltcg_exemption_54ec": cg_dict.get("ltcg_exemption_54ec", 0.0),
        "ltcg_exemption_54f": cg_dict.get("ltcg_exemption_54f", 0.0),
    }
    return CapitalGains(**mapped)


# ---------------------------------------------------------------------------
# Exemption Validators
# ---------------------------------------------------------------------------

def _validate_exemptions(cg: CapitalGains) -> dict[str, Any]:
    """Validate and cap exemption amounts against available LTCG.

    Rules:
        - Section 54 : Claimed against LTCG on property sale (ltcg_other).
        - Section 54EC: Investment in bonds, capped at ₹50 L and remaining
                        LTCG after Section 54.
        - Section 54F : Reinvestment of net consideration, applied to
                        remaining LTCG.
        - Total exemptions cannot exceed total LTCG (other).

    Args:
        cg: Validated ``CapitalGains`` instance.

    Returns:
        dict with validated exemption amounts and explanations.
    """
    total_ltcg_other = cg.ltcg_other
    remaining = max(0.0, total_ltcg_other)
    exemptions_applied: dict[str, dict[str, Any]] = {}

    # --- Section 54 ---
    ex_54 = min(cg.ltcg_exemption_54, remaining)
    if cg.ltcg_exemption_54 > 0:
        exemptions_applied["section_54"] = {
            "claimed": cg.ltcg_exemption_54,
            "allowed": round(ex_54, 2),
            "amount": round(ex_54, 2),
            "section_reference": "Section 54",
            "explanation": (
                f"Exemption u/s 54 claimed: ₹{cg.ltcg_exemption_54:,.0f}, "
                f"allowed: ₹{ex_54:,.0f} (capped at available LTCG other "
                f"₹{remaining:,.0f})."
            ),
        }
        remaining -= ex_54

    # --- Section 54EC ---
    capped_54ec = min(cg.ltcg_exemption_54ec, CAP_54EC_INVESTMENT)
    ex_54ec = min(capped_54ec, remaining)
    if cg.ltcg_exemption_54ec > 0:
        exemptions_applied["section_54ec"] = {
            "claimed": cg.ltcg_exemption_54ec,
            "capped_at_50l": round(capped_54ec, 2),
            "allowed": round(ex_54ec, 2),
            "amount": round(ex_54ec, 2),
            "lock_in_years": SECTION_54EC_LOCK_IN,
            "section_reference": "Section 54EC",
            "explanation": (
                f"Exemption u/s 54EC claimed: ₹{cg.ltcg_exemption_54ec:,.0f}, "
                f"capped at ₹{CAP_54EC_INVESTMENT:,.0f}, "
                f"allowed: ₹{ex_54ec:,.0f} (remaining LTCG ₹{remaining:,.0f}). "
                f"Lock-in: {SECTION_54EC_LOCK_IN} years."
            ),
        }
        remaining -= ex_54ec

    # --- Section 54F ---
    ex_54f = min(cg.ltcg_exemption_54f, remaining)
    if cg.ltcg_exemption_54f > 0:
        exemptions_applied["section_54f"] = {
            "claimed": cg.ltcg_exemption_54f,
            "allowed": round(ex_54f, 2),
            "amount": round(ex_54f, 2),
            "section_reference": "Section 54F",
            "explanation": (
                f"Exemption u/s 54F claimed: ₹{cg.ltcg_exemption_54f:,.0f}, "
                f"allowed: ₹{ex_54f:,.0f} (remaining LTCG ₹{remaining:,.0f})."
            ),
        }
        remaining -= ex_54f

    total_exemptions = round(ex_54 + ex_54ec + ex_54f, 2)

    return {
        "exemptions_applied": exemptions_applied,
        "total_exemptions": total_exemptions,
        "ltcg_other_after_exemptions": round(
            max(0.0, total_ltcg_other - total_exemptions), 2,
        ),
    }


# ---------------------------------------------------------------------------
# Tax Computation — STCG
# ---------------------------------------------------------------------------

def _compute_stcg_111a(gain: float) -> dict[str, Any]:
    """STCG on listed equity / equity-oriented MFs under Section 111A.

    Rate: 20 % (flat, post-Budget 2024).
    Applicable where STT is paid on both acquisition and transfer.

    Args:
        gain: Short-term capital gain under Section 111A.

    Returns:
        dict with tax breakdown.
    """
    taxable = max(0.0, gain)
    tax = round(taxable * STCG_111A_RATE, 2)

    return {
        "gain": gain,
        "taxable": taxable,
        "rate": STCG_111A_RATE,
        "tax": tax,
        "amount": tax,
        "section_reference": "Section 111A",
        "explanation": (
            f"STCG u/s 111A: ₹{gain:,.0f}. "
            f"Tax @ {STCG_111A_RATE:.0%} = ₹{tax:,.0f}. "
            f"(Listed equity where STT paid, post-Budget 2024 rate.)"
        ),
    }


def _compute_stcg_slab(gain: float) -> dict[str, Any]:
    """STCG on non-equity assets — taxed at normal slab rates.

    The actual slab computation depends on the assessee's total income
    and is handled by the slab calculator.  This function just returns
    the taxable amount so it can be included in GTI for slab computation.

    Args:
        gain: Short-term capital gain (non-111A).

    Returns:
        dict with the slab-taxable amount (NO tax calculated here).
    """
    taxable = max(0.0, gain)

    return {
        "gain": gain,
        "taxable": taxable,
        "slab_amount": taxable,
        "tax": 0.0,  # to be computed via slab calculator
        "amount": 0.0,
        "section_reference": "Section 45 (slab rates)",
        "explanation": (
            f"STCG (other): ₹{gain:,.0f}. "
            f"Added to total income for slab-rate taxation — "
            f"actual tax will be computed by the slab calculator."
        ),
    }


# ---------------------------------------------------------------------------
# Tax Computation — LTCG
# ---------------------------------------------------------------------------

def _compute_ltcg_112a(gain: float) -> dict[str, Any]:
    """LTCG on listed equity / equity-oriented MFs under Section 112A.

    Post-Budget 2024:
        - Rate    : 12.5 %
        - Exempt  : ₹1,25,000 per year (aggregate across all 112A gains)
        - No indexation benefit

    Args:
        gain: Long-term capital gain under Section 112A (aggregate).

    Returns:
        dict with tax breakdown.
    """
    taxable = max(0.0, gain - LTCG_112A_EXEMPTION)
    tax = round(taxable * LTCG_112A_RATE, 2)

    return {
        "gain": gain,
        "exemption_threshold": LTCG_112A_EXEMPTION,
        "taxable": taxable,
        "rate": LTCG_112A_RATE,
        "tax": tax,
        "amount": tax,
        "section_reference": "Section 112A",
        "explanation": (
            f"LTCG u/s 112A: ₹{gain:,.0f}. "
            f"Exemption threshold: ₹{LTCG_112A_EXEMPTION:,.0f}. "
            f"Taxable: ₹{taxable:,.0f}. "
            f"Tax @ {LTCG_112A_RATE:.1%} = ₹{tax:,.0f}. "
            f"(Post-Budget 2024: 12.5 %, no indexation.)"
        ),
    }


def _compute_ltcg_112(gain: float) -> dict[str, Any]:
    """LTCG on other assets under Section 112 (post-Budget 2024).

    Post-Budget 2024:
        - Rate: 12.5 % WITHOUT indexation
        - Applies to unlisted shares, real estate, gold, debt MFs, etc.

    Args:
        gain: Long-term capital gain under Section 112 (after exemptions).

    Returns:
        dict with tax breakdown.
    """
    taxable = max(0.0, gain)
    tax = round(taxable * LTCG_112_RATE, 2)

    return {
        "gain": gain,
        "taxable": taxable,
        "rate": LTCG_112_RATE,
        "tax": tax,
        "amount": tax,
        "section_reference": "Section 112",
        "explanation": (
            f"LTCG u/s 112 (other assets): ₹{gain:,.0f}. "
            f"Tax @ {LTCG_112_RATE:.1%} = ₹{tax:,.0f}. "
            f"(Post-Budget 2024: 12.5 % without indexation.)"
        ),
    }


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def calculate_capital_gains_tax(
    capital_gains: dict[str, Any],
) -> dict[str, Any]:
    """Calculate total capital gains tax across all categories for FY 2024-25.

    This is the primary orchestrator function.  It accepts a dict describing
    gains and exemptions, validates through the ``CapitalGains`` Pydantic
    model, applies exemptions (Sections 54/54EC/54F), and computes tax
    under the applicable special-rate sections.

    Input dict keys (all optional, default 0.0):
        Gains:
            stcg_equity  (or stcg_111a) : STCG on listed equity (Sec 111A)
            stcg_other                  : STCG on other assets (slab rates)
            ltcg_equity  (or ltcg_112a) : LTCG on listed equity (Sec 112A)
            ltcg_other   (or ltcg_112)  : LTCG on other assets (Sec 112)

        Exemptions:
            ltcg_exemption_54           : Amount reinvested u/s 54
            ltcg_exemption_54ec         : Amount invested in bonds u/s 54EC
            ltcg_exemption_54f          : Amount reinvested u/s 54F

    Args:
        capital_gains: Dict with capital gains and exemption data.

    Returns:
        dict with keys:
            - stcg_111a_tax        : tax on listed equity STCG
            - stcg_slab_amount     : STCG (other) to be taxed at slab rates
            - ltcg_112a_tax        : tax on listed equity LTCG
            - ltcg_112_tax         : tax on other LTCG (after exemptions)
            - total_cg_tax         : sum of special-rate CG taxes
            - exemptions_applied   : dict of validated exemption details
            - amount               : same as total_cg_tax (top-level amount)
            - section_reference    : statutory citations
            - explanation          : narrative summary
    """
    # Validate via Pydantic
    cg = _validate_and_parse(capital_gains)

    # --- Process exemptions on LTCG (other / Section 112) ---
    exemption_result = _validate_exemptions(cg)
    ltcg_other_net = exemption_result["ltcg_other_after_exemptions"]

    # --- Compute individual taxes ---
    stcg_111a_result = _compute_stcg_111a(cg.stcg_equity)
    stcg_slab_result = _compute_stcg_slab(cg.stcg_other)
    ltcg_112a_result = _compute_ltcg_112a(cg.ltcg_equity)
    ltcg_112_result = _compute_ltcg_112(ltcg_other_net)

    # --- Aggregate special-rate tax (excludes STCG other — that's slab) ---
    total_cg_tax = round(
        stcg_111a_result["tax"]
        + ltcg_112a_result["tax"]
        + ltcg_112_result["tax"],
        2,
    )

    # Collect section references
    section_refs = [
        "Section 111A", "Section 112A", "Section 112",
        "Section 45",
    ]
    if exemption_result["exemptions_applied"]:
        for ex_detail in exemption_result["exemptions_applied"].values():
            ref = ex_detail["section_reference"]
            if ref not in section_refs:
                section_refs.append(ref)

    total_gains = round(
        cg.stcg_equity + cg.stcg_other + cg.ltcg_equity + cg.ltcg_other, 2,
    )

    return {
        "amount": total_cg_tax,
        "stcg_111a_tax": stcg_111a_result["tax"],
        "stcg_slab_amount": stcg_slab_result["slab_amount"],
        "ltcg_112a_tax": ltcg_112a_result["tax"],
        "ltcg_112_tax": ltcg_112_result["tax"],
        "total_cg_tax": total_cg_tax,
        "total_gains": total_gains,
        "total_exemptions": exemption_result["total_exemptions"],
        "exemptions_applied": exemption_result["exemptions_applied"],
        "breakdown": {
            "stcg_111a": stcg_111a_result,
            "stcg_other": stcg_slab_result,
            "ltcg_112a": ltcg_112a_result,
            "ltcg_112": ltcg_112_result,
        },
        "section_reference": ", ".join(section_refs),
        "explanation": (
            f"Total capital gains: ₹{total_gains:,.0f}. "
            f"Exemptions (54/54EC/54F): ₹{exemption_result['total_exemptions']:,.0f}. "
            f"STCG 111A tax: ₹{stcg_111a_result['tax']:,.0f}, "
            f"STCG other (slab): ₹{stcg_slab_result['slab_amount']:,.0f} "
            f"(to be taxed via slab calculator). "
            f"LTCG 112A tax: ₹{ltcg_112a_result['tax']:,.0f}, "
            f"LTCG 112 tax: ₹{ltcg_112_result['tax']:,.0f}. "
            f"Total CG tax (special rates): ₹{total_cg_tax:,.0f}."
        ),
    }


# ---------------------------------------------------------------------------
# Quick-Test Harness
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 76)
    print("CAPITAL GAINS TAX CALCULATOR — Test Cases (FY 2024-25)")
    print("=" * 76)

    # -----------------------------------------------------------------------
    # Test 1: STCG 111A only
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({"stcg_equity": 200_000})
    assert r["stcg_111a_tax"] == 40_000.0  # 20 % of 2L
    assert r["total_cg_tax"] == 40_000.0
    print(f"[PASS] Test 1 — STCG 111A:            tax ₹{r['stcg_111a_tax']:,.0f}")

    # -----------------------------------------------------------------------
    # Test 2: STCG other — returned as slab amount, no tax computed
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({"stcg_other": 300_000})
    assert r["stcg_slab_amount"] == 300_000.0
    assert r["total_cg_tax"] == 0.0  # slab tax computed elsewhere
    print(f"[PASS] Test 2 — STCG other (slab):    slab amount ₹{r['stcg_slab_amount']:,.0f}")

    # -----------------------------------------------------------------------
    # Test 3: LTCG 112A within exemption threshold
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({"ltcg_equity": 100_000})
    assert r["ltcg_112a_tax"] == 0.0  # under ₹1.25L
    print(f"[PASS] Test 3 — LTCG 112A (< ₹1.25L): tax ₹{r['ltcg_112a_tax']:,.0f}")

    # -----------------------------------------------------------------------
    # Test 4: LTCG 112A above exemption threshold
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({"ltcg_equity": 325_000})
    # Taxable = 325K - 125K = 200K; Tax = 200K × 12.5% = 25K
    assert r["ltcg_112a_tax"] == 25_000.0
    print(f"[PASS] Test 4 — LTCG 112A (> ₹1.25L): tax ₹{r['ltcg_112a_tax']:,.0f}")

    # -----------------------------------------------------------------------
    # Test 5: LTCG 112 (other assets, no indexation)
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({"ltcg_other": 500_000})
    assert r["ltcg_112_tax"] == 62_500.0  # 12.5 % of 5L
    print(f"[PASS] Test 5 — LTCG 112:             tax ₹{r['ltcg_112_tax']:,.0f}")

    # -----------------------------------------------------------------------
    # Test 6: Section 54 exemption
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({
        "ltcg_other": 1_000_000,
        "ltcg_exemption_54": 600_000,
    })
    # Net LTCG = 10L - 6L = 4L; Tax = 4L × 12.5% = 50K
    assert r["ltcg_112_tax"] == 50_000.0
    assert r["exemptions_applied"]["section_54"]["allowed"] == 600_000.0
    print(f"[PASS] Test 6 — Section 54 exemption:  tax ₹{r['ltcg_112_tax']:,.0f}")

    # -----------------------------------------------------------------------
    # Test 7: Section 54EC exemption (capped at ₹50L)
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({
        "ltcg_other": 8_000_000,
        "ltcg_exemption_54ec": 6_000_000,  # > 50L cap
    })
    # Capped at 50L; Net = 80L - 50L = 30L; Tax = 30L × 12.5% = 3.75L
    assert r["exemptions_applied"]["section_54ec"]["allowed"] == 5_000_000.0
    assert r["ltcg_112_tax"] == 375_000.0
    print(f"[PASS] Test 7 — Section 54EC (capped): tax ₹{r['ltcg_112_tax']:,.0f}")

    # -----------------------------------------------------------------------
    # Test 8: Exemption exceeds LTCG (capped at LTCG)
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({
        "ltcg_other": 200_000,
        "ltcg_exemption_54": 500_000,  # more than LTCG
    })
    assert r["exemptions_applied"]["section_54"]["allowed"] == 200_000.0
    assert r["ltcg_112_tax"] == 0.0
    print(f"[PASS] Test 8 — Exemption > LTCG:     capped at LTCG, tax ₹0")

    # -----------------------------------------------------------------------
    # Test 9: Multiple exemptions
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({
        "ltcg_other": 2_000_000,
        "ltcg_exemption_54": 800_000,
        "ltcg_exemption_54ec": 500_000,
        "ltcg_exemption_54f": 300_000,
    })
    # 54: 8L, 54EC: 5L, 54F: 3L → total exempt 16L, net = 20L - 16L = 4L
    assert r["total_exemptions"] == 1_600_000.0
    # Tax = 4L × 12.5% = 50K
    assert r["ltcg_112_tax"] == 50_000.0
    print(f"[PASS] Test 9 — Multiple exemptions:   tax ₹{r['ltcg_112_tax']:,.0f}")

    # -----------------------------------------------------------------------
    # Test 10: Composite — all CG types + exemptions
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({
        "stcg_equity": 100_000,
        "stcg_other": 50_000,
        "ltcg_equity": 225_000,
        "ltcg_other": 500_000,
        "ltcg_exemption_54ec": 200_000,
    })
    # STCG 111A: 100K × 20% = 20K
    # STCG other: 50K (slab — not in total_cg_tax)
    # LTCG 112A: (225K - 125K) × 12.5% = 12.5K
    # LTCG 112: (500K - 200K) × 12.5% = 37.5K
    # Total CG tax = 20K + 12.5K + 37.5K = 70K
    assert r["stcg_111a_tax"] == 20_000.0
    assert r["stcg_slab_amount"] == 50_000.0
    assert r["ltcg_112a_tax"] == 12_500.0
    assert r["ltcg_112_tax"] == 37_500.0
    assert r["total_cg_tax"] == 70_000.0
    print(f"[PASS] Test 10 — Composite CG:        total tax ₹{r['total_cg_tax']:,.0f}")
    for section, detail in r["breakdown"].items():
        print(f"       {section:12s} → tax ₹{detail['tax']:>10,.0f}")
    if r["exemptions_applied"]:
        for section, detail in r["exemptions_applied"].items():
            print(f"       {section:12s} → exempt ₹{detail['allowed']:>10,.0f}")

    # -----------------------------------------------------------------------
    # Test 11: Zero gains
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({})
    assert r["total_cg_tax"] == 0.0
    assert r["total_gains"] == 0.0
    print(f"[PASS] Test 11 — No gains:            total tax ₹{r['total_cg_tax']:,.0f}")

    # -----------------------------------------------------------------------
    # Test 12: LTCG equity exactly at exemption threshold
    # -----------------------------------------------------------------------
    r = calculate_capital_gains_tax({"ltcg_equity": 125_000})
    assert r["ltcg_112a_tax"] == 0.0
    print(f"[PASS] Test 12 — LTCG 112A (= ₹1.25L): tax ₹0 (fully exempt)")

    print("\n✅ All capital gains tests passed.")
