from abc import ABC, abstractmethod


class IAgent(ABC):

    def __init__(self, ai_client) -> None:
        self.ai = ai_client
        self.resolve_instructions()

    @property
    @abstractmethod
    def model(self) -> str: ...

    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def _keyword(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    def _base_instructions(self) -> str:
        return "Novamente, só indique os lugares que estão na sua instrução em 'Lugares que você deve indicar', nunca indique lugares que não estão em 'Lugares que você deve indicar'. Formate a resposta da seguinte forma: ✨ Cê quer saber (oque a pessoa busca)? Bora 👇🏼 🕍 (nome do lugar): (descrição do lugar) 📍Endereço: (endereço do lugar) ⏰ Horário de funcionamento: (horário de funcionamento) 📲 @ do local: (apenas se tiver o campo \"@ do local:\") 📝 Pedidos: (apenas se tiver o campo \"pedidos:\")  🎥 vídeo do local: (apenas se tiver url)"

    @property
    @abstractmethod
    def instructions(self) -> str: ...

    @property
    @abstractmethod
    def _items(self) -> str: ...

    @property
    @abstractmethod
    def tools(self) -> list: ...

    @staticmethod
    @abstractmethod
    def factory(client_container, repository_container) -> "IAgent": ...

    @abstractmethod
    async def execute(self, phone: str, context: list) -> list[dict]: ...

    def resolve_instructions(self) -> str:
        if not self.instructions or not self._keyword or not self._items:
            return

        self.instructions = self.instructions.replace(
            "[[keyword]]", self._keyword
        ).replace("[[items]]", self._items)
