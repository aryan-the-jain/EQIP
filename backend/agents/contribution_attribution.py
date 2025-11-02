"""
Contribution Attribution Agent

Analyzes contributor efforts and calculates weighted attribution for IP assets.
Supports multiple evidence types: code contributions, design work, reviews, and team votes.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ..schemas.schemas import (
    ContributorIn, ContributionEvent, TeamVote, 
    ContributionAttributionIn, ContributorAttribution, ContributionAttributionOut
)


# All models are now imported from schemas.py


def calculate_event_based_attribution(
    contributors: List[ContributorIn], 
    events: List[ContributionEvent],
    weights: Dict[str, float]
) -> Dict[str, Dict[str, Any]]:
    """Calculate attribution based on contribution events"""
    
    contributor_scores = {}
    
    # Initialize contributor data
    for contributor in contributors:
        contributor_scores[contributor.email] = {
            "name": contributor.display_name,
            "total_score": 0.0,
            "breakdown": {event_type: 0.0 for event_type in weights.keys()},
            "event_count": 0
        }
    
    # Process each contribution event
    for event in events:
        if event.contributor_email not in contributor_scores:
            continue
            
        # Calculate base score for this event
        base_score = 0.0
        
        if event.event_type == "code":
            # Code contributions: LOC * complexity * time factor
            loc_factor = min(event.lines_of_code / 100.0, 5.0) if event.lines_of_code else 1.0
            time_factor = min(event.hours_spent / 8.0, 3.0) if event.hours_spent else 1.0
            base_score = loc_factor * time_factor * event.complexity_score
            
        elif event.event_type == "design":
            # Design work: primarily time-based with complexity
            time_factor = min(event.hours_spent / 4.0, 4.0) if event.hours_spent else 1.0
            base_score = time_factor * event.complexity_score
            
        elif event.event_type == "review":
            # Code reviews: moderate time factor
            time_factor = min(event.hours_spent / 2.0, 2.0) if event.hours_spent else 1.0
            base_score = time_factor * event.complexity_score
            
        else:
            # Documentation, testing, etc.: time-based
            time_factor = min(event.hours_spent / 4.0, 2.0) if event.hours_spent else 1.0
            base_score = time_factor * event.complexity_score
        
        # Apply event type weight
        weighted_score = base_score * weights.get(event.event_type, 0.1)
        
        contributor_scores[event.contributor_email]["total_score"] += weighted_score
        contributor_scores[event.contributor_email]["breakdown"][event.event_type] += weighted_score
        contributor_scores[event.contributor_email]["event_count"] += 1
    
    return contributor_scores


def calculate_vote_based_attribution(
    contributors: List[ContributorIn],
    votes: List[TeamVote]
) -> Dict[str, Dict[str, Any]]:
    """Calculate attribution based on team votes"""
    
    contributor_scores = {}
    vote_counts = {}
    
    # Initialize
    for contributor in contributors:
        contributor_scores[contributor.email] = {
            "name": contributor.display_name,
            "total_score": 0.0,
            "vote_sum": 0.0,
            "vote_count": 0
        }
        vote_counts[contributor.email] = 0
    
    # Process votes
    for vote in votes:
        if vote.contributor_email in contributor_scores:
            contributor_scores[vote.contributor_email]["vote_sum"] += vote.weight
            contributor_scores[vote.contributor_email]["vote_count"] += 1
            vote_counts[vote.contributor_email] += 1
    
    # Calculate average vote scores
    for email, data in contributor_scores.items():
        if data["vote_count"] > 0:
            data["total_score"] = data["vote_sum"] / data["vote_count"]
        else:
            data["total_score"] = 0.0
    
    return contributor_scores


def normalize_attributions(scores: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Normalize attribution scores to sum to 1.0"""
    
    total_score = sum(data["total_score"] for data in scores.values())
    
    if total_score == 0:
        # Equal distribution if no scores
        equal_weight = 1.0 / len(scores) if scores else 0.0
        for data in scores.values():
            data["normalized_weight"] = equal_weight
    else:
        # Normalize to sum to 1.0
        for data in scores.values():
            data["normalized_weight"] = data["total_score"] / total_score
    
    return scores


async def run_async(payload: ContributionAttributionIn) -> ContributionAttributionOut:
    """
    Main async function for contribution attribution analysis
    """
    return run(payload)


