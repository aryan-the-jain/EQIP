"""
License Generator Service

Recommends appropriate licenses based on asset type, ownership structure,
and intended use. Ensures compatibility with dependencies and provides
usage terms and obligations.
"""

from typing import List, Dict, Any, Tuple
from ..schemas.schemas import (
    LicenseRecommendationIn, LicenseRecommendationOut, 
    LicenseRecommendation, OwnershipArrangementOut
)


# License database with compatibility and usage information
LICENSE_DATABASE = {
    "MIT": {
        "name": "MIT License",
        "type": "permissive",
        "commercial_use": True,
        "attribution_required": True,
        "copyleft": False,
        "patent_grant": False,
        "usage_terms": "Permits commercial use, modification, distribution, and private use. Requires attribution.",
        "obligations": [
            "Include original license text",
            "Include copyright notice",
            "Provide attribution to original authors"
        ],
        "compatible_with": ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "GPL-3.0", "LGPL-3.0"],
        "good_for": ["software", "libraries", "commercial_products"]
    },
    
    "Apache-2.0": {
        "name": "Apache License 2.0",
        "type": "permissive",
        "commercial_use": True,
        "attribution_required": True,
        "copyleft": False,
        "patent_grant": True,
        "usage_terms": "Permits commercial use with explicit patent grant. Requires attribution and notice of changes.",
        "obligations": [
            "Include original license text",
            "Include copyright notice",
            "State significant changes made",
            "Include NOTICE file if present"
        ],
        "compatible_with": ["Apache-2.0", "MIT", "BSD-3-Clause", "BSD-2-Clause", "GPL-3.0"],
        "good_for": ["software", "enterprise_software", "patent_sensitive_projects"]
    },
    
    "GPL-3.0": {
        "name": "GNU General Public License v3.0",
        "type": "copyleft",
        "commercial_use": True,
        "attribution_required": True,
        "copyleft": True,
        "patent_grant": True,
        "usage_terms": "Requires derivative works to be licensed under GPL-3.0. Provides strong copyleft protection.",
        "obligations": [
            "Include original license text",
            "Include copyright notice",
            "License derivative works under GPL-3.0",
            "Provide source code for distributed binaries",
            "Include installation instructions for user products"
        ],
        "compatible_with": ["GPL-3.0", "LGPL-3.0", "AGPL-3.0"],
        "good_for": ["open_source_projects", "community_software", "anti_proprietary_use"]
    },
    
    "LGPL-3.0": {
        "name": "GNU Lesser General Public License v3.0",
        "type": "weak_copyleft",
        "commercial_use": True,
        "attribution_required": True,
        "copyleft": True,
        "patent_grant": True,
        "usage_terms": "Allows linking with proprietary software. Modifications to LGPL code must remain LGPL.",
        "obligations": [
            "Include original license text",
            "Include copyright notice",
            "License modifications under LGPL-3.0",
            "Allow relinking with modified LGPL components"
        ],
        "compatible_with": ["LGPL-3.0", "GPL-3.0", "AGPL-3.0"],
        "good_for": ["libraries", "shared_components", "commercial_integration"]
    },
    
    "BSD-3-Clause": {
        "name": "BSD 3-Clause License",
        "type": "permissive",
        "commercial_use": True,
        "attribution_required": True,
        "copyleft": False,
        "patent_grant": False,
        "usage_terms": "Permits commercial use with attribution. Includes non-endorsement clause.",
        "obligations": [
            "Include original license text",
            "Include copyright notice",
            "Do not use author names for endorsement without permission"
        ],
        "compatible_with": ["BSD-3-Clause", "MIT", "Apache-2.0", "GPL-3.0", "LGPL-3.0"],
        "good_for": ["software", "academic_projects", "corporate_use"]
    },
    
    "CC-BY-4.0": {
        "name": "Creative Commons Attribution 4.0",
        "type": "permissive",
        "commercial_use": True,
        "attribution_required": True,
        "copyleft": False,
        "patent_grant": False,
        "usage_terms": "Permits any use including commercial with attribution. Designed for creative works.",
        "obligations": [
            "Provide attribution to original creator",
            "Include license notice",
            "Indicate if changes were made"
        ],
        "compatible_with": ["CC-BY-4.0", "CC-BY-SA-4.0"],
        "good_for": ["datasets", "documentation", "media", "research_data"]
    },
    
    "CC-BY-SA-4.0": {
        "name": "Creative Commons Attribution-ShareAlike 4.0",
        "type": "copyleft",
        "commercial_use": True,
        "attribution_required": True,
        "copyleft": True,
        "patent_grant": False,
        "usage_terms": "Requires derivative works to be licensed under same license. Good for collaborative content.",
        "obligations": [
            "Provide attribution to original creator",
            "Include license notice",
            "License derivative works under CC-BY-SA-4.0",
            "Indicate if changes were made"
        ],
        "compatible_with": ["CC-BY-SA-4.0", "GPL-3.0"],
        "good_for": ["datasets", "documentation", "collaborative_content", "wikis"]
    },
    
    "Proprietary": {
        "name": "Proprietary License",
        "type": "proprietary",
        "commercial_use": True,
        "attribution_required": False,
        "copyleft": False,
        "patent_grant": False,
        "usage_terms": "All rights reserved. Usage requires explicit permission or commercial license.",
        "obligations": [
            "Respect copyright restrictions",
            "Obtain proper licensing for use",
            "Comply with terms of use agreements"
        ],
        "compatible_with": ["Proprietary"],
        "good_for": ["commercial_software", "trade_secrets", "exclusive_products"]
    }
}


