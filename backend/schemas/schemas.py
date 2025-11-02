from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ContributorIn(BaseModel):
    email: str
    display_name: str
    org: Optional[str] = None

class AssetCreate(BaseModel):
    name: Optional[str] = None
    type: str
    uri: Optional[str] = None
    contributors: List[ContributorIn] = []
    sector: Optional[str] = None
    jurisdictions: List[str] = []

class AssetOut(BaseModel):
    asset_id: int

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class IPOptionsIn(BaseModel):
    asset_id: int
    questions: Optional[str] = None
    jurisdictions: list[str] = []
    conversation_context: Optional[List[ConversationMessage]] = []

class IPOptionsOut(BaseModel):
    options: list[str]
    risks: list[str]
    next_steps: list[str]
    citations: list[str] = []

class AllocationIn(BaseModel):
    asset_id: int
    policy_yaml: str

class AllocationOut(BaseModel):
    shares: list[dict]
    warnings: list[str] = []

class DraftAgreementIn(BaseModel):
    asset_id: int
    type: str
    policy_id: Optional[int] = None

class DraftAgreementOut(BaseModel):
    agreement_id: int
    s3_uri: Optional[str] = None
    sign_url: Optional[str] = None

# New schemas for extended pipeline

class ContributionEvent(BaseModel):
    """Individual contribution event with metadata"""
    contributor_email: str
    event_type: str = Field(..., description="Type: 'code', 'design', 'review', 'documentation', 'testing'")
    lines_of_code: Optional[int] = Field(0, description="Lines of code added/modified")
    hours_spent: Optional[float] = Field(0, description="Time spent in hours")
    complexity_score: Optional[float] = Field(1.0, description="Complexity multiplier (1.0 = normal, 2.0 = high)")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    description: Optional[str] = Field("", description="Brief description of contribution")

class TeamVote(BaseModel):
    """Team member vote for contribution weighting"""
    voter_email: str
    contributor_email: str
    weight: float = Field(..., ge=0, le=1, description="Vote weight between 0 and 1")
    rationale: Optional[str] = Field("", description="Reason for the vote")

class ContributionAttributionIn(BaseModel):
    """Input for contribution attribution analysis"""
    asset_id: int
    contributors: List[ContributorIn]
    contribution_events: List[ContributionEvent] = []
    team_votes: List[TeamVote] = []
    mode: str = Field("hybrid", description="Attribution mode: 'events_only', 'votes_only', 'hybrid'")
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "code": 0.4,
            "design": 0.3, 
            "review": 0.15,
            "documentation": 0.1,
            "testing": 0.05
        },
        description="Weight multipliers for different contribution types"
    )

class ContributorAttribution(BaseModel):
    """Attribution result for a single contributor"""
    contributor_email: str
    contributor_name: str
    weight: float = Field(..., ge=0, le=1, description="Final attribution weight")
    rationale: str = Field(..., description="Explanation of how weight was calculated")
    breakdown: Dict[str, float] = Field(default_factory=dict, description="Breakdown by contribution type")

class ContributionAttributionOut(BaseModel):
    """Output of contribution attribution analysis"""
    asset_id: int
    attributions: List[ContributorAttribution]
    total_weight: float = Field(..., description="Should sum to 1.0")
    methodology: str = Field(..., description="Description of attribution methodology used")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the attribution")

class OwnershipArrangementIn(BaseModel):
    """Input for ownership arrangement finalization"""
    asset_id: int
    attribution_weights: List[ContributorAttribution] = []
    policy_type: str = Field("weighted", description="Policy: 'equal', 'weighted', 'funding_based', 'time_vested'")
    policy_params: Dict[str, Any] = Field(default_factory=dict, description="Additional policy parameters")

class OwnershipShare(BaseModel):
    """Individual ownership share"""
    contributor_email: str
    contributor_name: str
    shares: int
    percentage: float
    governance_rights: str = Field("standard", description="Governance rights level")

class OwnershipArrangementOut(BaseModel):
    """Output of ownership arrangement"""
    asset_id: int
    ownership_table: List[OwnershipShare]
    total_shares: int
    governance_summary: str
    policy_applied: str

class ContractGenerationIn(BaseModel):
    """Input for contract generation"""
    asset_id: int
    contract_type: str = Field(..., description="Type: 'nda', 'ip_assignment', 'jda', 'revenue_share'")
    ownership_arrangement: OwnershipArrangementOut
    additional_clauses: List[str] = []
    jurisdiction: str = Field("US", description="Legal jurisdiction")

class ContractGenerationOut(BaseModel):
    """Output of contract generation"""
    agreement_id: str
    contract_type: str
    draft_text: str
    clauses: List[str]
    sign_url: Optional[str] = None
    download_url: Optional[str] = None

class LicenseRecommendationIn(BaseModel):
    """Input for license recommendation"""
    asset_id: int
    asset_type: str
    ownership_arrangement: OwnershipArrangementOut
    intended_use: str = Field("commercial", description="Intended use: 'commercial', 'open_source', 'research'")
    dependencies: List[str] = Field(default_factory=list, description="List of dependency licenses")

class LicenseRecommendation(BaseModel):
    """Individual license recommendation"""
    license_name: str
    compatibility_score: float = Field(..., ge=0, le=1)
    rationale: str
    usage_terms: str
    obligations: List[str]

class LicenseRecommendationOut(BaseModel):
    """Output of license recommendation"""
    asset_id: int
    recommended_licenses: List[LicenseRecommendation]
    primary_recommendation: LicenseRecommendation
    compatibility_issues: List[str] = []
