from interfaces.tools.tool_interface import ITool
from container.clients import ClientContainer
from container.repositories import RepositoryContainer
from tools.crm_tool import CRMTool
from tools.notificar_novo_lead_tool import NotificarNovoLeadTool


class ToolContainer:
    def __init__(self, clients: ClientContainer, repositories: RepositoryContainer):
        self._clients = clients
        self._repositories = repositories
        self._tools: dict[str, ITool] = {}
        self._register_tools()

    def _register_tools(self):
        self._tools = {
            "crm": CRMTool(
                ai_client=self._clients.ai,
                database_client=self._clients.database,
                chat_client=self._clients.evolution,
            ),
            "notificar_novo_lead": NotificarNovoLeadTool(
                ai_client=self._clients.ai,
                chat_client=self._clients.evolution,
            ),
        }

    def get(self, name: str) -> ITool:
        return self._tools[name]

    def all(self) -> list[ITool]:
        return list(self._tools.values())
