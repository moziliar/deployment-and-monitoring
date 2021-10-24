#!/usr/bin/env bash

chmod +x scripts/install_prometheus.sh
./scripts/install_prometheus.sh

chmod +x scripts/install_node_exporter.sh
./scripts/install_node_exporter

chmod +x scripts/install_reverse_tunnel.sh
./scripts/install_reverse_tunnel.sh
