#!/bin/bash

if [[ ! -e .env ]]
then
  cp .env.example .env
fi

if [[ ! -e nodes.txt ]]
then
  cp nodes.txt.example nodes.txt
fi

chmod +x run.sh
