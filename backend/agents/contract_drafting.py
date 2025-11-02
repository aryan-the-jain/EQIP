"""
Contract Drafting Agent

Auto-generates legal documents using Jinja2 templates based on asset information,
contributor data, and ownership arrangements.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any
from jinja2 import Environment, BaseLoader, Template
from ..schemas.schemas import (
    ContractGenerationIn, ContractGenerationOut, 
    OwnershipArrangementOut, OwnershipShare
)


class StringTemplateLoader(BaseLoader):
    """Custom Jinja2 loader for string templates"""
    
    def __init__(self, templates: Dict[str, str]):
        self.templates = templates
    
    def get_source(self, environment: Environment, template: str):
        if template not in self.templates:
            raise FileNotFoundError(f"Template {template} not found")
        source = self.templates[template]
        return source, None, lambda: True


# Contract templates
CONTRACT_TEMPLATES = {
    "nda": """
NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into on {{ current_date }} by and between:

{% for share in ownership_arrangement.ownership_table %}
{{ share.contributor_name }} ({{ share.contributor_email }}) - {{ share.percentage }}% ownership
{% endfor %}

(collectively, the "Parties")

RECITALS

WHEREAS, the Parties wish to explore potential collaboration regarding {{ asset_type }} asset (ID: {{ asset_id }});

WHEREAS, in connection with such discussions, the Parties may disclose certain confidential and proprietary information;

NOW, THEREFORE, in consideration of the mutual covenants contained herein, the Parties agree as follows:

1. DEFINITION OF CONFIDENTIAL INFORMATION
   "Confidential Information" means any and all non-public, confidential or proprietary information disclosed by one Party to another, including but not limited to:
   - Technical data, algorithms, source code, and software
   - Business plans, financial information, and customer lists
   - Research and development information
   - Any information related to the {{ asset_type }} asset

2. OBLIGATIONS OF RECEIVING PARTY
   Each Party agrees to:
   a) Hold all Confidential Information in strict confidence
   b) Not disclose Confidential Information to third parties without prior written consent
   c) Use Confidential Information solely for evaluation purposes
   d) Return or destroy all Confidential Information upon request

3. EXCEPTIONS
   This Agreement does not apply to information that:
   a) Is publicly available through no breach of this Agreement
   b) Was known to the receiving Party prior to disclosure
   c) Is independently developed without use of Confidential Information

4. TERM
   This Agreement shall remain in effect for a period of {{ nda_term_years | default(5) }} years from the date of execution.

5. GOVERNING LAW
   This Agreement shall be governed by the laws of {{ jurisdiction }}.

IN WITNESS WHEREOF, the Parties have executed this Agreement as of the date first written above.

{% for share in ownership_arrangement.ownership_table %}
_________________________
{{ share.contributor_name }}
Date: ___________

{% endfor %}
""",

    "ip_assignment": """
INTELLECTUAL PROPERTY ASSIGNMENT AGREEMENT

This Intellectual Property Assignment Agreement ("Agreement") is made on {{ current_date }} among:

{% for share in ownership_arrangement.ownership_table %}
{{ share.contributor_name }} ({{ share.contributor_email }}) - {{ share.percentage }}% ownership, {{ share.shares }} shares
{% endfor %}

(collectively, the "Assignors" and "Assignees")

RECITALS

WHEREAS, the parties have collaborated in the development of {{ asset_type }} asset (ID: {{ asset_id }});

WHEREAS, the parties wish to clarify ownership rights and assign intellectual property interests;

NOW, THEREFORE, the parties agree as follows:

1. ASSIGNMENT OF RIGHTS
   Each party hereby assigns to the collective ownership structure the following rights in the {{ asset_type }} asset:
   - All copyright interests
   - All patent rights and applications
   - All trade secret rights
   - All other intellectual property rights

2. OWNERSHIP STRUCTURE
   The intellectual property shall be owned as follows:
   {% for share in ownership_arrangement.ownership_table %}
   - {{ share.contributor_name }}: {{ share.percentage }}% ({{ share.shares }} shares)
     Governance Rights: {{ share.governance_rights }}
   {% endfor %}

3. GOVERNANCE AND DECISION MAKING
   {{ ownership_arrangement.governance_summary }}

4. REPRESENTATIONS AND WARRANTIES
   Each party represents and warrants that:
   a) They have the right to assign the intellectual property
   b) The intellectual property does not infringe third-party rights
   c) They have not previously assigned these rights to others

5. FUTURE DEVELOPMENTS
   Any future improvements or derivative works shall be owned according to the same ownership structure, unless otherwise agreed in writing.

6. COMMERCIALIZATION
   Decisions regarding licensing, commercialization, or sale of the intellectual property shall require:
   {% if ownership_arrangement.ownership_table | selectattr('percentage', 'ge', 50) | list %}
   - Approval from the majority owner
   {% else %}
   - Unanimous consent of all parties
   {% endif %}

