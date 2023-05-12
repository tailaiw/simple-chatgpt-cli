# ChatGPT

A super quick implementation of ChatGPT in terminal, so I can avoid using the ChatGPT website which is more expensive and less privacy-friendly.

## Installation

Assuming you have [Poetry](https://python-poetry.org/) installed, run the following command to install the dependencies:

```bash
git clone git@github.com:tailaiw/chatgpt.git
cd chatgpt
poetry install
```

## Usage

```bash
poetry run chatgpt
```

Optionally, put the following in your `.bashrc` or `.zshrc` so you can call `chatgpt` directly from anywhere:

```bash
# create a shell function `chatgpt`
export CHATGPT_CLI_DIR="$HOME/your/local/path/to/this/repo/
chatgpt() {( set -e
  cd $CHATGPT_CLI_DIR
  poetry run chatgpt
)}
```

You must have an environment variable `OPENAI_API_KEY` for a valid OpenAI API key.

## Tips

Use `#startover` to start a new conversation whenever you switch a new topic and the bot doesn't need to refer the previous context anymore. This helps saving money. The program will remind you that if a conversation is idle for a while.

## Development

This project was initialized by my [Python project boilerplate](https://github.com/tailaiw/python-boilerplate). So you will need all the prerequisites of that project.
