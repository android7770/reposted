# Elgato StreamDeck Bluetooth Plugin

[![test](https://github.com/sobolevn/bluetooth-streamdeck-plugin/actions/workflows/test.yml/badge.svg)](https://github.com/sobolevn/bluetooth-streamdeck-plugin/actions/workflows/test.yml)

Allows you to toggle your bluetooth state from the StreamDeck.


## Installation

Right now this tool **only works on macOS**.
Windows support is welcome, but I don't want to do it myself :)

To install, please:
1. Download `com.sobolevn.bluetooth.streamDeckPlugin` from [releases](https://github.com/sobolevn/bluetooth-streamdeck-plugin/releases)
2. Double click on this file, StreamDeck will promt you about further installation


## Development

### Setting up your venv

Install latest `3.9.x` python via:

```bash
PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.9
```

Then create and activate `venv` using this version of python.
Then run `pip install -r bluetooth-python/requirements.txt`

### Creating an `.exe` file from Python's source

We use `pyinstaller` to do that.
Make sure you run `pip install pyinstaller` in your `venv`.
It is not listed
And then run `make python-dist`

### Creating a StreamDeck plugin

We bundle `DistributionTool` with this plugin for better DX ([docs](https://developer.elgato.com/documentation/stream-deck/sdk/packaging/)).

Run `make plugin` to create a release after python dist is created.

### CI

We use `poetry` and `pyproject.toml` to specify dev-only dependencies.
This is required because we use `pyinstaller`
and we don't want to polute `requirements.txt` and production env.


## Acknowledgements

Code:

- https://github.com/ChrisRegado/streamdeck-googlemeet
- https://gist.github.com/rnaveiras/2224859
- https://github.com/alvaroiramirez/SensorTile

Icons:

- https://iconarchive.com/show/papirus-status-icons-by-papirus-team.html
- https://www.iconsdb.com/white-icons/bluetooth-icon.html

DistributionTool:

- https://developer.elgato.com/documentation/stream-deck/sdk/packaging/
