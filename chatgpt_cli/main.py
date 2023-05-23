import os
import signal
import time
from dataclasses import dataclass
from enum import Enum

import openai
from rich import print
from rich.prompt import Confirm, Prompt

# disable CTRL+C
signal.signal(signal.SIGINT, lambda signum, frame: None)


def setup_openai_key() -> None:
    key_file_path = os.path.join(
        os.path.expanduser("~"), ".config/simple_chatgpt_cli/openai_api_key"
    )
    if os.getenv("OPENAI_API_KEY") is None and not os.path.exists(key_file_path):
        openai_api_key = Prompt.ask(
            "OpenAI API key not found. Press Enter it here to continue", password=True
        )
        openai.api_key = openai_api_key
        confirm_save_key = Confirm.ask(
            f"Do you want to save the key to {key_file_path} so you don't have to enter it again next time?",
            default=True,
        )
        if confirm_save_key:
            os.makedirs(os.path.dirname(key_file_path), exist_ok=True)
            with open(key_file_path, "w") as f:
                f.write(openai_api_key)
    elif os.getenv("OPENAI_API_KEY") is None and os.path.exists(key_file_path):
        with open(key_file_path, "r") as f:
            openai.api_key = f.read().strip()
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")


class Role(Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


@dataclass
class Message:
    role: Role
    content: str
    timestamp: int


class ChatExitReason(Enum):
    EXIT = "#exit"
    START_OVER = "#startover"


class AllowedModels(Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"


ALLOWED_MODELS = [model.value for model in AllowedModels]
WARNING_PREFIX = ":small_red_triangle:"
INFO_PREFIX = ":small_blue_diamond:"
BYE_PREFIX = ":wave:"
USER_DISPLAY_NAME = "[yellow3][b]You[/b][/yellow3] :smiley:"
BOT_DISPLAY_NAME = "[deep_sky_blue3][bold]Bot[/bold][/deep_sky_blue3] :robot:"
SYS_CONVERSATION_INITIATION_MESSAGE = Message(
    role=Role.SYSTEM,
    content="You are a helpful assistant. Answer as concisely as possible.",
    timestamp=int(time.time()),
)
CONVERSATION_SOFT_TIMEOUT_SECONDS = 300
TEMPERATURE = 0.5


def select_model() -> str:
    model = Prompt.ask(
        f"{INFO_PREFIX} Please select the model you want to use",
        default=AllowedModels.GPT_4.value,
        choices=ALLOWED_MODELS,
    )
    print(f"{INFO_PREFIX} You selected [bold cyan]{model}[/bold cyan].")
    return model


def request_user_input() -> str:
    user_input = Prompt.ask(USER_DISPLAY_NAME)

    if not user_input or user_input.isspace():
        return request_user_input()

    if user_input == ChatExitReason.EXIT.value:
        exit_confirm = Confirm.ask(
            f"{WARNING_PREFIX} Do you really want to exit?", default=True
        )
        if exit_confirm:
            return ChatExitReason.EXIT.value
        return request_user_input()

    if user_input == ChatExitReason.START_OVER.value:
        startover_confirm = Confirm.ask(
            f"{WARNING_PREFIX} A new conversation will lose all previous context. Do you really want to start a new conversation?",
            default=True,
        )
        if startover_confirm:
            return ChatExitReason.START_OVER.value
        return request_user_input()

    if user_input == "#multiline":
        print("Multiline mode enabled. Press CTRL+D to finish.")
        try:
            user_input = ""
            while True:
                user_input += input() + "\n"
        except EOFError:
            pass

    return user_input


def chat(
    model: str, has_previous_chat: bool, rollover_message: Message | None = None
) -> tuple[ChatExitReason, Message | None]:
    # welcome console message
    if not has_previous_chat:
        print(
            f"{INFO_PREFIX} You can now start chatting with the bot. \n"
            f"Type '{ChatExitReason.EXIT.value}' to exit. "
            f"Type '{ChatExitReason.START_OVER.value}' to start a new conversation (a new conversation will lose all previous context). "
            f"Type '#multiline' to enter multiline mode."
        )
    else:
        print(
            f"{INFO_PREFIX} A new conversation started. The bot forgot all previous context."
        )

    if rollover_message is None:
        messages = [SYS_CONVERSATION_INITIATION_MESSAGE]
    else:
        messages = [SYS_CONVERSATION_INITIATION_MESSAGE, rollover_message]

    while True:
        if messages[-1].role != Role.USER:
            user_input = request_user_input()
            if user_input == ChatExitReason.EXIT.value:
                return ChatExitReason.EXIT, None
            if user_input == ChatExitReason.START_OVER.value:
                return ChatExitReason.START_OVER, None
            user_input_timestamp = int(time.time())
            if (
                messages[-1].role != Role.SYSTEM
                and user_input_timestamp - messages[-1].timestamp
                > CONVERSATION_SOFT_TIMEOUT_SECONDS
            ):
                startover_confirm = Confirm.ask(
                    f"{WARNING_PREFIX} The previous conversation has been idle for more than {CONVERSATION_SOFT_TIMEOUT_SECONDS} seconds. "
                    "Do you want to start a new conversation?",
                    default=True,
                )
                if startover_confirm:
                    return ChatExitReason.START_OVER, Message(
                        role=Role.USER,
                        content=user_input,
                        timestamp=user_input_timestamp,
                    )
            messages.append(
                Message(
                    role=Role.USER, content=user_input, timestamp=user_input_timestamp
                )
            )

        response = openai.ChatCompletion.create(  # type: ignore
            model=model,
            temperature=TEMPERATURE,
            messages=[
                {"role": message.role.value, "content": message.content}
                for message in messages
            ],
        )
        assert response.choices[0]["message"]["role"] == Role.ASSISTANT.value

        bot_response = response.choices[0]["message"]["content"]
        print(f"{BOT_DISPLAY_NAME}:", bot_response)
        messages.append(
            Message(
                role=Role.ASSISTANT, content=bot_response, timestamp=int(time.time())
            )
        )

        if response.choices[0]["finish_reason"] == "length":
            Prompt.ask(
                f"{WARNING_PREFIX} The total token count exceeds the maximum. You must start a new conversation. Press Enter to continue",
            )
            return ChatExitReason.START_OVER, None


def run() -> None:
    setup_openai_key()
    model = select_model()
    chat_exit_reason, rollover_message = chat(model, has_previous_chat=False)
    while chat_exit_reason == ChatExitReason.START_OVER:
        chat_exit_reason, rollover_message = chat(
            model, has_previous_chat=True, rollover_message=rollover_message
        )
    print(f"{BYE_PREFIX} Bye!")
