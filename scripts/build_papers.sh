#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p output/pdf work
"${PYTHON:-.venv/bin/python}" scripts/full_report_tables.py
cd paper
for pair in 'report:技术报告' 'appendix:技术补充' 'defense:答辩演示' 'full_report:完整技术报告'; do
  source_name="${pair%%:*}"
  output_name="${pair#*:}"
  for pass in 1 2; do
    xelatex -interaction=nonstopmode -halt-on-error -output-directory=../output/pdf -jobname="$output_name" "$source_name.tex" > "../work/${source_name}-build.log" 2>&1
  done
done
