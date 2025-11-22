from typing import Annotated
from dishka import Provider, Scope, provide, FromComponent

from contacts.repositories import ContactRepository
from contacts.usecases import (
    CreateContactUseCase,
    GetContactUseCase,
    UpdateContactUseCase,
    DeleteContactUseCase,
    ListContactsUseCase,
)
from core.database.unit_of_work import UnitOfWork


class ContactProvider(Provider):
    scope = Scope.REQUEST
    component = "contacts"

    @provide
    def get_contact_repository(
        self, uow: Annotated[UnitOfWork, FromComponent("database")]
    ) -> ContactRepository:
        return ContactRepository(uow.session)

    @provide
    def get_create_contact_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        contact_repository: Annotated[ContactRepository, FromComponent("contacts")],
    ) -> CreateContactUseCase:
        return CreateContactUseCase(uow, contact_repository)

    @provide
    def get_get_contact_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        contact_repository: Annotated[ContactRepository, FromComponent("contacts")],
    ) -> GetContactUseCase:
        return GetContactUseCase(uow, contact_repository)

    @provide
    def get_update_contact_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        contact_repository: Annotated[ContactRepository, FromComponent("contacts")],
    ) -> UpdateContactUseCase:
        return UpdateContactUseCase(uow, contact_repository)

    @provide
    def get_delete_contact_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        contact_repository: Annotated[ContactRepository, FromComponent("contacts")],
    ) -> DeleteContactUseCase:
        return DeleteContactUseCase(uow, contact_repository)

    @provide
    def get_list_contacts_usecase(
        self,
        uow: Annotated[UnitOfWork, FromComponent("database")],
        contact_repository: Annotated[ContactRepository, FromComponent("contacts")],
    ) -> ListContactsUseCase:
        return ListContactsUseCase(uow, contact_repository)

