#!/usr/bin/env bash
# Delete and create kafka topics
#
# @Author: Patryk Jacek Laskowski

KAFKA_DIR="kafka_2.13-2.8.0"

EXAMPLE_001="example.001"
EXAMPLE_001_AGE_SUM="example.001.age.sum"

ZOOKEEPER="127.0.0.1:2181"

timestamp (){
  echo "[$(date +%T)]"
}

log () {
  printf "$(timestamp) $@\n"
}

list_topics () {
  log "Listing all existing topics:"
  for TOPIC in $(./bin/kafka-topics.sh --zookeeper $ZOOKEEPER --list)
  do
    log "\t$TOPIC"
  done
}

sleep_time () {
  SEC=10
  log "Sleeping $SEC s ..."
  sleep $SEC
  log "Done sleeping !"
}

log "Changing directory to $KAFKA_DIR"
cd ~/$KAFKA_DIR

list_topics

for KAFKA_TOPIC in $EXAMPLE_001 $EXAMPLE_001_AGE_SUM
do
  log "checking topic: $KAFKA_TOPIC"

  if ./bin/kafka-topics.sh --zookeeper $ZOOKEEPER --list | grep -q $KAFKA_TOPIC
  then

    log "YES! topic $KAFKA_TOPIC exists"

    log "Deleting $KAFKA_TOPIC topic"
    ./bin/kafka-topics.sh --zookeeper $ZOOKEEPER --topic $KAFKA_TOPIC --delete --force

    sleep_time

    log "Creating $KAFKA_TOPIC topic"
    ./bin/kafka-topics.sh --zookeeper $ZOOKEEPER --topic $KAFKA_TOPIC --create --partitions 1 --replication-factor 1

  else

    log "NO! topic $KAFKA_TOPIC does not exist"

    log "Creating $KAFKA_TOPIC topic"
    ./bin/kafka-topics.sh --zookeeper $ZOOKEEPER --topic $KAFKA_TOPIC --create --partitions 1 --replication-factor 1

  fi

done

list_topics

log "Done!"