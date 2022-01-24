#!/usr/bin/env bash

# Install Prometheus
if [[ -e /usr/lib/systemd/system/node_exporter_reverse_tunnel.service ]]; then
  echo reverse tunnel service file exists
else
  # Set up node_exporter key
  TARGET_PORT=$1
  KEY_FILE=$2
  REMOTE_TARGET=$3
  REMOTE_USER=$4

  if [[ ! -e $KEY_FILE ]]; then
    ssh-keygen -f $KEY_FILE -q -N ""
  fi

  ssh-copy-id -i $KEY_FILE $REMOTE_USER@$REMOTE_TARGET

  sed -e "s|TARGET_PORT|$TARGET_PORT|g"\
    -e "s|KEY_FILE|$KEY_FILE|g"\
    -e "s|REMOTE_TARGET|$REMOTE_TARGET|g"\
    -e "s|REMOTE_USER|$REMOTE_USER|g"\
    ./template/node_exporter_reverse_tunnel.service\
    > /usr/lib/systemd/system/node_exporter_reverse_tunnel.service
fi

systemctl daemon-reload
systemctl start node_exporter_reverse_tunnel && echo node_exporter_reverse_tunnel started
