from dependency_injector.containers import (
    DeclarativeContainer,
    WiringConfiguration,
)
from dependency_injector.providers import (
    Singleton,
    Callable,
    Dependency,
)
from ._environment import Environment
from ._logger import LoggerService, get_logger
from src.managers import TypesenseManager
from src.services import SearchService
from src.controllers import SearchController


class Application(DeclarativeContainer):
    wiring_config = WiringConfiguration(
        auto_wire=False,
        modules=[
            "preprocessing",
        ],
    )
    environment: Dependency[Environment] = Dependency(
        Environment,
        default=Environment.from_env_file(),
    )
    logger: Callable[LoggerService] = Callable(
        get_logger,
        environment=environment,
    )
    typesense_manager: Singleton[TypesenseManager] = Singleton(
        TypesenseManager,
        environment=environment,
        logger=logger,
    )
    search_service: Singleton[SearchService] = Singleton(
        SearchService,
        typesense_manager=typesense_manager,
        logger=logger,
    )
    search_controller: Singleton[SearchController] = Singleton(
        SearchController,
        search_service=search_service,
        logger=logger,
    )
