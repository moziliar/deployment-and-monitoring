#!/usr/bin/env bash

# Install Prometheus
if [[ -e /usr/lib/systemd/system/node_exporter.service ]]; then
  echo node_exporter service file exists
else
  cp ./template/node_exporter.service /usr/lib/systemd/system/node_exporter.service
fi

if [[ -e /usr/local/bin/node_exporter ]]; then
  echo node_exporter version "${/usr/local/bin/node_exporter --version}" exists
  exit
fi

wget https://github.com/prometheus/node_exporter/releases/download/v1.2.2/node_exporter-1.2.2.linux-amd64.tar.gz
tar xvfz node_exporter-1.2.2.linux-amd64.tar.gz
cd node_exporter-1.2.2.linux-amd64
cp node_exporter /usr/local/bin/node_exporter
cd ..
rm -rf node_exporter-1.2.2.linux-amd64*
systemctl daemon-reload
systemctl start node_exporter

echo node_exporter started
