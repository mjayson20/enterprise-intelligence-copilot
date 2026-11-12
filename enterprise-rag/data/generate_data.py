"""
Synthetic data generator for Acme Enterprise demo dataset.
Demo Environment -- Synthetic Enterprise Data
"""
import csv
import random
import os
from datetime import datetime, timedelta

import pandas as pd
from openpyxl import Workbook

random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── shared reference data ───────────────────────────────────────────────────
CUSTOMER_IDS = [f"CUST-{i:03d}" for i in range(1, 21)]

CUSTOMER_NAMES = [
    "Apex Logistics", "Blue Horizon Tech", "Cascade Manufacturing",
    "Delta Financial", "Eagle Retail Group", "Frontier Healthcare",
    "Global Shipping Co", "Harbor Industries", "Ironclad Security",
    "Jade Pharmaceuticals", "Keystone Analytics", "Lighthouse Media",
    "Meridian Consulting", "Northern Grid Energy", "Orbit Software",
    "Pacific Ventures", "Quantum Dynamics", "Riverstone Mining",
    "Summit Aerospace", "Titan Construction",
]

INDUSTRIES = ["Logistics", "Technology", "Manufacturing", "Finance", "Retail",
              "Healthcare", "Shipping", "Industrial", "Security", "Pharmaceuticals",
              "Analytics", "Media", "Consulting", "Energy", "Software",
              "Venture Capital", "Engineering", "Mining", "Aerospace", "Construction"]

REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]

ACCOUNT_MANAGERS = ["Sarah Chen", "James Okafor", "Maria Rodriguez",
                    "David Kim", "Priya Patel"]

PRODUCTS = ["DataSync Pro", "CloudVault Enterprise", "SecureEdge Suite",
            "AnalyticsCore", "ConnectAPI Platform", "AutoScale Engine",
            "ReportMaster", "DataSync Basic", "CloudVault Standard"]

ISSUE_TYPES = ["Billing Issue", "Technical Support", "Feature Request",
               "Access Problem", "Performance Issue", "Integration Error",
               "Data Export", "Account Management"]


def random_date(start_year=2020, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


# ─── CRM CSV ─────────────────────────────────────────────────────────────────
def generate_crm():
    rows = []
    for i, cid in enumerate(CUSTOMER_IDS):
        rows.append({
            "customer_id": cid,
            "customer_name": CUSTOMER_NAMES[i],
            "industry": INDUSTRIES[i],
            "region": random.choice(REGIONS),
            "account_manager": random.choice(ACCOUNT_MANAGERS),
            "annual_revenue": random.randint(500_000, 50_000_000),
            "employee_count": random.randint(50, 10_000),
            "customer_since": random_date(2015, 2022).strftime("%Y-%m-%d"),
            "account_status": random.choices(
                ["Active", "At Risk", "Churned"], weights=[70, 20, 10])[0],
        })
    path = os.path.join(BASE_DIR, "crm_customers.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  OK {path}")


# ─── Sales XLSX ──────────────────────────────────────────────────────────────
def generate_sales():
    rows = []
    for i in range(1, 201):
        cid = random.choice(CUSTOMER_IDS)
        product = random.choice(PRODUCTS)
        qty = random.randint(1, 50)
        unit_price = random.choice([299, 499, 999, 1499, 2999, 4999])
        rows.append({
            "transaction_id": f"TXN-{i:04d}",
            "customer_id": cid,
            "product": product,
            "sales_date": random_date(2023, 2025).strftime("%Y-%m-%d"),
            "quantity": qty,
            "unit_price": unit_price,
            "sales_amount": qty * unit_price,
            "region": random.choice(REGIONS),
            "sales_rep": random.choice(ACCOUNT_MANAGERS),
            "status": random.choices(["Closed Won", "Closed Lost", "Pending"],
                                     weights=[65, 20, 15])[0],
        })
    path = os.path.join(BASE_DIR, "sales_transactions.xlsx")
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False, sheet_name="Sales")
    print(f"  OK {path}")


