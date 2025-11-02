#!/usr/bin/env python3
"""
Test script for the complete Eqip.ai IP pipeline

Tests the end-to-end flow with dummy data to verify all integrations work.
"""

import asyncio
import json
from datetime import datetime
from backend.agents import contribution_attribution, ownership_arrangement, contract_drafting
from backend.services import license_generator
from backend.schemas.schemas import (
    ContributorIn, ContributionEvent, ContributionAttributionIn,
    OwnershipArrangementIn, ContractGenerationIn, LicenseRecommendationIn
)

def create_dummy_data():
    """Create dummy data for testing"""
    
    # Contributors
    contributors = [
        ContributorIn(email="alice@example.com", display_name="Alice Smith", org="TechCorp"),
        ContributorIn(email="bob@example.com", display_name="Bob Johnson", org="DevStudio"),
        ContributorIn(email="carol@example.com", display_name="Carol Davis", org="TechCorp")
    ]
    
    # Contribution events
    events = [
        ContributionEvent(
            contributor_email="alice@example.com",
            event_type="code",
            lines_of_code=1500,
            hours_spent=40.0,
            complexity_score=2.0,
            description="Core algorithm implementation"
        ),
        ContributionEvent(
            contributor_email="bob@example.com",
            event_type="design",
            lines_of_code=0,
            hours_spent=25.0,
            complexity_score=1.5,
            description="UI/UX design and architecture"
        ),
        ContributionEvent(
            contributor_email="carol@example.com",
            event_type="code",
            lines_of_code=800,
            hours_spent=20.0,
            complexity_score=1.0,
            description="Testing and documentation"
        ),
        ContributionEvent(
            contributor_email="alice@example.com",
            event_type="review",
            lines_of_code=0,
            hours_spent=10.0,
            complexity_score=1.0,
            description="Code reviews and quality assurance"
        )
    ]
    
    return contributors, events

async def test_pipeline():
    """Test the complete pipeline"""
    
    print("🚀 Testing Eqip.ai Complete IP Pipeline")
    print("=" * 50)
    
    # Create dummy data
    contributors, events = create_dummy_data()
    asset_id = 12345
    
    print(f"📊 Testing with {len(contributors)} contributors and {len(events)} contribution events")
    
    # Stage 1: Contribution Attribution
    print("\n1️⃣ Testing Contribution Attribution...")
    
    attribution_payload = ContributionAttributionIn(
        asset_id=asset_id,
        contributors=contributors,
        contribution_events=events,
        mode="hybrid"
    )
    
    try:
        attribution_result = contribution_attribution.run(attribution_payload)
        print(f"✅ Attribution analysis complete")
        print(f"   Methodology: {attribution_result.methodology}")
        print(f"   Confidence: {attribution_result.confidence_score:.1%}")
        
        for attr in attribution_result.attributions:
            print(f"   • {attr.contributor_name}: {attr.weight:.1%}")
    
    except Exception as e:
        print(f"❌ Attribution failed: {str(e)}")
        return False
    
    # Stage 2: Ownership Arrangement
    print("\n2️⃣ Testing Ownership Arrangement...")
    
    ownership_payload = OwnershipArrangementIn(
        asset_id=asset_id,
        attribution_weights=attribution_result.attributions,
        policy_type="weighted",
        policy_params={"total_shares": 1000000}
    )
    
    try:
        ownership_result = ownership_arrangement.run_ownership_arrangement(ownership_payload)
        print(f"✅ Ownership arrangement complete")
        print(f"   Policy: {ownership_result.policy_applied}")
        print(f"   Total shares: {ownership_result.total_shares:,}")
        
        for share in ownership_result.ownership_table:
            print(f"   • {share.contributor_name}: {share.percentage:.2f}% ({share.shares:,} shares)")
    
    except Exception as e:
        print(f"❌ Ownership arrangement failed: {str(e)}")
        return False
    
    # Stage 3: Contract Generation
    print("\n3️⃣ Testing Contract Generation...")
    
    contract_types = ["nda", "ip_assignment", "jda", "revenue_share"]
    generated_contracts = {}
    
    for contract_type in contract_types:
        contract_payload = ContractGenerationIn(
            asset_id=asset_id,
            contract_type=contract_type,
            ownership_arrangement=ownership_result,
            jurisdiction="US"
        )
        
        try:
            contract_result = contract_drafting.run_contract_generation(contract_payload)
            generated_contracts[contract_type] = contract_result
            print(f"   ✅ {contract_type.upper()} generated (ID: {contract_result.agreement_id[:8]}...)")
            print(f"      Clauses: {len(contract_result.clauses)}")
        
        except Exception as e:
            print(f"   ❌ {contract_type.upper()} generation failed: {str(e)}")
            return False
    
    # Stage 4: License Recommendation
    print("\n4️⃣ Testing License Recommendation...")
    
    license_payload = LicenseRecommendationIn(
        asset_id=asset_id,
        asset_type="software",
        ownership_arrangement=ownership_result,
        intended_use="commercial",
        dependencies=["MIT", "Apache-2.0"]
    )
    
    try:
        license_result = license_generator.run_license_recommendation(license_payload)
        print(f"✅ License recommendations generated")
        print(f"   Primary: {license_result.primary_recommendation.license_name}")
        print(f"   Score: {license_result.primary_recommendation.compatibility_score:.1%}")
        print(f"   Total options: {len(license_result.recommended_licenses)}")
        
        if license_result.compatibility_issues:
            print(f"   ⚠️  Compatibility issues: {len(license_result.compatibility_issues)}")
    
    except Exception as e:
        print(f"❌ License recommendation failed: {str(e)}")
        return False
    
    # Final Summary
    print("\n📋 Pipeline Summary")
    print("=" * 30)
    print(f"Asset ID: {asset_id}")
    print(f"Contributors: {len(contributors)}")
    print(f"Attribution Method: {attribution_result.methodology}")
    print(f"Ownership Policy: {ownership_result.policy_applied}")
    print(f"Contracts Generated: {len(generated_contracts)}")
    print(f"Primary License: {license_result.primary_recommendation.license_name}")
    
    # Export summary
    summary_data = {
        "asset_id": asset_id,
        "test_timestamp": datetime.now().isoformat(),
        "contributors": [c.dict() for c in contributors],
        "attribution_results": attribution_result.dict(),
        "ownership_arrangement": ownership_result.dict(),
        "contracts_generated": list(generated_contracts.keys()),
        "license_recommendation": license_result.primary_recommendation.dict(),
        "pipeline_status": "SUCCESS"
    }
    
    with open("test_pipeline_results.json", "w") as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\n💾 Test results saved to test_pipeline_results.json")
    print("\n🎉 All pipeline stages completed successfully!")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_pipeline())
    exit(0 if success else 1)
