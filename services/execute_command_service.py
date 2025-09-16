class ExecuteCommandService:
    def __init__(self, message_repository, chat_client):
        self.message_repository = message_repository
        self.chat = chat_client

    def execute(self, phone, command, **kwargs):
        if not self.chat.is_valid_message(**kwargs):
            return