# ─── Support Tickets CSV ──────────────────────────────────────────────────────
def generate_tickets():
    rows = []
    for i in range(1, 151):
        cid = random.choice(CUSTOMER_IDS)
        created = random_date(2023, 2025)
        resolved = random.random() > 0.25
        rows.append({
            "ticket_id": f"TKT-{i:04d}",
            "customer_id": cid,
            "issue_type": random.choice(ISSUE_TYPES),
            "priority": random.choices(["P1", "P2", "P3", "P4"],
                                       weights=[10, 25, 40, 25])[0],
            "product": random.choice(PRODUCTS),
            "created_date": created.strftime("%Y-%m-%d"),
            "status": "Resolved" if resolved else random.choice(["Open", "In Progress"]),
            "resolution_time_hours": round(random.uniform(0.5, 72), 1) if resolved else "",
            "description": _ticket_description(cid, random.choice(ISSUE_TYPES),
                                               random.choice(PRODUCTS)),
        })
    path = os.path.join(BASE_DIR, "support_tickets.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  OK {path}")


def _ticket_description(cid, issue, product):
    templates = [
        f"Customer {cid} reported {issue.lower()} with {product}. "
        f"User unable to access the system after recent update. "
        f"Requires immediate investigation by support team.",
        f"{product} experiencing intermittent {issue.lower()} for customer {cid}. "
        f"Error logs indicate authentication timeout. Escalated to Tier 2.",
        f"Customer {cid} submitted {issue.lower()} request regarding {product} licensing. "
        f"Account manager notified. SLA timer started.",
        f"Recurring {issue.lower()} issue reported by {cid} for {product}. "
        f"Previous ticket TKT-0001 related. Root cause analysis underway.",
    ]
    return random.choice(templates)


# ─── PDF content strings (ASCII-safe) ─────────────────────────────────────────

CUSTOMER_POLICY_TEXT = """
ACME ENTERPRISE -- CUSTOMER POLICY MANUAL
Version 3.2 | Effective Date: January 1, 2024

SECTION 1 -- CUSTOMER CLASSIFICATION
Acme Enterprise classifies customers into three tiers based on annual revenue:

  Tier 1 (Enterprise): Annual revenue contribution > $1,000,000
    - Dedicated account manager
    - Quarterly business reviews
    - 24/7 priority support access
    - Custom SLA agreements
    - Named support engineers

  Tier 2 (Business): Annual revenue $100,000 to $999,999
    - Assigned account manager
    - Semi-annual business reviews
    - Business hours support (8am-8pm local time)
    - Standard SLA: P1 = 4 hours, P2 = 8 hours

  Tier 3 (Standard): Annual revenue < $100,000
    - Shared account management pool
    - Annual review
    - Email/portal support only
    - Standard SLA: P1 = 8 hours, P2 = 24 hours

SECTION 2 -- ACCOUNT MANAGEMENT
Each customer is assigned an account manager responsible for:
  - Quarterly check-ins and business reviews
  - Renewal negotiations
  - Escalation handling
  - Upsell and cross-sell opportunities

Current account managers and their portfolios:
  - Sarah Chen: Technology, Software, Analytics sectors
  - James Okafor: Manufacturing, Industrial, Mining sectors
  - Maria Rodriguez: Healthcare, Pharmaceuticals, Consulting sectors
  - David Kim: Finance, Energy, Aerospace sectors
  - Priya Patel: Retail, Logistics, Shipping sectors

SECTION 3 -- CUSTOMER ONBOARDING
New customer onboarding follows a 5-step process:
  Step 1: Welcome call with account manager (Day 1)
  Step 2: Technical onboarding with implementation team (Days 2-5)
  Step 3: Product training sessions (Week 2)
  Step 4: Go-live support (Week 3)
  Step 5: 30-day post-launch review

SECTION 4 -- AT-RISK CUSTOMERS
Customers flagged as "At Risk" must be escalated immediately.
Criteria for At Risk designation:
  - Two or more P1 tickets within 30 days
  - Renewal date within 60 days with no renewal confirmation
  - Payment overdue by more than 30 days
  - NPS score below 6

SECTION 5 -- CHURNED ACCOUNTS
Churned accounts are retained in the system for 24 months.
Win-back campaigns are triggered automatically at 3 months post-churn.

SECTION 6 -- DATA RETENTION
Customer data is retained for 7 years per regulatory requirements.
PII data is anonymized after contract termination plus 2 years.

SECTION 7 -- COMPLIANCE
All customer interactions must comply with:
  - GDPR (EU customers)
  - CCPA (California customers)
  - SOC 2 Type II requirements
  - ISO 27001 standards

For questions about this policy, contact: policy@acme-enterprise.demo
"""

