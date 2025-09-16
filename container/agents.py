from interfaces.agents.agent_interface import IAgent
from container.clients import ClientContainer
from container.repositories import RepositoryContainer
import agents
import pkgutil
import importlib


class AgentContainer:

    def __init__(self, clients: ClientContainer, repositories: RepositoryContainer):
        self._clients = clients
        self._repositories = repositories
        self._agents: list[IAgent] = []
        self._register_agents()

    def _register_agents(self):
        agents_id: list[str] = []

        for _, module_name, _ in pkgutil.iter_modules(agents.__path__):
            module = importlib.import_module(f"agents.{module_name}")
            for attr in dir(module):
                obj = getattr(module, attr)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, IAgent)
                    and hasattr(obj, "factory")
                ):
                    agent = obj.factory(
                        client_container=self._clients,
                        repository_container=self._repositories,
                    )

                    if agent:
                        if agent.id in agents_id:
                            raise ValueError(f"Duplicate agent ID found: {agent.id}")

                        agents_id.append(agent.id)
                        self._agents.append(agent)

    def get(self, id: str) -> IAgent | None:
        return next((agent for agent in self._agents if agent.id == id), None)

    def all(self) -> list[IAgent]:
        return self._agents
