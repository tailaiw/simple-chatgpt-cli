# ChatGPT

A super quick implementation of ChatGPT in terminal, so I can avoid using the ChatGPT website which is more expensive and less privacy-friendly.

## Installation

Assuming you have [Poetry](https://python-poetry.org/) installed, run the following command to install the dependencies:

```bash
git clone git@github.com:tailaiw/chatgpt-cli.git
cd chatgpt-cli
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


## Development

This project was initialized by my [Python project boilerplate](https://github.com/tailaiw/python-boilerplate). So you will need all the prerequisites of that project.
