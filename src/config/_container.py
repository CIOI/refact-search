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
from src.services import TypesenseService, QdrantService
from src.controllers import TypesenseController, QdrantController
from src.embedding.clip import ClipEmbeddingModel
from src.embedding.schma import fashion_clip


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


class ServicesContainer(DeclarativeContainer):
    logger: Dependency[LoggerService] = Dependency(LoggerService)
    environment: Dependency[Environment] = Dependency(Environment)
    managers: Container[ManagersContainer] = Container(ManagersContainer)
    embedding_model: Dependency[ClipEmbeddingModel] = Dependency(ClipEmbeddingModel)

    typesense_service: Singleton[TypesenseService] = Singleton(
        TypesenseService,
        logger=logger,
        typesense_manager=managers.typesense_manager,
    )
    qdrant_service: Singleton[QdrantService] = Singleton(
        QdrantService,
        logger=logger,
        qdrant_manager=managers.qdrant_manager,
        embedding_model=embedding_model,
    )


class ControllersContainer(DeclarativeContainer):
    logger: Dependency[LoggerService] = Dependency(LoggerService)
    services: Container[ServicesContainer] = Container(ServicesContainer)
    typesense_controller: Singleton[TypesenseController] = Singleton(
        TypesenseController,
        service=services.typesense_service,
        logger=logger,
    )
    qdrant_controller: Singleton[QdrantController] = Singleton(
        QdrantController,
        service=services.qdrant_service,
        logger=logger,
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
    embedding_model: Singleton[ClipEmbeddingModel] = Singleton(
        ClipEmbeddingModel,
        clip_model=fashion_clip,
        logger=logger,
    )
    managers: Container[ManagersContainer] = Container(
        ManagersContainer,
        logger=logger,
        environment=environment,
    )
    services: Container[ServicesContainer] = Container(
        ServicesContainer,
        logger=logger,
        environment=environment,
        managers=managers,
        embedding_model=embedding_model,
    )
    controllers: Container[ControllersContainer] = Container(
        ControllersContainer,
        logger=logger,
        services=services,
    )
