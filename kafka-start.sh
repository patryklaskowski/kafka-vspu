#!/usr/bin/env bash
# Start Kafka server
#
# @Author: Patryk Jacek Laskowski

KAFKA_DIR="kafka_2.13-2.8.0"

timestamp (){
  echo "[$(date +%T)]"
}

log () {
  printf "$(timestamp) $@\n"
}

sleep_time () {
  SEC=10
  log "Sleeping $SEC s ..."
  sleep $SEC
  log "Done sleeping !"
}

log "Changing directory to $KAFKA_DIR"
cd ~/$KAFKA_DIR

log "Staring zookeeper server as daemon process"
./bin/zookeeper-server-start.sh -daemon config/zookeeper.properties & log $!

sleep_time

log "Staring kafka server as daemon process"
./bin/kafka-server-start.sh -daemon config/server.properties & log $!

sleep_time

log "Done!"
