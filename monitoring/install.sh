#!/usr/bin/env bash

# Prepare systemd service file directory
if [[ ! -d /usr/lib/systemd/system ]]; then
    mkdir /usr/lib/systemd/system
fi

chmod +x scripts/install_prometheus.sh
./scripts/install_prometheus.sh

chmod +x scripts/install_node_exporter.sh
./scripts/install_node_exporter.sh

chmod +x scripts/install_reverse_tunnel.sh
./scripts/install_reverse_tunnel.sh $1 $2 $3 $4