7. GOVERNING LAW
   This Agreement shall be governed by the laws of {{ jurisdiction }}.

IN WITNESS WHEREOF, the parties have executed this Agreement.

{% for share in ownership_arrangement.ownership_table %}
_________________________
{{ share.contributor_name }}
{{ share.contributor_email }}
Date: ___________

{% endfor %}
""",

    "jda": """
JOINT DEVELOPMENT AGREEMENT

This Joint Development Agreement ("Agreement") is entered into on {{ current_date }} by and between:

{% for share in ownership_arrangement.ownership_table %}
{{ share.contributor_name }} ({{ share.contributor_email }}) - {{ share.percentage }}% interest
{% endfor %}

(collectively, the "Parties")

RECITALS

WHEREAS, the Parties desire to jointly develop and enhance {{ asset_type }} asset (ID: {{ asset_id }});

WHEREAS, the Parties wish to establish terms for their collaboration and resulting intellectual property;

NOW, THEREFORE, the Parties agree as follows:

1. DEVELOPMENT OBJECTIVES
   The Parties shall collaborate to:
   - Enhance and improve the existing {{ asset_type }} asset
   - Develop new features and capabilities
   - Prepare the asset for commercialization

2. CONTRIBUTIONS AND RESPONSIBILITIES
   {% for share in ownership_arrangement.ownership_table %}
   {{ share.contributor_name }} ({{ share.percentage }}% interest):
   - Governance Rights: {{ share.governance_rights }}
   - Expected to contribute proportionally to development efforts
   {% endfor %}

3. INTELLECTUAL PROPERTY OWNERSHIP
   All intellectual property developed under this Agreement shall be owned as follows:
   {% for share in ownership_arrangement.ownership_table %}
   - {{ share.contributor_name }}: {{ share.percentage }}%
   {% endfor %}

4. DECISION MAKING
   {{ ownership_arrangement.governance_summary }}

5. CONFIDENTIALITY
   All Parties agree to maintain confidentiality of:
   - Development plans and strategies
   - Technical information and trade secrets
   - Business and financial information

6. TERM AND TERMINATION
   This Agreement shall commence on {{ current_date }} and continue until:
   a) Completion of development objectives, or
   b) Termination by mutual consent, or
   c) {{ jda_term_years | default(3) }} years from the effective date

7. COMMERCIALIZATION
   Upon completion of development:
   - Revenue sharing shall follow ownership percentages
   - Licensing decisions require appropriate governance approval
   - Each party may use the developed IP for their own purposes

8. GOVERNING LAW
   This Agreement shall be governed by the laws of {{ jurisdiction }}.

IN WITNESS WHEREOF, the Parties have executed this Agreement.

{% for share in ownership_arrangement.ownership_table %}
_________________________
{{ share.contributor_name }}
Date: ___________

{% endfor %}
""",

    "revenue_share": """
REVENUE SHARING ADDENDUM

This Revenue Sharing Addendum ("Addendum") is made on {{ current_date }} and supplements existing agreements regarding {{ asset_type }} asset (ID: {{ asset_id }}).

PARTIES:
{% for share in ownership_arrangement.ownership_table %}
{{ share.contributor_name }} ({{ share.contributor_email }}) - {{ share.percentage }}% ownership
{% endfor %}

REVENUE SHARING TERMS:

1. REVENUE DISTRIBUTION
   Net revenues from the commercialization of the asset shall be distributed as follows:
   {% for share in ownership_arrangement.ownership_table %}
   - {{ share.contributor_name }}: {{ share.percentage }}%
   {% endfor %}

2. REVENUE CALCULATION
   "Net Revenue" means gross revenue less:
   - Direct costs of sales and marketing
   - Platform fees and transaction costs
   - Taxes and regulatory fees
   - Agreed operational expenses (max {{ max_operational_deduction | default(15) }}%)

3. PAYMENT TERMS
   - Revenue distributions shall be made {{ payment_frequency | default('quarterly') }}
   - Payments due within 30 days of period end
   - Detailed accounting statements provided with each payment

4. GOVERNANCE OF REVENUE DECISIONS
   {{ ownership_arrangement.governance_summary }}

5. LICENSING AND PARTNERSHIPS
   Revenue from licensing deals and partnerships shall be subject to the same distribution percentages.

6. ACCOUNTING AND RECORDS
   - Detailed records of all revenue and expenses shall be maintained
   - All parties have right to audit records annually
   - Independent accounting firm may be engaged if disputes arise

7. MINIMUM REVENUE THRESHOLDS
   If annual revenue falls below ${{ min_revenue_threshold | default(10000) }}, parties may:
   - Renegotiate terms
   - Dissolve the revenue sharing arrangement
   - Seek alternative commercialization strategies