SUPPORT_POLICY_TEXT = """
ACME ENTERPRISE -- SUPPORT POLICY AND SLA
Version 2.1 | Effective Date: January 1, 2024

SECTION 1 -- PRIORITY LEVELS

P1 -- CRITICAL
Definition: Complete system outage or critical business function unavailable.
  - All production users affected
  - No viable workaround exists
  - Financial or reputational impact imminent
Initial Response SLA:
  - Tier 1 (Enterprise): 15 minutes
  - Tier 2 (Business): 30 minutes
  - Tier 3 (Standard): 1 hour
Resolution Target:
  - Tier 1: 2 hours
  - Tier 2: 4 hours
  - Tier 3: 8 hours
Escalation: Automatically escalated to Tier 2 support and account manager.
            If unresolved in 1 hour, VP of Support is notified.

P2 -- HIGH
Definition: Significant functionality impaired with no reasonable workaround.
  - Core feature unavailable
  - Significant user impact but system partially operational
Initial Response SLA:
  - Tier 1: 30 minutes
  - Tier 2: 1 hour
  - Tier 3: 4 hours
Resolution Target:
  - Tier 1: 4 hours
  - Tier 2: 8 hours
  - Tier 3: 24 hours

P3 -- MEDIUM
Definition: Non-critical functionality impaired; workaround available.
Initial Response SLA: 4 business hours (all tiers)
Resolution Target: 3 business days

P4 -- LOW
Definition: Minor issue, cosmetic problem, or general inquiry.
Initial Response SLA: 1 business day
Resolution Target: 5 business days

SECTION 2 -- SUPPORT CHANNELS
  - Enterprise Portal: support.acme-enterprise.demo (24/7)
  - Phone: +1-800-ACME-HELP (Tier 1 only, 24/7)
  - Email: support@acme-enterprise.demo
  - Slack Connect: Available for Tier 1 customers

SECTION 3 -- ESCALATION PATH
Level 1: Support Agent (first contact)
Level 2: Senior Support Engineer
Level 3: Support Team Lead
Level 4: VP of Customer Support
Level 5: CTO / Executive Escalation

SECTION 4 -- SUPPORT HOURS
  - Tier 1 Enterprise: 24/7/365
  - Tier 2 Business: Monday-Friday, 8am-8pm local time
  - Tier 3 Standard: Monday-Friday, 9am-5pm ET

SECTION 5 -- SLA BREACH POLICY
If SLA is breached:
  - P1 breach: 10% service credit applied automatically
  - P2 breach: 5% service credit upon request
  - Three P1 breaches in a quarter trigger executive review

SECTION 6 -- SUPPORTED PRODUCTS
All support policies apply to:
  - DataSync Pro and DataSync Basic
  - CloudVault Enterprise and CloudVault Standard
  - SecureEdge Suite
  - AnalyticsCore
  - ConnectAPI Platform
  - AutoScale Engine
  - ReportMaster

SECTION 7 -- OUT OF SCOPE
Support does not cover:
  - Third-party integrations not certified by Acme
  - Customer-modified code or configurations
  - Issues arising from unsupported browser versions
  - Data migration from non-Acme platforms (Professional Services required)

For support: support@acme-enterprise.demo
"""

