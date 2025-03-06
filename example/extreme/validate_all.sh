#!/bin/bash

echo "Validating all solutions in the extreme folder..."
echo

echo "=== Minimal Solution ==="
python3 ../validator.py extreme_input.json minimal_solution.json
echo

echo "=== Simple Solution ==="
python3 ../validator.py extreme_input.json extreme_solution_simple.json
echo

echo "=== Complex Solution ==="
python3 ../validator.py extreme_input.json extreme_solution.json
echo

echo "Validation complete!" 