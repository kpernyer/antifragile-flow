"""
Sample documents for testing document processing workflows.

These documents are embedded in code for repeatability in testing.
Each document includes realistic content for different document types.
"""

from dataclasses import dataclass


@dataclass
class SampleDocument:
    """A sample document for testing."""

    filename: str
    document_type: str
    content: str
    expected_insights: list[str] = None


# Financial Report Sample
FINANCIAL_REPORT = SampleDocument(
    filename="Q3_2024_Financial_Report.txt",
    document_type="financial_report",
    content="""
    EXECUTIVE SUMMARY - Q3 2024 Financial Report
    Company: TechCorp Inc.

    KEY FINANCIAL METRICS:
    - Revenue: $2.5M (up 15% from Q2)
    - Operating Expenses: $1.8M
    - Net Profit: $700K
    - Cash Flow: Positive $500K
    - Employee Count: 45 (up from 40)

    STRATEGIC INITIATIVES:
    1. Launch of new AI product line generating $300K in Q3
    2. Expansion into European markets - 3 new clients signed
    3. Partnership with GlobalTech Solutions worth $400K annually

    OPERATIONAL HIGHLIGHTS:
    - Customer retention rate: 95%
    - New customer acquisition: 12 enterprise clients
    - Product development velocity increased 25%
    - Server uptime: 99.9%

    RISK FACTORS:
    - Increased competition in AI space from 5 new entrants
    - Supply chain uncertainties affecting hardware costs (+8%)
    - Regulatory changes in data privacy (GDPR compliance costs $50K)
    - Key talent retention in competitive market

    FORWARD-LOOKING STATEMENTS:
    - Q4 revenue projection: $2.8M
    - European expansion expected to add $500K ARR
    - New AI features launching in Q1 2025

    RECOMMENDATIONS:
    - Accelerate product development (hire 2 engineers)
    - Increase marketing spend by 20% to $200K/month
    - Establish European office by Q1 2025
    - Implement advanced customer success programs

    NEXT STEPS:
    - Board review scheduled for November 15, 2024
    - Investor presentation on November 30, 2024
    - Strategic planning session in December 2024
    - Q4 budget finalization by October 31, 2024
    """,
    expected_insights=[
        "Strong revenue growth of 15%",
        "Successful AI product launch",
        "European expansion opportunity",
        "Competitive pressures in AI market",
    ],
)


# Software Contract Sample
SOFTWARE_CONTRACT = SampleDocument(
    filename="Software_License_Agreement.txt",
    document_type="contract",
    content="""
    SOFTWARE LICENSE AGREEMENT

    This Software License Agreement ("Agreement") is entered into on October 1, 2024
    between TechCorp Inc., a Delaware corporation ("Licensor") and
    Enterprise Client Corp., a California corporation ("Licensee").

    1. LICENSE GRANT
    Subject to the terms and conditions of this Agreement, Licensor hereby grants
    to Licensee a non-exclusive, non-transferable license to use the Software
    product "AI Analytics Platform" for internal business purposes only.

    2. TERM AND TERMINATION
    This Agreement shall commence on January 1, 2025 and shall continue for a
    period of three (3) years, automatically renewing for additional one-year
    terms unless either party provides 90 days written notice of non-renewal.

    3. FEES AND PAYMENT
    Licensee shall pay Licensor an annual license fee of $50,000, payable in
    advance on January 1 of each year. Late payments incur 1.5% monthly interest.
    Additional users beyond 100 seats cost $500 per user annually.

    4. SUPPORT AND MAINTENANCE
    Licensor will provide:
    - Technical support during business hours (9 AM - 5 PM Pacific, Monday-Friday)
    - Software updates and bug fixes at no additional cost
    - 99.5% uptime SLA with credits for downtime
    - Dedicated customer success manager

    5. DATA AND SECURITY
    - All customer data remains property of Licensee
    - SOC 2 Type II certification maintained by Licensor
    - Data encryption in transit and at rest (AES-256)
    - Annual security audits with reports provided to Licensee

    6. LIABILITY AND WARRANTIES
    - Software provided "as-is" with 30-day warranty period
    - Liability cap of $100,000 per incident, $500,000 annually
    - Licensee responsible for data backup and recovery

    7. TERMINATION CONDITIONS
    Either party may terminate this Agreement:
    - For convenience with 90 days written notice
    - For material breach with 30 days cure period
    - Immediately for insolvency or bankruptcy

    8. INTELLECTUAL PROPERTY
    - All software IP remains with Licensor
    - Licensee retains rights to their data and configurations
    - No reverse engineering or redistribution permitted

    GOVERNING LAW: Delaware
    DISPUTE RESOLUTION: Binding arbitration

    Signatures:
    TechCorp Inc. - Sarah Johnson, CEO - October 1, 2024
    Enterprise Client Corp. - Michael Chen, CTO - October 1, 2024
    """,
    expected_insights=[
        "3-year term with auto-renewal",
        "$50K annual license fee",
        "99.5% uptime SLA commitment",
        "90-day termination notice required",
    ],
)


