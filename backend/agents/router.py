# Minimal "StrAND-like" planner stub.
from typing import Literal
from ..schemas.schemas import IPOptionsIn, IPOptionsOut, AllocationIn, AllocationOut

def plan_ip_options(_: IPOptionsIn) -> list[Literal["rag","rules","license_scan","disclosure_check"]]:
    return ["rag", "rules", "license_scan", "disclosure_check"]

def plan_allocation(_: AllocationIn) -> list[Literal["weigh","simulate","vote"]]:
    return ["weigh", "simulate"]
