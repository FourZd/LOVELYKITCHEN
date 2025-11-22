from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider

from core.database.providers import DatabaseConnectionProvider, DatabaseSessionProvider
from core.environment.providers import EnvironmentProvider
from auth.providers import AuthProvider
from users.providers import UserProvider
from organizations.providers import OrganizationProvider
from contacts.providers import ContactProvider
from deals.providers import DealProvider
from tasks.providers import TaskProvider
from activities.providers import ActivityProvider
from analytics.providers import AnalyticsProvider


container = make_async_container(
    FastapiProvider(),
    DatabaseConnectionProvider(),
    DatabaseSessionProvider(),
    EnvironmentProvider(),
    AuthProvider(),
    UserProvider(),
    OrganizationProvider(),
    ContactProvider(),
    DealProvider(),
    TaskProvider(),
    ActivityProvider(),
    AnalyticsProvider(),
)