def analyze_ownership_structure(ownership_arrangement: OwnershipArrangementOut) -> Dict[str, Any]:
    """Analyze ownership structure to inform license recommendations"""
    
    analysis = {
        "single_owner": len(ownership_arrangement.ownership_table) == 1,
        "majority_owner": False,
        "distributed_ownership": True,
        "commercial_focus": False,
        "open_source_friendly": True
    }
    
    if ownership_arrangement.ownership_table:
        max_ownership = max(share.percentage for share in ownership_arrangement.ownership_table)
        analysis["majority_owner"] = max_ownership >= 50
        analysis["distributed_ownership"] = max_ownership < 75
        
        # Check governance rights for commercial indicators
        governance_types = [share.governance_rights for share in ownership_arrangement.ownership_table]
        analysis["commercial_focus"] = any(
            "investor" in rights or "majority" in rights 
            for rights in governance_types
        )
    
    return analysis


def check_dependency_compatibility(dependencies: List[str], candidate_license: str) -> Tuple[bool, List[str]]:
    """Check if candidate license is compatible with dependencies"""
    
    if not dependencies:
        return True, []
    
    issues = []
    candidate_info = LICENSE_DATABASE.get(candidate_license, {})
    compatible_licenses = candidate_info.get("compatible_with", [])
    
    for dep_license in dependencies:
        if dep_license not in compatible_licenses:
            # Check for specific incompatibility issues
            dep_info = LICENSE_DATABASE.get(dep_license, {})
            
            if dep_info.get("copyleft") and not candidate_info.get("copyleft"):
                issues.append(f"Copyleft dependency {dep_license} incompatible with permissive {candidate_license}")
            elif candidate_info.get("copyleft") and dep_info.get("type") == "proprietary":
                issues.append(f"Copyleft {candidate_license} incompatible with proprietary dependency {dep_license}")
            else:
                issues.append(f"License incompatibility: {dep_license} -> {candidate_license}")
    
    return len(issues) == 0, issues


