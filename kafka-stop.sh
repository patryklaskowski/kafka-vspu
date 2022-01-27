#!/usr/bin/env bash
# Stop Kafka server
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

log "Shutting down kafka server"
./bin/kafka-server-stop.sh

sleep_time

log "Shutting down zookeeper server"
./bin/zookeeper-server-stop.sh

sleep_time

log "Done!"
