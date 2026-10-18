# Quality gate for this repo. `make gate` before every PR.
.PHONY: test gate

test:
	@set -e; for d in scripts skills/*/scripts evals; do python3 -m unittest discover -s $$d -p 'test_*.py'; done

gate: test
	python3 skills/doc-writing/scripts/doc_check.py .
	python3 skills/architecture/scripts/arch_check.py .
	python3 skills/ui-design-system/scripts/design_lint.py skills/architecture/references/examples/ts
	sh skills/security/scripts/sec_check.sh .
	scripts/privacy_check.sh
