from ..schemas.schemas import DraftAgreementIn, DraftAgreementOut

def run(payload: DraftAgreementIn) -> DraftAgreementOut:
    # toy: returns a fake agreement id and s3 uri
    return DraftAgreementOut(agreement_id=1, s3_uri="s3://eqip/drafts/example.pdf", sign_url=None)