PRODUCT_CATALOG_TEXT = """
ACME ENTERPRISE -- PRODUCT CATALOG 2024
Demo Environment -- Synthetic Enterprise Data

DATASYNC PRO
Category: Data Integration Platform
Price: $4,999/month
Description:
  DataSync Pro is our flagship enterprise data integration platform.
  Supports 200+ connectors including Salesforce, SAP, Oracle, and custom APIs.
  Features real-time sync, conflict resolution, and audit logging.
Key Features:
  - Real-time bidirectional sync
  - 200+ pre-built connectors
  - Visual workflow designer
  - Enterprise security (SOC 2, GDPR)
  - 99.9% uptime SLA
Best For: Enterprise customers with complex multi-system environments

DATASYNC BASIC
Category: Data Integration Platform
Price: $299/month
Description:
  Entry-level data sync for small to mid-size teams.
  Supports up to 20 connectors with daily batch sync.
Best For: Standard tier customers or SMB use cases

CLOUDVAULT ENTERPRISE
Category: Cloud Storage and Security
Price: $2,999/month
Description:
  Secure enterprise cloud storage with end-to-end encryption.
  Includes automated backup, disaster recovery, and compliance tooling.
Key Features:
  - Unlimited storage, AES-256 encryption
  - Automated daily backups, 90-day point-in-time recovery
  - HIPAA and SOX compliant
Best For: Healthcare, Finance, and regulated industries

CLOUDVAULT STANDARD
Category: Cloud Storage and Security
Price: $499/month
Description: Standard cloud storage with 10TB capacity and standard encryption.
Best For: Business tier customers

SECUREEDGE SUITE
Category: Security and Compliance
Price: $1,499/month
Description: Comprehensive security platform including SIEM and threat detection.
Key Features:
  - Real-time threat monitoring
  - Automated compliance reports (SOC 2, ISO 27001)
  - Zero-trust network access, 24/7 SOC integration
Best For: Enterprise customers in regulated industries

ANALYTICSCORE
Category: Business Intelligence
Price: $999/month
Description: Self-service analytics and reporting platform with AI-powered insights.
Best For: Business and Enterprise customers needing BI capabilities

CONNECTAPI PLATFORM
Category: API Management
Price: $1,499/month
Description: Full lifecycle API management including design, deployment, and monitoring.
Best For: Technology and Software companies

AUTOSCALE ENGINE
Category: Infrastructure Automation
Price: $2,999/month
Description: Intelligent infrastructure auto-scaling based on ML-driven demand prediction.
Best For: High-traffic applications

REPORTMASTER
Category: Reporting and Analytics
Price: $499/month
Description: Automated report generation and distribution platform.
Best For: Standard and Business tier customers

PROFESSIONAL SERVICES
  - Implementation services: $250/hour
  - Custom integration development: $300/hour
  - Training and certification programs: $1,500/day
  - Annual architecture review: $5,000 flat fee

For pricing and demos: sales@acme-enterprise.demo
"""

INVOICE_TEXT = """
ACME ENTERPRISE -- INVOICE SAMPLES
Demo Environment -- Synthetic Enterprise Data

INVOICE #INV-2024-001
Date: March 15, 2024 | Due: April 15, 2024
Customer: Apex Logistics (CUST-001)

  DataSync Pro Annual License       $4,999 x 12    $59,988.00
  CloudVault Enterprise Annual      $2,999 x 12    $35,988.00
  SecureEdge Suite Annual           $1,499 x 12    $17,988.00
  Implementation Services           40h x $250     $10,000.00
  Subtotal                                        $123,964.00
  Discount (Enterprise 10%)                       -$12,396.40
  Tax (8.5%)                                        $9,488.19
  TOTAL DUE                                       $121,055.79

Payment Terms: Net 30 | Reference: INV-2024-001-CUST001

INVOICE #INV-2024-002
Date: March 20, 2024 | Due: April 20, 2024
Customer: Blue Horizon Tech (CUST-002)

  CloudVault Enterprise Quarterly   $2,999 x 3      $8,997.00
  AnalyticsCore Quarterly           $999 x 3        $2,997.00
  ConnectAPI Platform Quarterly     $1,499 x 3      $4,497.00
  Training Workshop 2 days          $1,500 x 2      $3,000.00
  Subtotal                                         $19,491.00
  Tax (8.625% CA)                                   $1,681.59
  TOTAL DUE                                        $21,172.59

INVOICE #INV-2024-003
Date: April 1, 2024 | Due: May 1, 2024
Customer: Delta Financial (CUST-004)

  SecureEdge Suite Annual           $1,499 x 12    $17,988.00
  CloudVault Enterprise Annual      $2,999 x 12    $35,988.00
  Compliance Reporting Add-On       $500 x 12       $6,000.00
  Annual Architecture Review        Flat Fee        $5,000.00
  Subtotal                                         $64,976.00
  Discount (Finance 5%)                            -$3,248.80
  Tax (8.875% NY)                                   $5,488.80
  TOTAL DUE                                        $67,215.00

  Payment Status: PAID -- April 28, 2024

INVOICE #INV-2024-004
Date: April 10, 2024 | Due: May 10, 2024
Customer: Jade Pharmaceuticals (CUST-010)

  CloudVault Enterprise Annual      $2,999 x 12    $35,988.00
  SecureEdge Suite Annual           $1,499 x 12    $17,988.00
  HIPAA Compliance Module           $750 x 12       $9,000.00
  DataSync Pro Annual               $4,999 x 12    $59,988.00
  Subtotal                                        $122,964.00
  Discount (Pharma 8%)                             -$9,837.12
  Tax (6.25% MA)                                    $7,070.43
  TOTAL DUE                                       $120,197.31

  Payment Status: OVERDUE -- 15 days past due
"""


