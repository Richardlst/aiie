from pydantic import BaseModel


class GoogleUserProfile(BaseModel):
    id: str
    email: str
    verified_email: bool
    name: str
    given_name: str
    family_name: str
    picture: str


class GoogleCallbackData(BaseModel):
    access_token: str
