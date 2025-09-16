from container.clients import ClientContainer
from container.services import ServiceContainer
from container.controllers import ControllerContainer
from container.repositories import RepositoryContainer
from container.agents import AgentContainer
from container.tools import ToolContainer


class Container:
    def __init__(self):
        self.clients = ClientContainer()
        self.repositories = RepositoryContainer(clients=self.clients)
        self.agents = AgentContainer(
            clients=self.clients, repositories=self.repositories
        )
        self.tools = ToolContainer(clients=self.clients, repositories=self.repositories)
        self.services = ServiceContainer(
            clients=self.clients,
            repositories=self.repositories,
            agents=self.agents,
            tools=self.tools,
        )
        self.controllers = ControllerContainer(services=self.services)