def calculate_license_score(
    license_key: str, 
    asset_type: str, 
    intended_use: str, 
    ownership_analysis: Dict[str, Any],
    dependencies: List[str]
) -> Tuple[float, str]:
    """Calculate compatibility score for a license option"""
    
    license_info = LICENSE_DATABASE[license_key]
    score = 0.0
    rationale_parts = []
    
    # Asset type compatibility (30% of score)
    asset_score = 0.0
    if asset_type in license_info.get("good_for", []):
        asset_score = 1.0
        rationale_parts.append(f"Excellent fit for {asset_type}")
    elif asset_type == "software" and license_info["type"] in ["permissive", "copyleft"]:
        asset_score = 0.8
        rationale_parts.append(f"Good fit for {asset_type}")
    elif asset_type in ["dataset", "media"] and "CC-" in license_key:
        asset_score = 0.9
        rationale_parts.append(f"Well-suited for {asset_type}")
    else:
        asset_score = 0.3
        rationale_parts.append(f"Basic compatibility with {asset_type}")
    
    score += asset_score * 0.3
    
    # Intended use compatibility (25% of score)
    use_score = 0.0
    if intended_use == "commercial" and license_info["commercial_use"]:
        use_score = 1.0
        rationale_parts.append("Supports commercial use")
    elif intended_use == "open_source" and license_info["type"] in ["permissive", "copyleft"]:
        use_score = 1.0
        rationale_parts.append("Ideal for open source")
    elif intended_use == "research" and license_info["type"] == "permissive":
        use_score = 0.9
        rationale_parts.append("Great for research")
    else:
        use_score = 0.5
        rationale_parts.append(f"Moderate fit for {intended_use}")
    
    score += use_score * 0.25
    
    # Ownership structure compatibility (20% of score)
    ownership_score = 0.0
    if ownership_analysis["single_owner"] and license_info["type"] == "proprietary":
        ownership_score = 0.9
        rationale_parts.append("Single owner enables proprietary licensing")
    elif ownership_analysis["distributed_ownership"] and license_info["type"] in ["permissive", "copyleft"]:
        ownership_score = 0.8
        rationale_parts.append("Distributed ownership favors open licensing")
    elif ownership_analysis["commercial_focus"] and license_info["commercial_use"]:
        ownership_score = 0.7
        rationale_parts.append("Commercial focus supported")
    else:
        ownership_score = 0.5
    
    score += ownership_score * 0.2
    
    # Dependency compatibility (25% of score)
    is_compatible, compatibility_issues = check_dependency_compatibility(dependencies, license_key)
    if is_compatible:
        dependency_score = 1.0
        rationale_parts.append("Compatible with all dependencies")
    elif not dependencies:
        dependency_score = 1.0
        rationale_parts.append("No dependency constraints")
    else:
        dependency_score = 0.2
        rationale_parts.append(f"Compatibility issues: {len(compatibility_issues)} conflicts")
    
    score += dependency_score * 0.25
    
    # Ensure score is between 0 and 1
    score = max(0.0, min(1.0, score))
    
    rationale = "; ".join(rationale_parts)
    return score, rationale


def generate_license_recommendations(payload: LicenseRecommendationIn) -> LicenseRecommendationOut:
    """
    Generate license recommendations based on asset and ownership characteristics
    
    Args:
        payload: LicenseRecommendationIn with asset and ownership information
        
    Returns:
        LicenseRecommendationOut with ranked license recommendations
    """
    
    # Analyze ownership structure
    ownership_analysis = analyze_ownership_structure(payload.ownership_arrangement)
    
    # Calculate scores for all licenses
    license_scores = []
    compatibility_issues = []
    
    for license_key, license_info in LICENSE_DATABASE.items():
        score, rationale = calculate_license_score(
            license_key,
            payload.asset_type,
            payload.intended_use,
            ownership_analysis,
            payload.dependencies
        )
        
        # Check dependency compatibility for issues
        is_compatible, issues = check_dependency_compatibility(payload.dependencies, license_key)
        if not is_compatible:
            compatibility_issues.extend(issues)
        
        license_recommendation = LicenseRecommendation(
            license_name=license_info["name"],
            compatibility_score=score,
            rationale=rationale,
            usage_terms=license_info["usage_terms"],
            obligations=license_info["obligations"]
        )
        
        license_scores.append((score, license_recommendation))
    
    # Sort by score (highest first)
    license_scores.sort(key=lambda x: x[0], reverse=True)
    
    # Extract recommendations
    recommended_licenses = [rec for score, rec in license_scores]
    primary_recommendation = recommended_licenses[0] if recommended_licenses else None
    
    # Remove duplicate compatibility issues
    unique_issues = list(set(compatibility_issues))
    
    return LicenseRecommendationOut(
        asset_id=payload.asset_id,
        recommended_licenses=recommended_licenses,
        primary_recommendation=primary_recommendation,
        compatibility_issues=unique_issues
    )


def run_license_recommendation(payload: LicenseRecommendationIn) -> LicenseRecommendationOut:
    """Main function for license recommendation service"""
    return generate_license_recommendations(payload)
