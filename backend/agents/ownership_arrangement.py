"""
Ownership Arrangement Engine

Extends the allocation agent to support multiple ownership policies and 
creates finalized ownership arrangements with governance structures.
"""

import yaml
from typing import List, Dict, Any
from ..schemas.schemas import (
    AllocationIn, AllocationOut, 
    OwnershipArrangementIn, OwnershipArrangementOut,
    OwnershipShare as OwnershipShareSchema, ContributorAttribution
)


def calculate_equal_ownership(contributors: List[ContributorAttribution], total_shares: int = 1000000) -> List[OwnershipShareSchema]:
    """Calculate equal ownership distribution"""
    if not contributors:
        return []
    
    shares_per_contributor = total_shares // len(contributors)
    remaining_shares = total_shares % len(contributors)
    
    ownership_shares = []
    for i, contributor in enumerate(contributors):
        # Give extra shares to first contributors if there's a remainder
        shares = shares_per_contributor + (1 if i < remaining_shares else 0)
        percentage = (shares / total_shares) * 100
        
        ownership_shares.append(OwnershipShareSchema(
            contributor_email=contributor.contributor_email,
            contributor_name=contributor.contributor_name,
            shares=shares,
            percentage=percentage,
            governance_rights="equal"
        ))
    
    return ownership_shares


def calculate_weighted_ownership(contributors: List[ContributorAttribution], total_shares: int = 1000000) -> List[OwnershipShareSchema]:
    """Calculate ownership based on contribution weights"""
    if not contributors:
        return []
    
    ownership_shares = []
    for contributor in contributors:
        shares = int(contributor.weight * total_shares)
        percentage = contributor.weight * 100
        
        # Determine governance rights based on ownership percentage
        if percentage >= 50:
            governance_rights = "majority"
        elif percentage >= 25:
            governance_rights = "significant"
        elif percentage >= 10:
            governance_rights = "standard"
        else:
            governance_rights = "minority"
        
        ownership_shares.append(OwnershipShareSchema(
            contributor_email=contributor.contributor_email,
            contributor_name=contributor.contributor_name,
            shares=shares,
            percentage=percentage,
            governance_rights=governance_rights
        ))
    
    return ownership_shares


def calculate_funding_based_ownership(
    contributors: List[ContributorAttribution], 
    policy_params: Dict[str, Any],
    total_shares: int = 1000000
) -> List[OwnershipShareSchema]:
    """Calculate ownership based on funding contributions"""
    
    # Get funding data from policy params
    funding_data = policy_params.get("funding", {})
    sweat_equity_weight = policy_params.get("sweat_equity_weight", 0.3)
    
    if not funding_data:
        # Fallback to weighted if no funding data
        return calculate_weighted_ownership(contributors, total_shares)
    
    ownership_shares = []
    
    for contributor in contributors:
        # Base ownership from contribution weight (sweat equity)
        sweat_equity_share = contributor.weight * sweat_equity_weight
        
        # Additional ownership from funding
        funding_amount = funding_data.get(contributor.contributor_email, 0)
        total_funding = sum(funding_data.values()) if funding_data.values() else 1
        funding_share = (funding_amount / total_funding) * (1 - sweat_equity_weight) if total_funding > 0 else 0
        
        # Combined ownership
        total_ownership = sweat_equity_share + funding_share
        shares = int(total_ownership * total_shares)
        percentage = total_ownership * 100
        
        # Governance rights based on combined ownership
        if percentage >= 50:
            governance_rights = "majority"
        elif percentage >= 25:
            governance_rights = "significant"
        elif funding_amount > 0:
            governance_rights = "investor"
        else:
            governance_rights = "standard"
        
        ownership_shares.append(OwnershipShareSchema(
            contributor_email=contributor.contributor_email,
            contributor_name=contributor.contributor_name,
            shares=shares,
            percentage=percentage,
            governance_rights=governance_rights
        ))
    
    return ownership_shares


def calculate_time_vested_ownership(
    contributors: List[ContributorAttribution],
    policy_params: Dict[str, Any],
    total_shares: int = 1000000
) -> List[OwnershipShareSchema]:
    """Calculate ownership with time-based vesting"""
    
    vesting_period_months = policy_params.get("vesting_period_months", 48)  # 4 years default
    cliff_months = policy_params.get("cliff_months", 12)  # 1 year cliff
    
    ownership_shares = []
    
    for contributor in contributors:
        # Get contributor's time data
        months_contributed = policy_params.get("time_data", {}).get(contributor.contributor_email, 12)
        
        # Calculate vesting percentage
        if months_contributed < cliff_months:
            vested_percentage = 0.0
        else:
            vested_percentage = min(months_contributed / vesting_period_months, 1.0)
        
        # Base ownership from contribution weight
        base_ownership = contributor.weight
        vested_ownership = base_ownership * vested_percentage
        
        shares = int(vested_ownership * total_shares)
        percentage = vested_ownership * 100
        
        # Governance rights include vesting status
        if vested_percentage == 1.0:
            governance_rights = "fully_vested"
        elif vested_percentage > 0.5:
            governance_rights = "partially_vested"
        elif vested_percentage > 0:
            governance_rights = "cliff_vested"
        else:
            governance_rights = "unvested"
        
        ownership_shares.append(OwnershipShareSchema(
            contributor_email=contributor.contributor_email,
            contributor_name=contributor.contributor_name,
            shares=shares,
            percentage=percentage,
            governance_rights=governance_rights
        ))
    
    return ownership_shares


