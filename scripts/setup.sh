#!/usr/bin/env bash

if [[ ! -f .env ]]; then
  cp .env.template .env
fi

if [[ ! -d deployment/log ]]; then
  mkdir log
fi

if [[ ! -d deployment/resources ]]; then
  mkdir resources
fi

if [[ ! -f deployment/resources/machine-list.yaml ]]; then
  touch resources/machine-list.yaml
fi

if [[ ! -f deployment/resources/user-list.yaml ]]; then
  touch resources/user-list.yaml
fi

if [[ ! -f deployment/resources/software-list.yaml ]]; then
  touch resources/software-list.yaml
fi

if [[ ! -d /tmp/ansible ]]; then
  mkdir /tmp/ansible
fi

# TODO: make ansible-vault using ansible-vault create secrete and make vault.txt file
