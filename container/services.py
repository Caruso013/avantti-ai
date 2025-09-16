from services.generate_response_service import GenerateResponseService
from services.message_queue_service import MessageQueueService
from container.clients import ClientContainer
from container.repositories import RepositoryContainer
from services.audio_transcription_service import AudioTranscriptionService
from services.unsupported_media_handler_service import UnsupportedMediaHandlerService
from services.response_orchestrator_service import ResponseOrchestratorService
from container.agents import AgentContainer
from container.tools import ToolContainer


class ServiceContainer:

    def __init__(
        self,
        clients: ClientContainer,
        repositories: RepositoryContainer,
        agents: AgentContainer,
        tools: ToolContainer,
    ):
        self._clients = clients
        self._repositories = repositories
        self.agents = agents
        self.tools = tools

    @property
    def generate_response_service(self) -> GenerateResponseService:
        return GenerateResponseService(
            chat_client=self._clients.chat,
            message_repository=self._repositories.message,
            response_orchestrator=self.response_orchestrator_service,
        )

    @property
    def message_queue_service(self) -> MessageQueueService:
        return MessageQueueService(
            cache_client=self._clients.cache,
            chat_client=self._clients.chat,
            unsupported_media_handler=self.unsupported_media_handler_service,
            audio_transcription_service=self.audio_transcription_service,
            abandoned_message_repository=self._repositories.abandoned_conversation,
        )

    @property
    def audio_transcription_service(self) -> AudioTranscriptionService:
        return AudioTranscriptionService(
            chat_client=self._clients.chat,
            ai_client=self._clients.ai,
        )

    @property
    def unsupported_media_handler_service(self) -> UnsupportedMediaHandlerService:
        return UnsupportedMediaHandlerService(
            chat_client=self._clients.chat,
            database_client=self._clients.database,
        )

    @property
    def response_orchestrator_service(self):
        return ResponseOrchestratorService(
            agent_container=self.agents,
            tool_container=self.tools,
            chat_client=self._clients.chat,
            message_repository=self._repositories.message,
            ai_client=self._clients.ai,
        )
