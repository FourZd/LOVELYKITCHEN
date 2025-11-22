from dishka import Provider, Scope, provide
from core.environment.config import Settings


class EnvironmentProvider(Provider):
    scope = Scope.APP
    component = "environment"

    @provide
    def get_settings(self) -> Settings:
        return Settings()

