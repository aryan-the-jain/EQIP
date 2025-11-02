import yaml
from ..schemas.schemas import AllocationIn, AllocationOut

def run(payload: AllocationIn) -> AllocationOut:
    # toy simulation: equal split among 3 hypothetical contributors if not specified
    try:
        policy = yaml.safe_load(payload.policy_yaml) if payload.policy_yaml else {}
    except Exception:
        policy = {}
    n = policy.get("assume_contributors", 3)
    share = round(100.0 / n, 2)
    shares = [{"contributor": f"user{i+1}", "pct": share} for i in range(n)]
    return AllocationOut(shares=shares, warnings=[])