8. TERM
   This Addendum shall remain in effect for {{ revenue_term_years | default(10) }} years or until terminated by mutual agreement.

IN WITNESS WHEREOF, the parties have executed this Addendum.

{% for share in ownership_arrangement.ownership_table %}
_________________________
{{ share.contributor_name }}
Date: ___________

{% endfor %}
"""
}


def generate_contract_clauses(contract_type: str, ownership_arrangement: OwnershipArrangementOut) -> List[str]:
    """Generate standard clauses based on contract type and ownership structure"""
    
    clauses = []
    
    # Common clauses
    clauses.extend([
        "Governing Law and Jurisdiction",
        "Entire Agreement",
        "Amendment and Modification",
        "Severability",
        "Force Majeure"
    ])
    
    # Contract-specific clauses
    if contract_type == "nda":
        clauses.extend([
            "Definition of Confidential Information",
            "Obligations of Receiving Party",
            "Exceptions to Confidentiality",
            "Return of Materials",
            "Remedies for Breach"
        ])
    
    elif contract_type == "ip_assignment":
        clauses.extend([
            "Assignment of Rights",
            "Ownership Structure",
            "Representations and Warranties",
            "Future Developments",
            "Commercialization Rights"
        ])
    
    elif contract_type == "jda":
        clauses.extend([
            "Development Objectives",
            "Contributions and Responsibilities",
            "Intellectual Property Ownership",
            "Decision Making Process",
            "Confidentiality Obligations",
            "Term and Termination"
        ])
    
    elif contract_type == "revenue_share":
        clauses.extend([
            "Revenue Distribution",
            "Revenue Calculation",
            "Payment Terms",
            "Accounting and Records",
            "Minimum Thresholds",
            "Audit Rights"
        ])
    
    # Add governance-specific clauses based on ownership structure
    majority_holders = [s for s in ownership_arrangement.ownership_table if s.percentage >= 50]
    if majority_holders:
        clauses.append("Majority Control Provisions")
    else:
        clauses.append("Unanimous Consent Requirements")
    
    return clauses


def run_contract_generation(payload: ContractGenerationIn) -> ContractGenerationOut:
    """
    Generate legal contract based on ownership arrangement and contract type
    
    Args:
        payload: ContractGenerationIn with contract requirements
        
    Returns:
        ContractGenerationOut with generated contract text
    """
    
    if payload.contract_type not in CONTRACT_TEMPLATES:
        raise ValueError(f"Unsupported contract type: {payload.contract_type}")
    
    # Create Jinja2 environment
    loader = StringTemplateLoader(CONTRACT_TEMPLATES)
    env = Environment(loader=loader)
    
    # Load template
    template = env.get_template(payload.contract_type)
    
    # Prepare template variables
    template_vars = {
        "asset_id": payload.asset_id,
        "asset_type": "intellectual property",  # Could be derived from asset data
        "ownership_arrangement": payload.ownership_arrangement,
        "current_date": datetime.now().strftime("%B %d, %Y"),
        "jurisdiction": payload.jurisdiction,
        "additional_clauses": payload.additional_clauses
    }
    
    # Add contract-specific defaults
    if payload.contract_type == "nda":
        template_vars.update({
            "nda_term_years": 5
        })
    elif payload.contract_type == "jda":
        template_vars.update({
            "jda_term_years": 3
        })
    elif payload.contract_type == "revenue_share":
        template_vars.update({
            "payment_frequency": "quarterly",
            "max_operational_deduction": 15,
            "min_revenue_threshold": 10000,
            "revenue_term_years": 10
        })
    
    # Render contract
    try:
        draft_text = template.render(**template_vars)
    except Exception as e:
        raise ValueError(f"Error rendering contract template: {str(e)}")
    
    # Generate clauses list
    clauses = generate_contract_clauses(payload.contract_type, payload.ownership_arrangement)
    clauses.extend(payload.additional_clauses)
    
    # Generate unique agreement ID
    agreement_id = str(uuid.uuid4())
    
    # In a real implementation, you would:
    # 1. Save the contract to storage (S3, database, etc.)
    # 2. Generate signing URLs (DocuSign, HelloSign, etc.)
    # 3. Create download URLs
    
    return ContractGenerationOut(
        agreement_id=agreement_id,
        contract_type=payload.contract_type,
        draft_text=draft_text,
        clauses=clauses,
        sign_url=f"https://sign.eqip.ai/agreements/{agreement_id}",  # Placeholder
        download_url=f"https://api.eqip.ai/agreements/{agreement_id}/download"  # Placeholder
    )


# Legacy function for backward compatibility
def run(payload) -> dict:
    """Legacy contract composer function"""
    return {
        "agreement_id": 1,
        "s3_uri": "s3://eqip/drafts/example.pdf",
        "sign_url": None
    }
