from typing import Annotated, Optional
from fastapi import APIRouter, Query
from uuid import UUID
from dishka.integrations.fastapi import inject
from dishka import FromComponent

from contacts.schemas import (
    CreateContactRequest,
    UpdateContactRequest,
    ContactResponse,
    ContactsListResponse,
)
from contacts.usecases import (
    CreateContactUseCase,
    GetContactUseCase,
    UpdateContactUseCase,
    DeleteContactUseCase,
    ListContactsUseCase,
)
from auth.entities import AuthenticatedUser


router = APIRouter(
    prefix="/api/v1/contacts",
    tags=["contacts"],
)


@router.get("", response_model=ContactsListResponse)
@inject
async def list_contacts(
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    list_usecase: Annotated[ListContactsUseCase, FromComponent("contacts")],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    owner_id: Optional[UUID] = None,
):
    contacts, total = await list_usecase(user, page, page_size, search, owner_id)
    return ContactsListResponse(data=contacts, total=total, page=page, page_size=page_size)


@router.post("", response_model=ContactResponse)
@inject
async def create_contact(
    request: CreateContactRequest,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    create_usecase: Annotated[CreateContactUseCase, FromComponent("contacts")],
):
    contact = await create_usecase(user, request.name, request.email, request.phone)
    return ContactResponse(data=contact)


@router.get("/{contact_id}", response_model=ContactResponse)
@inject
async def get_contact(
    contact_id: UUID,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    get_usecase: Annotated[GetContactUseCase, FromComponent("contacts")],
):
    contact = await get_usecase(user, contact_id)
    return ContactResponse(data=contact)


@router.patch("/{contact_id}", response_model=ContactResponse)
@inject
async def update_contact(
    contact_id: UUID,
    request: UpdateContactRequest,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    update_usecase: Annotated[UpdateContactUseCase, FromComponent("contacts")],
):
    update_data = request.model_dump(exclude_unset=True)
    contact = await update_usecase(user, contact_id, update_data)
    return ContactResponse(data=contact)


@router.delete("/{contact_id}", status_code=204)
@inject
async def delete_contact(
    contact_id: UUID,
    user: Annotated[AuthenticatedUser, FromComponent("auth")],
    delete_usecase: Annotated[DeleteContactUseCase, FromComponent("contacts")],
):
    await delete_usecase(user, contact_id)

