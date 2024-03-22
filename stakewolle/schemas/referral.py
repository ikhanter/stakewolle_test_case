from pydantic import BaseModel, AwareDatetime


class ReferralSchema(BaseModel):
    referral: str
    expires_at: AwareDatetime
