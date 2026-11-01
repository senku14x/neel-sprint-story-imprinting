#!/usr/bin/env bash
# git credential helper: reads GITHUB_TOKEN from the environment at call time; nothing is stored.
[ "$1" = "get" ] || exit 0
echo "username=x-access-token"
echo "password=${GITHUB_TOKEN}"
