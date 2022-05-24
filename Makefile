SHELL:=/usr/bin/env bash

.PHONY: python-dist
python-dist:
	@rm -rf ./com.sobolevn.bluetooth.sdPlugin/dist/macos
	@pyinstaller \
		--clean \
		--noconfirm \
		--dist com.sobolevn.bluetooth.sdPlugin/dist/macos \
		bluetooth-python/src/main.py

.PHONY: plugin
plugin:
	@rm -rf ./Release
	@mkdir ./Release
	@./DistributionTool -b -i ./com.sobolevn.bluetooth.sdPlugin -o ./Release

.PHONY: build
build: python-dist plugin

.PHONY: lint
lint:
	mypy bluetooth-python
	flake8 bluetooth-python
