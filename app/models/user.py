from typing import Optional
from passlib.context import CryptContext
from .rwmodel import RWModel


class User(RWModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = None


class UserInDB(User):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password: str

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)
