from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from contacts.entities import ContactEntity


class CreateContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)


class UpdateContactRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)


class ContactResponse(BaseModel):
    data: ContactEntity


class ContactsListResponse(BaseModel):
    data: list[ContactEntity]
    total: int
    page: int
    page_size: int

