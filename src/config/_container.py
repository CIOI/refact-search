from dependency_injector.containers import (
    DeclarativeContainer,
    WiringConfiguration,
)
from dependency_injector.providers import (
    Singleton,
    Callable,
    Dependency,
    Container,
)
from ._environment import Environment
from ._logger import LoggerService, get_logger
from src.managers import TypesenseManager, QdrantManager
from src.services import SearchService
from src.controllers import SearchController


class ManagersContainer(DeclarativeContainer):
    logger: Dependency[LoggerService] = Dependency(LoggerService)
    environment: Dependency[Environment] = Dependency(Environment)

    qdrant_manager: Singleton[QdrantManager] = Singleton(
        QdrantManager,
        environment=environment,
        logger=logger,
    )
    typesense_manager: Singleton[TypesenseManager] = Singleton(
        TypesenseManager,
        logger=logger,
        environment=environment,
    )


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
    managers: Container[ManagersContainer] = Container(
        ManagersContainer,
        logger=logger,
        environment=environment,
    )
    search_service: Singleton[SearchService] = Singleton(
        SearchService,
        typesense_manager=managers.typesense_manager,
        logger=logger,
    )
    search_controller: Singleton[SearchController] = Singleton(
        SearchController,
        search_service=search_service,
        logger=logger,
    )