# ─── PDFs ─────────────────────────────────────────────────────────────────────
def generate_pdfs():
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("  PyMuPDF not installed -- writing placeholder PDFs as text")
        _write_placeholder_pdfs()
        return

    docs_dir = os.path.join(BASE_DIR, "documents")
    os.makedirs(docs_dir, exist_ok=True)

    _write_pdf(os.path.join(docs_dir, "customer_policy.pdf"),
               "Customer Policy Manual", CUSTOMER_POLICY_TEXT)
    _write_pdf(os.path.join(docs_dir, "support_policy.pdf"),
               "Support Policy and SLA", SUPPORT_POLICY_TEXT)
    _write_pdf(os.path.join(docs_dir, "product_catalog.pdf"),
               "Product Catalog 2024", PRODUCT_CATALOG_TEXT)
    _write_pdf(os.path.join(docs_dir, "invoice_samples.pdf"),
               "Invoice Samples", INVOICE_TEXT)


def _write_pdf(path, title, body):
    import fitz
    doc = fitz.open()
    font = fitz.Font("helv")

    # Title page
    page = doc.new_page()
    tw = fitz.TextWriter(page.rect)
    tw.append((72, 100), "Acme Enterprise", font=font, fontsize=24)
    tw.append((72, 135), "Demo Environment -- Synthetic Enterprise Data",
              font=font, fontsize=10)
    tw.append((72, 175), title, font=font, fontsize=18)
    tw.write_text(page)

    # Content pages
    lines = body.strip().split("\n")
    page = doc.new_page()
    tw2 = fitz.TextWriter(page.rect)
    y = 72
    for line in lines:
        if y > 750:
            tw2.write_text(page)
            page = doc.new_page()
            tw2 = fitz.TextWriter(page.rect)
            y = 72
        safe_line = line.encode("ascii", "replace").decode("ascii")
        tw2.append((72, y), safe_line, font=font, fontsize=10)
        y += 15
    tw2.write_text(page)

    doc.save(path)
    doc.close()
    print(f"  OK {path}")


def _write_placeholder_pdfs():
    """Write text files as placeholder if PyMuPDF is missing."""
    docs_dir = os.path.join(BASE_DIR, "documents")
    for name, content in [
        ("customer_policy.pdf", CUSTOMER_POLICY_TEXT),
        ("support_policy.pdf", SUPPORT_POLICY_TEXT),
        ("product_catalog.pdf", PRODUCT_CATALOG_TEXT),
        ("invoice_samples.pdf", INVOICE_TEXT),
    ]:
        path = os.path.join(docs_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  OK {path} (text placeholder)")


if __name__ == "__main__":
    print("Generating Acme Enterprise synthetic dataset...")
    print("Demo Environment -- Synthetic Enterprise Data\n")
    generate_crm()
    generate_sales()
    generate_tickets()
    generate_pdfs()
    print("\nDone.")
