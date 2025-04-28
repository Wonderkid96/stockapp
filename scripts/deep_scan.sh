#!/usr/bin/env bash
set -e

echo "1) Lint & Format"
flake8 src/stockapp --max-line-length=88 --extend-ignore=E203,W503
black --check src/stockapp
isort --check-only --recursive src/stockapp

echo "2) Type-check"
mypy src/stockapp

echo "3) Security"
bandit -r src/stockapp -ll
pip freeze > .reqs.tmp.txt
safety check --file .reqs.tmp.txt --full-report
rm .reqs.tmp.txt

echo "4) Complexity & Dead Code"
radon cc src/stockapp -nc
vulture src/stockapp

echo "5) Dependency Graph & Conflicts"
pipdeptree
pip check

echo "✅ Deep scan complete!" 