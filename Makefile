.PHONY: init
init:
	rye sync
	rye run pre-commit install
