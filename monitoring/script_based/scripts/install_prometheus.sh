#!/usr/bin/env bash

# Install Prometheus
if [[ -e /usr/lib/systemd/system/prometheus.service ]]; then
  echo prometheus service file exists
else
  cp ./template/prometheus.service /usr/lib/systemd/system/prometheus.service
fi

if [[ -e /usr/local/bin/prometheus ]]; then
  echo prometheus version "${/usr/local/bin/prometheus --version}" exists
  exit
fi

# Create prom user and change owner of dir
useradd --no-create-home --shell /bin/false prometheus

if [[ ! -d /etc/prometheus ]]; then
  mkdir /etc/prometheus
  chown prometheus:prometheus /etc/prometheus
fi

if [[ ! -d /var/lib/prometheus ]]; then
  mkdir /var/lib/prometheus
  chown prometheus:prometheus /var/lib/prometheus
fi

wget -q https://github.com/prometheus/prometheus/releases/download/v2.31.0-rc.0/prometheus-2.31.0-rc.0.linux-amd64.tar.gz
tar xvfz prometheus-2.31.0-rc.0.linux-amd64.tar.gz
cd prometheus-2.31.0-rc.0.linux-amd64
cp prometheus /usr/local/bin/prometheus
cp prometheus.yml /etc/prometheus/prometheus.yml # Manual setup for node exporter scraping required
chown prometheus:prometheus /usr/local/bin/prometheus
chown prometheus:prometheus /etc/prometheus/prometheus.yml
cd ..
rm -rf prometheus-2.31.0-rc.0.linux-amd64*
systemctl daemon-reload
systemctl start prometheus

echo prometheus started
