from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
