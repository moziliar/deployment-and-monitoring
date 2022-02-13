#!/usr/bin/env bash

if [[ ! -f .env ]]; then
  cp .env.template .env
fi

if [[ ! -f machine-list.yaml ]]; then
  touch machine-list.yaml
fi

if [[ ! -f user-list.yaml ]]; then
  touch user-list.yaml
fi

if [[ ! -f software-list.yaml ]]; then
  touch software-list.yaml
fi