# Meeting Notes Sample
MEETING_NOTES = SampleDocument(
    filename="Strategic_Planning_Meeting_Notes.txt",
    document_type="meeting_notes",
    content="""
    STRATEGIC PLANNING MEETING - Q4 2024 PLANNING
    Date: September 25, 2024
    Time: 2:00 PM - 4:00 PM Pacific
    Location: Conference Room A / Zoom Hybrid

    ATTENDEES:
    - Sarah Johnson (CEO) - Present
    - Michael Torres (CTO) - Present
    - Lisa Wang (VP Sales) - Present
    - David Kim (VP Marketing) - Remote
    - Jennifer Adams (CFO) - Present
    - Alex Rodriguez (VP Engineering) - Present

    AGENDA ITEMS DISCUSSED:

    1. Q3 PERFORMANCE REVIEW
    - Revenue target exceeded by 8% ($2.5M vs $2.3M target)
    - AI product launch successful with 15 enterprise clients
    - European pilot program showing promising results
    - Engineering velocity up 25% with new development processes

    2. Q4 2024 OBJECTIVES
    - Revenue target: $2.8M (12% growth from Q3)
    - Launch advanced AI features by December 15
    - Sign 20 new enterprise clients
    - Complete European market research and regulatory compliance
    - Implement customer success automation platform

    3. 2025 STRATEGIC INITIATIVES
    Priority 1: European Market Entry
    - Timeline: Q1 2025 office establishment
    - Budget: $500K for office setup and local hiring
    - Regulatory: GDPR compliance completed, other EU regulations pending
    - Team: Hire European sales director by December 1

    Priority 2: Product Platform Evolution
    - Migrate to cloud-native architecture by Q2 2025
    - Add real-time analytics capabilities
    - Develop mobile application for executives
    - Budget: $300K additional engineering investment

    Priority 3: Partnership Strategy
    - Formalize GlobalTech partnership terms
    - Explore integration with CRM platforms (Salesforce, HubSpot)
    - Evaluate acquisition targets in data visualization space

    4. RESOURCE ALLOCATION
    Engineering: Hire 3 engineers (2 backend, 1 frontend) by January
    Sales: Add 2 enterprise sales reps for European expansion
    Marketing: Increase digital marketing budget 30% for Q1 2025
    Operations: Implement customer success platform by Q4

    5. RISK MITIGATION
    - Competitive Response: Accelerate feature development timeline
    - Talent Retention: Implement equity refresh program
    - Economic Uncertainty: Develop conservative revenue scenarios
    - Technical Debt: Allocate 20% engineering time to infrastructure

    ACTION ITEMS:
    - [Alex] Finalize Q4 engineering roadmap by October 5
    - [Lisa] Present European sales strategy by October 10
    - [David] Launch Q4 marketing campaigns by October 15
    - [Jennifer] Complete 2025 budget scenarios by October 20
    - [Sarah] Schedule board presentation for November 15

    DECISIONS MADE:
    1. Approved $500K European expansion budget
    2. Authorized 5 new hires for Q4/Q1
    3. Committed to Q4 revenue target of $2.8M
    4. Selected December 15 for advanced AI feature launch

    NEXT MEETING: October 9, 2024 at 2:00 PM - Q4 Progress Review
    """,
    expected_insights=[
        "European expansion approved for Q1 2025",
        "5 new hires authorized",
        "Q4 revenue target of $2.8M",
        "Advanced AI features launching December 15",
    ],
)


# Collection of all sample documents
ALL_SAMPLE_DOCUMENTS = [FINANCIAL_REPORT, SOFTWARE_CONTRACT, MEETING_NOTES]


def get_document_by_type(doc_type: str) -> SampleDocument:
    """Get a sample document by type."""
    for doc in ALL_SAMPLE_DOCUMENTS:
        if doc.document_type == doc_type:
            return doc
    raise ValueError(f"No sample document found for type: {doc_type}")


def get_document_by_filename(filename: str) -> SampleDocument:
    """Get a sample document by filename."""
    for doc in ALL_SAMPLE_DOCUMENTS:
        if doc.filename == filename:
            return doc
    raise ValueError(f"No sample document found with filename: {filename}")
