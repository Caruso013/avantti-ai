import time
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime, timedelta
from container.container import Container
from os import getenv
from utils.logger import logger, to_json_dump

container = Container()


def get_abandoned_conversations() -> list:
    from_time = datetime.now() - timedelta(
        hours=int(getenv("ABANDONED_CONVERSATIONS_TIME_IN_HOURS", 5))
    )

    abandoned_conversations: list = (
        container.repositories.message.get_abandoned_conversation_numbers(
            until_time=from_time
        )
    )

    if not abandoned_conversations:
        return []

    abandoned_conversations_checked = [
        phone
        for phone in abandoned_conversations
        if container.repositories.abandoned_conversation.is_not_abandoned_conversation(
            phone
        )
    ]

    return abandoned_conversations_checked


def get_context(phone: str) -> list[dict]:

    context = container.repositories.message.get_latest_customer_messages(
        phone=phone, limit=999
    )
    context_resolved = []

    # Trata os casos do contexto simples do usuário e do assistente e das chamadas e saídas das tools
    for message in context[::-1]:
        role = message.get("role", "")
        content = message.get("content", "")

        if role in ["user", "assistant"]:
            context_resolved.append({"role": role, "content": content})
            continue

        context_resolved.append(content)

    context = context_resolved

    context.append(
        {
            "role": "user",
            "content": "Já se passaram mais de 5 horas sem uma resposta do usuário. Por favor, crie uma mensagem de conversa abandonada que será enviada ao usuário.",
        }
    ),

    return context


def save_messages_to_database(phone: str, input: dict, output: list[dict]) -> None:
    logger.info(
        f"[GENERATE RESPONSE SERVICE] Salvando mensagens no banco de dados para o telefone: {phone} \nInput: {to_json_dump(input)} Output: \n{to_json_dump(output)}"
    )

    # Salva a nova mensagem do usuário
    container.repositories.message.create(
        phone=phone,
        role=input.get("role"),
        content=input.get("content"),
    )

    if not output:
        logger.warning(
            f"[GENERATE RESPONSE SERVICE] A resposta gerada está vazia para o telefone {phone}. Input: \n{to_json_dump(input)}"
        )
        return

    # Salva a resposta gerada pela IA
    container.repositories.message.create(
        phone=phone,
        role=output.get("role"),
        content=output.get("content"),
    )

    logger.info(
        f"[GENERATE RESPONSE SERVICE] Mensagens salvas no banco de dados para o telefone: {phone}. Input: \n{to_json_dump(input)}, output: \n{to_json_dump(output)}"
    )


def main():
    phones = get_abandoned_conversations()

    if not phones:
        logger.info(
            "[ABANDONED CONVERSATION TASK] No abandoned conversations to process."
        )
        exit()

    for phone in phones:
        context: list = get_context(phone)
        response = container.clients.ai.create_model_response(
            model="gpt-4.1",
            input=context,
            instructions="Crie uma mensagem de conversa abandonada para o usuário. Responda somente com o texto bruto, sem nenhuma explicação ou contexto adicional. A mensagem deve ser amigável e convidativa, incentivando o usuário a retomar a conversa.",
        )
        output = {
            "role": "assistant",
            "content": ". ".join(
                [
                    o.get("text", "")
                    for message in response.get("output", [])
                    if message.get("status", "") == "completed"
                    for o in message.get("content", [])
                    if o.get("type") == "output_text"
                ]
            ),
        }

        logger.info(
            f"[ABANDONED CONVERSATION TASK] Resposta gerada para o telefone {phone}: {to_json_dump(output)}"
        )

        container.clients.chat.send_message(
            phone=phone,
            message=output.get("content"),
        )

        save_messages_to_database(phone, context[-1], output)

        container.repositories.abandoned_conversation.mark_as_abandoned_conversation(
            phone=phone
        )

    time.sleep(10)


if __name__ == "__main__":
    main()