def run(payload: ContributionAttributionIn) -> ContributionAttributionOut:
    """
    Analyze contributions and calculate weighted attribution for IP asset
    
    Args:
        payload: ContributionAttributionIn with asset info, contributors, events, and votes
        
    Returns:
        ContributionAttributionOut with calculated attributions and methodology
    """
    
    if not payload.contributors:
        return ContributionAttributionOut(
            asset_id=payload.asset_id,
            attributions=[],
            total_weight=0.0,
            methodology="No contributors provided",
            confidence_score=0.0
        )
    
    # Calculate attribution based on mode
    if payload.mode == "events_only" and payload.contribution_events:
        scores = calculate_event_based_attribution(
            payload.contributors, 
            payload.contribution_events, 
            payload.weights
        )
        methodology = "Event-based attribution using contribution data"
        confidence = 0.8 if len(payload.contribution_events) >= len(payload.contributors) else 0.6
        
    elif payload.mode == "votes_only" and payload.team_votes:
        scores = calculate_vote_based_attribution(payload.contributors, payload.team_votes)
        methodology = "Vote-based attribution using team consensus"
        confidence = 0.7 if len(payload.team_votes) >= len(payload.contributors) else 0.5
        
    elif payload.mode == "hybrid" and (payload.contribution_events or payload.team_votes):
        # Combine both methods
        event_scores = {}
        vote_scores = {}
        
        if payload.contribution_events:
            event_scores = calculate_event_based_attribution(
                payload.contributors, 
                payload.contribution_events, 
                payload.weights
            )
        
        if payload.team_votes:
            vote_scores = calculate_vote_based_attribution(payload.contributors, payload.team_votes)
        
        # Merge scores (60% events, 40% votes if both available)
        scores = {}
        for contributor in payload.contributors:
            email = contributor.email
            scores[email] = {
                "name": contributor.display_name,
                "total_score": 0.0,
                "breakdown": {}
            }
            
            event_score = event_scores.get(email, {}).get("total_score", 0.0)
            vote_score = vote_scores.get(email, {}).get("total_score", 0.0)
            
            if event_scores and vote_scores:
                scores[email]["total_score"] = 0.6 * event_score + 0.4 * vote_score
                scores[email]["breakdown"] = event_scores.get(email, {}).get("breakdown", {})
            elif event_scores:
                scores[email]["total_score"] = event_score
                scores[email]["breakdown"] = event_scores.get(email, {}).get("breakdown", {})
            elif vote_scores:
                scores[email]["total_score"] = vote_score
        
        methodology = "Hybrid attribution combining events and team votes"
        confidence = 0.85 if (payload.contribution_events and payload.team_votes) else 0.7
        
    else:
        # Fallback to equal distribution
        scores = {}
        equal_score = 1.0 / len(payload.contributors)
        for contributor in payload.contributors:
            scores[contributor.email] = {
                "name": contributor.display_name,
                "total_score": equal_score,
                "breakdown": {}
            }
        methodology = "Equal distribution (no contribution data available)"
        confidence = 0.3
    
    # Normalize scores
    scores = normalize_attributions(scores)
    
    # Build attribution results
    attributions = []
    for email, data in scores.items():
        # Create rationale
        rationale_parts = []
        if "breakdown" in data and data["breakdown"]:
            for contrib_type, score in data["breakdown"].items():
                if score > 0:
                    rationale_parts.append(f"{contrib_type}: {score:.2f}")
        
        if not rationale_parts:
            rationale = f"Attributed {data['normalized_weight']:.1%} based on {methodology.lower()}"
        else:
            rationale = f"Breakdown: {', '.join(rationale_parts)}. Final weight: {data['normalized_weight']:.1%}"
        
        attributions.append(ContributorAttribution(
            contributor_email=email,
            contributor_name=data["name"],
            weight=data["normalized_weight"],
            rationale=rationale,
            breakdown=data.get("breakdown", {})
        ))
    
    # Sort by weight (highest first)
    attributions.sort(key=lambda x: x.weight, reverse=True)
    
    total_weight = sum(attr.weight for attr in attributions)
    
    return ContributionAttributionOut(
        asset_id=payload.asset_id,
        attributions=attributions,
        total_weight=total_weight,
        methodology=methodology,
        confidence_score=confidence
    )
