import os
from clients.zapi_client import ZAPIClient
from clients.evolution_api_client import EvolutionAPIClient
from clients.openai_client import OpenIAClient
from clients.supabase_client import SupabaseClient
from clients.redis_client import RedisClient
from clients.pipedrive_client import PipeDriveClient


class ClientContainer:
    @property
    def chat(self) -> ZAPIClient:
        if os.getenv("APP_ENV") == "stage":
            return EvolutionAPIClient()

        return ZAPIClient()

    @property
    def ai(self) -> OpenIAClient:
        return OpenIAClient()

    @property
    def database(self) -> SupabaseClient:
        return SupabaseClient(ai_client=self.ai)

    @property
    def cache(self) -> RedisClient:
        return RedisClient()

    @property
    def crm(self) -> PipeDriveClient:
        # Mantido para compatibilidade, mas desabilitado
        return PipeDriveClient()

    @property
    def evolution(self) -> EvolutionAPIClient:
        return EvolutionAPIClient()
