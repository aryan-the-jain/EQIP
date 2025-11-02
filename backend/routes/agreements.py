from fastapi import APIRouter
from ..schemas.schemas import DraftAgreementIn, DraftAgreementOut
from ..agents import contract_composer

router = APIRouter(tags=["agreements"])

@router.post("/agreements/draft", response_model=DraftAgreementOut)
def draft_agreement(payload: DraftAgreementIn):
    return contract_composer.run(payload)
