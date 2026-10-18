# Quality gate for this repo. `make gate` before every PR.
.PHONY: test gate

test:
	@set -e; for d in skills/*/scripts; do python3 -m unittest discover -s $$d -p 'test_*.py'; done

gate: test
	python3 skills/doc-writing/scripts/doc_check.py .
	scripts/privacy_check.sh
