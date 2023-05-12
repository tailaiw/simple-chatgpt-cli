import os
from enum import Enum

import openai
from rich import print
from rich.prompt import Confirm, Prompt

openai.api_key = os.getenv("API_KEY")

ALLOWED_MODELS = ["gpt-3.5-turbo", "gpt-4"]
USER_DISPLAY_NAME = "[yellow3][b]You[/b][/yellow3] :smiley:"
BOT_DISPLAY_NAME = "[deep_sky_blue3][bold]Bot[/bold][/deep_sky_blue3] :robot:"


def select_model() -> str:
    model = Prompt.ask(
        "Please select the model you want to use",
        default="gpt-3.5-turbo",
        choices=ALLOWED_MODELS,
    )
    print(f"You selected [bold cyan]{model}[/bold cyan].")
    return model


class ChatExitReason(Enum):
    EXIT = "#exit"
    START_OVER = "#startover"


def request_user_input() -> str:
    user_input = Prompt.ask(USER_DISPLAY_NAME)

    if not user_input or user_input.isspace():
        return request_user_input()

    if user_input == ChatExitReason.EXIT.value:
        exit_confirm = Confirm.ask("Do you really want to exit?", default=False)
        if exit_confirm:
            return ChatExitReason.EXIT.value
        return request_user_input()

    if user_input == ChatExitReason.START_OVER.value:
        startover_confirm = Confirm.ask(
            "A new conversation will lose all previous context. Do you really want to start a new conversation?",
            default=False,
        )
        if startover_confirm:
            return ChatExitReason.START_OVER.value
        return request_user_input()

    return user_input


def chat(model: str, has_previous_chat: bool) -> ChatExitReason:
    if not has_previous_chat:
        print(
            "You can now start chatting with the bot. "
            f"Type '{ChatExitReason.EXIT.value}' to exit. "
            f"Type '{ChatExitReason.START_OVER.value}' to start a new conversation (a new conversation will lose all previous context)."
        )
    else:
        print("A new conversation started. The bot forgot all previous context.")

    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    while True:
        user_input = request_user_input()
        if user_input == ChatExitReason.EXIT.value:
            return ChatExitReason.EXIT

        if user_input == ChatExitReason.START_OVER.value:
            return ChatExitReason.START_OVER

        messages.append({"role": "user", "content": user_input})
        response = openai.ChatCompletion.create(
            model=model, temperature=0.5, messages=messages
        )
        assert response.choices[0]["message"]["role"] == "assistant"

        bot_response = response.choices[0]["message"]["content"]
        print(f"{BOT_DISPLAY_NAME}:", bot_response)

        if response.choices[0]["finish_reason"] == "length":
            Prompt.ask(
                "The total token count exceeds the maximum. You must start a new conversation. Press Enter to continue"
            )
            return ChatExitReason.START_OVER

        messages.append({"role": "assistant", "content": bot_response})


if __name__ == "__main__":
    model = select_model()
    chat_exit_reason = chat(model, has_previous_chat=False)
    while chat_exit_reason == ChatExitReason.START_OVER:
        chat_exit_reason = chat(model, has_previous_chat=True)
