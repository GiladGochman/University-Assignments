#!/bin/bash

expected_paths=(
  "./frontend"
  "./frontend/playwright-tests/test.spec.ts"
  "./frontend/playwright.config.ts"
  "./frontend/package.json"
  "./frontend/src/components/.keep"
  "./frontend/src/contexts/.keep"
  "./backend"
  "./backend/config/.keep"
  "./backend/controllers/.keep"
  "./backend/services/.keep"
  "./backend/routes/.keep"
  "./backend/middlewares/.keep"
  "./backend/models/.keep"
  "./backend/tests/crud.test.ts"
  "./backend/package.json"
)

for path in "${expected_paths[@]}"; do
  if [[ "$path" == *.* ]]; then
    # It's a file
    mkdir -p "$(dirname "$path")"
    touch "$path"
  else
    # It's a directory
    mkdir -p "$path"
  fi
done

echo "Structure generated!"

