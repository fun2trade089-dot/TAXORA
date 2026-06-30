"""
AI Chatbot Agent — Virtual Chartered Accountant (CA) co-pilot.

This module implements the ``VirtualCAAgent`` class which orchestrates:
    1. Query analysis and keyword extraction.
    2. Legal knowledge base search (from ``core.legal_db``).
    3. Profile calculations and optimizations (from ``core.optimizer``).
    4. AI Reasoning (via LangChain Google GenerativeAI) or a high-fidelity local fallback.

Cites exact sections of the Income Tax Act, 1961.
"""

from __future__ import annotations

import os
import re
from typing import Any, Optional
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from .legal_db import search_sections
from .optimizer import generate_optimization_report, TaxpayerProfile

# Load environment variables (e.g. from .env in the root directory)
load_dotenv()


class VirtualCAAgent:
    """AI Agent acting as a virtual Chartered Accountant (CA) co-pilot."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """Initialize the agent.

        Loads GEMINI_API_KEY from environment variables and sets up the LLM.
        """
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = model_name
        self.llm = None

        if self.api_key:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=0.2,
                )
            except Exception as e:
                print(f"Warning: Failed to initialize ChatGoogleGenerativeAI: {e}")

    def _extract_keywords(self, query: str) -> list[str]:
        """Extract tax-relevant keywords from a user query to search the database."""
        words = re.findall(r"\b\w+\b", query.lower())
        tax_keywords = {
            "80c", "80ccc", "80ccd", "80d", "80e", "80g", "80gg", "80tta", "80ttb", "80u", "87a",
            "hra", "rent", "housing", "loan", "interest", "salary", "standard deduction", "standard",
            "capital", "gains", "stcg", "ltcg", "equity", "stocks", "mutual", "fund", "house",
            "property", "business", "presumptive", "depreciation", "audit", "advance tax", "115bac",
            "regime", "slab", "slabs", "late", "fee", "penalty"
        }
        return list(set(words) & tax_keywords)

    def get_context_for_query(self, query: str) -> str:
        """Search the legal database for matching tax provisions."""
        keywords = self._extract_keywords(query)
        matched_sections = []

        for kw in keywords:
            matched_sections.extend(search_sections(kw))

        # De-duplicate sections
        unique_sections = {}
        for s in matched_sections:
            unique_sections[s["section"]] = s

        # If no keywords matched, fall back to matching words directly
        if not unique_sections:
            for word in query.lower().split():
                if len(word) > 2:
                    for s in search_sections(word):
                        unique_sections[s["section"]] = s

        # Format matches as readable text
        context_parts = []
        for _, sec_meta in unique_sections.items():
            investments = (
                f"\n  Eligible investments: {', '.join(sec_meta['eligible_investments'])}"
                if sec_meta.get("eligible_investments")
                else ""
            )
            notes = f"\n  Notes: {sec_meta['notes']}" if sec_meta.get("notes") else ""
            context_parts.append(
                f"- {sec_meta['section']} ({sec_meta['act']}): {sec_meta['title']}\n"
                f"  Limit: {sec_meta.get('max_limit') or 'No specific limit'}\n"
                f"  Regime availability: {'Both' if sec_meta.get('available_in_new_regime') else 'Old Regime only'}"
                f"{investments}{notes}"
            )

        if not context_parts:
            return "No matching specific legal sections found in database."
        return "\n\n".join(context_parts)

    def query(self, user_query: str, profile_dict: Optional[dict[str, Any]] = None) -> str:
        """Query the CA advisor chatbot.

        Args:
            user_query: The natural language question from the user.
            profile_dict: Optional taxpayer profile details. If provided,
                          runs computations and regime optimization.
        """
        # 1. Search legal references
        legal_context = self.get_context_for_query(user_query)

        # 2. Run optimization report if profile exists
        opt_report_str = ""
        if profile_dict:
            try:
                profile = TaxpayerProfile(**profile_dict)
                report = generate_optimization_report(profile)

                opt_report_str = (
                    f"Taxpayer Gross Total Income: INR {report['gross_total_income']['gross_total_income']:,.2f}\n"
                    f"Recommended Regime: {report['summary']['recommended_regime']}\n"
                    f"Recommended Tax: INR {report['summary']['tax_under_recommended_regime']:,.2f}\n"
                    f"Savings by choosing recommended regime: INR {report['summary']['regime_savings']:,.2f}\n"
                    f"Compliance Passed: {report['compliance']['passed']}\n"
                    f"Compliance Issues Flagged: {len(report['compliance']['issues'])}\n"
                )

                if report.get("deduction_gaps"):
                    opt_report_str += "Deduction Gaps:\n"
                    for gap in report["deduction_gaps"]:
                        opt_report_str += (
                            f"  - Section {gap['section']}: Current Claim: INR {gap['current_claim']:.0f}, "
                            f"Limit: INR {gap['limit']:.0f}, Gap: INR {gap['gap']:.0f}, "
                            f"Potential Savings: INR {gap['potential_tax_savings']:.0f}\n"
                        )

                if report["compliance"]["issues"]:
                    opt_report_str += "Compliance Issues Details:\n"
                    for issue in report["compliance"]["issues"]:
                        opt_report_str += f"  - [{issue['status'].upper()}] Section {issue.get('section_reference', 'N/A')}: {issue['message']}\n"
            except Exception as e:
                import traceback
                traceback.print_exc()
                opt_report_str = f"Error generating tax optimization report: {e}\n"

        # 3. Build Prompt
        system_prompt = (
            "You are an expert virtual Chartered Accountant (CA) co-pilot. Your tone is professional, legally precise, and compliant.\n"
            "Your goal is to help the taxpayer legally minimize their tax liability based on the provided tax laws and computation results.\n\n"
            "Rules you must follow:\n"
            "1. Strictly use standard tax terminology (e.g., Assessment Year, Financial Year, Heads of Income, Exemptions under Section 10, Deductions under Chapter VI-A).\n"
            "2. Format your response as a structured 'CA Advisory Memo' with the following sections:\n"
            "   - **Executive Summary**: Clear bottom-line advice and net savings.\n"
            "   - **Computation details / Regime Comparison** (if numeric details are present): Compare Old vs New regimes in a clean markdown table.\n"
            "   - **Tax Planning Recommendations**: Clear actionable steps to save tax, referencing the exact Sections (e.g., Section 80C, Section 10(13A)).\n"
            "   - **Compliance & Filing Notes**: Flags for deadlines, advance tax, audit thresholds, or missing proofs.\n"
            "3. Cite the exact statutory references (Act, Section, Rules) for every tax exemption or deduction recommended. Only reference sections present in the context below.\n"
            "4. If the query cannot be fully resolved with the provided database, state that professional consultation is required. Do NOT hallucinate limits or sections.\n"
            "5. If no API key is available, you will run in a mock advisory mode."
        )

        user_message_content = (
            f"User Query:\n{user_query}\n\n"
            f"Retrieved Legal References:\n{legal_context}\n\n"
        )
        if opt_report_str:
            user_message_content += f"Tax Computation & Optimization Report:\n{opt_report_str}\n"

        # 4. Run LLM or fall back to local mock
        if self.llm:
            try:
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_message_content),
                ]
                response = self.llm.invoke(messages)
                return response.content
            except Exception as e:
                return self._generate_fallback_response(
                    user_query, legal_context, opt_report_str, error=str(e)
                )
        else:
            return self._generate_fallback_response(user_query, legal_context, opt_report_str)

    def _generate_fallback_response(
        self, query: str, context: str, report_str: str, error: Optional[str] = None
    ) -> str:
        err_msg = (
            f"\n*(Note: Running in local-first mock mode. LLM error: {error})*\n"
            if error
            else "\n*(Note: Running in local-first mock mode. Set GEMINI_API_KEY in .env for full AI advisory)*\n"
        )

        response = (
            f"# CHARTERED ACCOUNTANT ADVISORY MEMO\n"
            f"{err_msg}\n"
            f"**To:** Taxpayer / Client  \n"
            f"**From:** AI CA Co-Pilot  \n"
            f"**Date:** June 29, 2026  \n"
            f"**Subject:** Tax Minimization Advisory  \n\n"
            f"## Executive Summary\n"
            f"We have analyzed your query: *\"{query}\"* against the provisions of the Income Tax Act, 1961.\n"
        )

        if report_str:
            lines = report_str.split("\n")
            recommended = "NEW" if "NEW" in report_str else "OLD"
            savings = "0.00"
            for line in lines:
                if "Savings by choosing" in line:
                    savings = line.split(":")[-1].strip()
                    break

            response += (
                f"Based on your profile, the **{recommended} Tax Regime** is recommended. "
                f"By filing under the {recommended} regime, you will save **{savings}** compared to the alternative.\n\n"
                f"## Computation & Regime Comparison\n"
                f"| Head / Component | Old Regime | New Regime |\n"
                f"| :--- | :--- | :--- |\n"
                f"| Gross Total Income | Assessed | Assessed |\n"
                f"| Taxable Income | Capped Deductions | Standard Allowances |\n"
                f"| **Net Tax Liability** | **Higher** | **Lower (Recommended)** |\n\n"
            )
        else:
            response += (
                "Based on the statutory limits, you can minimize tax liability by choosing the correct tax regime "
                "and fully utilizing Chapter VI-A deductions.\n\n"
            )

        response += "## Tax Planning Recommendations\n"
        query_lower = query.lower()

        if any(w in query_lower for w in ["80c", "investment", "saving", "elss", "ppf"]):
            response += (
                "1. **Maximize Section 80C Deduction**:  \n"
                "   - *Statute*: Section 80C of the Income Tax Act, 1961.  \n"
                "   - *Recommendation*: Invest up to ₹1,50,000 in PPF, ELSS, or Tax-Saving FDs. "
                "This deduction is only available under the Old Tax Regime.  \n\n"
            )
        if any(w in query_lower for w in ["rent", "hra", "room"]):
            response += (
                "2. **Claim House Rent Allowance (HRA) Exemption**:  \n"
                "   - *Statute*: Section 10(13A) read with Rule 2A.  \n"
                "   - *Recommendation*: Exemption is the minimum of actual HRA received, rent paid minus 10% "
                "basic salary, or 40%/50% basic salary. Rent receipts must be maintained. Landlord's PAN is "
                "mandatory if annual rent exceeds ₹1,00,000.  \n\n"
            )
        if any(w in query_lower for w in ["nps", "pension", "national pension"]):
            response += (
                "3. **Additional NPS Contribution u/s 80CCD(1B)**:  \n"
                "   - *Statute*: Section 80CCD(1B).  \n"
                "   - *Recommendation*: Invest ₹50,000 in NPS Tier-I. This is over and above the ₹1.5L cap of "
                "Section 80CCE and saves up to ₹15,600 (under 30% slab, Old Regime).  \n\n"
            )
        if any(w in query_lower for w in ["insurance", "medical", "health", "80d"]):
            response += (
                "4. **Health Insurance Premium u/s 80D**:  \n"
                "   - *Statute*: Section 80D.  \n"
                "   - *Recommendation*: Claim up to ₹25,000 for self/spouse/children and up to ₹25,000 "
                "(or ₹50,000 if senior citizen) for parents' health insurance premium.  \n\n"
            )
        if any(w in query_lower for w in ["capital", "gain", "stcg", "ltcg", "sell", "stock", "share", "property"]):
            response += (
                "5. **Capital Gains Tax Optimization**:  \n"
                "   - *Statute*: Section 111A and Section 112A.  \n"
                "   - *Recommendation*: Short-term capital gains on listed equities are taxed at 20% u/s 111A. "
                "Long-term capital gains are taxed at 12.5% u/s 112A, with an annual exemption of ₹1.25L. "
                "Utilize Section 54/54EC/54F exemptions if reinvesting real estate gains.  \n\n"
            )

        response += (
            "## Compliance & Filing Notes\n"
            "- **ITR Filing Deadline**: The standard due date for individual filing is **31st July** of the "
            "Assessment Year. Delay attracts interest u/s 234A and a late fee u/s 234F.  \n"
            "- **Advance Tax u/s 208**: Payable in quarterly installments if net tax liability after TDS "
            "exceeds ₹10,000.  \n"
            "- **AIS/TIS Matching**: Ensure all entries match your Annual Information Statement (AIS) to avoid "
            "automated notices u/s 143(1).\n\n"
            "## Legal References Identified:\n"
            f"{context}\n\n"
            "---  \n"
            "*Disclaimer: This memorandum is generated by an automated expert system for information purposes. "
            "For formal filing or complex tax planning, please review with your Chartered Accountant.*"
        )
        return response


if __name__ == "__main__":
    # Self-test block
    print("Testing VirtualCAAgent...")
    agent = VirtualCAAgent()
    
    # Test keyword context search
    print("\n--- Test context retrieval ---")
    context = agent.get_context_for_query("I want to save tax on my rent and buy medical insurance")
    print(context)
    
    # Test query response in mock mode
    print("\n--- Test query mock advisor response ---")
    res = agent.query("How do I save tax using 80C and HRA?")
    print(res[:500] + "...\n[TRUNCATED]")
