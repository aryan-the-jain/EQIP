from fastapi import APIRouter
from ..schemas.schemas import (
    IPOptionsIn, IPOptionsOut, AllocationIn, AllocationOut,
    ContributionAttributionIn, ContributionAttributionOut,
    OwnershipArrangementIn, OwnershipArrangementOut,
    ContractGenerationIn, ContractGenerationOut,
    LicenseRecommendationIn, LicenseRecommendationOut
)
from ..agents import router as planner
from ..agents import ip_path_finder, allocation, contribution_attribution, ownership_arrangement, contract_drafting
from ..services import license_generator

router = APIRouter(tags=["agents"])

@router.post("/agents/ip-options", response_model=IPOptionsOut)
def ip_options(payload: IPOptionsIn):
    _ = planner.plan_ip_options(payload)
    return ip_path_finder.run(payload)

@router.post("/agents/allocation/simulate", response_model=AllocationOut)
def allocation_sim(payload: AllocationIn):
    _ = planner.plan_allocation(payload)
    return allocation.run(payload)

@router.post("/agents/attribution/run", response_model=ContributionAttributionOut)
def contribution_attribution_analysis(payload: ContributionAttributionIn):
    """Analyze contributor efforts and calculate weighted attribution"""
    return contribution_attribution.run(payload)

@router.post("/agents/allocation/finalize", response_model=OwnershipArrangementOut)
def finalize_ownership_arrangement(payload: OwnershipArrangementIn):
    """Finalize ownership arrangement based on attribution and policy"""
    return ownership_arrangement.run_ownership_arrangement(payload)

@router.post("/agreements/generate", response_model=ContractGenerationOut)
def generate_contract(payload: ContractGenerationIn):
    """Generate legal contract based on ownership arrangement"""
    return contract_drafting.run_contract_generation(payload)

@router.post("/license/recommend", response_model=LicenseRecommendationOut)
def recommend_license(payload: LicenseRecommendationIn):
    """Recommend appropriate license based on asset and ownership characteristics"""
    return license_generator.run_license_recommendation(payload)
