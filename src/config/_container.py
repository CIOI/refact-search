from dependency_injector import containers
from dependency_injector.containers import WiringConfiguration
from dependency_injector.providers import Dependency

from ._environment import Environment


class Application(containers.DeclarativeContainer):
    wiring_config = WiringConfiguration(
        auto_wire=False,
        modules=[
            "preprocessing",
        ],
    )
    environment = Dependency(
        Environment,
        default=Environment.from_env_file(),
    )
