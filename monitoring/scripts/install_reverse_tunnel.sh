#!/usr/bin/env bash

# Install Prometheus
if [[ -e /usr/lib/systemd/system/node_exporter_reverse_tunnel.service ]]; then
  echo reverse tunnel service file exists
else
  cp ./template/node_exporter_reverse_tunnel.service /usr/lib/systemd/system/node_exporter_reverse_tunnel.service
fi

systemctl daemon-reload
systemctl start node_exporter_reverse_tunnel && echo node_exporter_reverse_tunnel started