def generate_governance_summary(ownership_shares: List[OwnershipShareSchema], policy_type: str) -> str:
    """Generate a summary of governance structure"""
    
    if not ownership_shares:
        return "No ownership structure defined."
    
    total_contributors = len(ownership_shares)
    majority_holders = [s for s in ownership_shares if s.percentage >= 50]
    significant_holders = [s for s in ownership_shares if 25 <= s.percentage < 50]
    
    summary_parts = [
        f"Ownership distributed among {total_contributors} contributors using {policy_type} policy."
    ]
    
    if majority_holders:
        summary_parts.append(f"Majority control: {majority_holders[0].contributor_name} ({majority_holders[0].percentage:.1f}%)")
    elif significant_holders:
        summary_parts.append(f"Significant stakeholders: {', '.join([f'{s.contributor_name} ({s.percentage:.1f}%)' for s in significant_holders])}")
    else:
        summary_parts.append("No single majority holder - distributed ownership structure.")
    
    # Add policy-specific governance notes
    if policy_type == "equal":
        summary_parts.append("All contributors have equal voting rights.")
    elif policy_type == "weighted":
        summary_parts.append("Voting rights proportional to contribution weights.")
    elif policy_type == "funding_based":
        summary_parts.append("Governance includes both sweat equity and financial investment considerations.")
    elif policy_type == "time_vested":
        summary_parts.append("Ownership subject to time-based vesting schedules.")
    
    return " ".join(summary_parts)


def run_ownership_arrangement(payload: OwnershipArrangementIn) -> OwnershipArrangementOut:
    """
    Create finalized ownership arrangement based on attribution and policy
    
    Args:
        payload: OwnershipArrangementIn with attribution weights and policy
        
    Returns:
        OwnershipArrangementOut with ownership table and governance summary
    """
    
    if not payload.attribution_weights:
        return OwnershipArrangementOut(
            asset_id=payload.asset_id,
            ownership_table=[],
            total_shares=0,
            governance_summary="No contributors provided for ownership arrangement.",
            policy_applied=payload.policy_type
        )
    
    total_shares = payload.policy_params.get("total_shares", 1000000)
    
    # Calculate ownership based on policy type
    if payload.policy_type == "equal":
        ownership_shares = calculate_equal_ownership(payload.attribution_weights, total_shares)
        
    elif payload.policy_type == "weighted":
        ownership_shares = calculate_weighted_ownership(payload.attribution_weights, total_shares)
        
    elif payload.policy_type == "funding_based":
        ownership_shares = calculate_funding_based_ownership(
            payload.attribution_weights, 
            payload.policy_params, 
            total_shares
        )
        
    elif payload.policy_type == "time_vested":
        ownership_shares = calculate_time_vested_ownership(
            payload.attribution_weights,
            payload.policy_params,
            total_shares
        )
        
    else:
        # Default to weighted
        ownership_shares = calculate_weighted_ownership(payload.attribution_weights, total_shares)
    
    # Ensure shares add up correctly
    actual_total_shares = sum(share.shares for share in ownership_shares)
    if actual_total_shares != total_shares and ownership_shares:
        # Adjust the largest holder's shares to match total
        largest_holder = max(ownership_shares, key=lambda x: x.shares)
        adjustment = total_shares - actual_total_shares
        largest_holder.shares += adjustment
        largest_holder.percentage = (largest_holder.shares / total_shares) * 100
    
    # Generate governance summary
    governance_summary = generate_governance_summary(ownership_shares, payload.policy_type)
    
    return OwnershipArrangementOut(
        asset_id=payload.asset_id,
        ownership_table=ownership_shares,
        total_shares=total_shares,
        governance_summary=governance_summary,
        policy_applied=payload.policy_type
    )


# Legacy allocation function for backward compatibility
def run(payload: AllocationIn) -> AllocationOut:
    """Legacy allocation function - maintains backward compatibility"""
    try:
        policy = yaml.safe_load(payload.policy_yaml) if payload.policy_yaml else {}
    except Exception:
        policy = {}
    
    n = policy.get("assume_contributors", 3)
    share = round(100.0 / n, 2)
    shares = [{"contributor": f"user{i+1}", "pct": share} for i in range(n)]
    return AllocationOut(shares=shares, warnings=[])
