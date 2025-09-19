.PHONY: run fast planonly index route-test artifacts lint

run:
	python -m payready.cli tekton --goal "$(GOAL)"

fast:
	python -m payready.cli tekton --goal "$(GOAL)" --consensus-free code test_debug

planonly:
	python -m payready.cli tekton --goal "$(GOAL)" --to plan

index:
	python scripts/index_repo.py $(ROOT)

route-test:
	pytest -q tests/test_routing.py

artifacts:
	pytest -q tests/test_artifacts.py

lint:
	ruff check
