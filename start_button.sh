# #!/usr/bin/env bash
# Activate system
# @Author: Patryk Jacek Laskowski

STDOUT_PREFIX="[VSPU]: "
DEFAULT_CONFIG_FILE="config.yaml"
DEFAULT_DOCKER_COMPOSE_FILE="docker-compose.yaml"

WEB_PAGE="http://localhost:8050"
WEB_BROWSER="google chrome"

DATA_PRODUCER_DIR="data-producer"
DATA_PRODUCER_SERVICE_NAME="sum_the_age_mockup"


press_enter_to_continue () {
  # If anything was provided, print it first
  if [[ "$@" != "" ]]; then
    INFO=$(echo "$@")
  else
    INFO="Enter to continue else to quit"
  fi

  echo "$STDOUT_PREFIX"
  read -n1 -s -r -p $"$STDOUT_PREFIX $INFO [Y/n]" keypress
  echo -e "\n$STDOUT_PREFIX"

  # Else than Enter -> close
  if [ "$keypress" != "" ]; then
    echo "$STDOUT_PREFIX docker-compose down && shutting down."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    exit 1
  fi
}

stdout_file () {
  # Print out whole file line by line
  echo "$STDOUT_PREFIX stdoud file $1"
  while IFS="" read -r single_line || [ -n "$single_line" ]
  do
    printf '%s\n' "$STDOUT_PREFIX $single_line"
  done < "$1"
  echo "$STDOUT_PREFIX"
}

live_long_vspu () {
  # Pretty print logo
  echo "$STDOUT_PREFIX"
  echo "$STDOUT_PREFIX            __       __"
  echo "$STDOUT_PREFIX    \  /   \__      |__) |    |"
  echo "$STDOUT_PREFIX     \/  .  __/  .  |  .  \__/  ."
  echo "$STDOUT_PREFIX "
  echo "$STDOUT_PREFIX > Video Stream Processing Unit <"
  echo "$STDOUT_PREFIX "
}

live_long_vspu

# Retrieve -c and -d flags (configuration file path and custom docker-compose.yaml)
press_enter_to_continue "Retrieve -c flag (optional conf file path) and -d flag (custom docker-compose.yaml)?"
while getopts c:d: flag
do
  case "${flag}" in
    c) CONFIG_FILE=${OPTARG};;
    d) DOCKER_COMPOSE_FILE=${OPTARG};;
  esac
done

# Resolve configuration file (as specified or default)
if [ -z "$CONFIG_FILE" ]
then
  # Not specified, set default
  echo "$STDOUT_PREFIX Config file flag (-c) was not specified."
  echo "$STDOUT_PREFIX Using default file: $DEFAULT_CONFIG_FILE"
  CONFIG_FILE=$(echo "$DEFAULT_CONFIG_FILE")
else
  # Specified
  echo "$STDOUT_PREFIX Config file flag (-c) found: $CONFIG_FILE"
fi

# Resolve docker-compose file (as specified or default)
if [ -z "$DOCKER_COMPOSE_FILE" ]
then
  # Not specified, set default
  echo "$STDOUT_PREFIX Custom docker compose file flag (-d) was not specified."
  echo "$STDOUT_PREFIX Using default docker compose file: $DEFAULT_DOCKER_COMPOSE_FILE"
  DOCKER_COMPOSE_FILE=$(echo "$DEFAULT_DOCKER_COMPOSE_FILE")
else
  # Specified
  echo "$STDOUT_PREFIX Custom docker compose file flag (-d) found: $DOCKER_COMPOSE_FILE"
fi

# Set specific env variables from config file
press_enter_to_continue "Set env variables from config file?"
echo "$STDOUT_PREFIX Reading from $CONFIG_FILE"
for KEY in STREAMS_BOOTSTRAP_SERVERS STREAMS_INPUT_TOPIC STREAMS_OUTPUT_TOPIC BOOTSTRAP_SERVER
do
  # Look for value. Expects "KEY: <value>" patterns.
  VALUE=$(grep -w "$KEY" "$CONFIG_FILE" | sed 's/^.*: //')

  if [ -z "$VALUE" ]; then
    # Key not found
    echo "$STDOUT_PREFIX $KEY not found in $CONFIG_FILE."
    echo "$STDOUT_PREFIX Make sure $KEY in $CONFIG_FILE and start again."
    echo "$STDOUT_PREFIX Exit."
    exit 1
  elif [[ "$VALUE" == *"$KEY"* ]]; then
    # Key found but not specified "KEY: "
    echo "$STDOUT_PREFIX According to $CONFIG_FILE $KEY=<not defined>"
  else
    # Key found and specified "KEY: <value>" -> EXPORT
    echo "$STDOUT_PREFIX According to $CONFIG_FILE $KEY=$VALUE"
    export "$KEY"="$VALUE"
  fi
done
echo "$STDOUT_PREFIX Env variables set!"

# Print out docker-compose file
press_enter_to_continue "Stdout docker compose file: $DOCKER_COMPOSE_FILE ?"
stdout_file "$DOCKER_COMPOSE_FILE"

# Run docker compose file
press_enter_to_continue "Run docker-compose command?"
docker-compose -f "$DOCKER_COMPOSE_FILE" up --build -d

# Open Dash webpage
press_enter_to_continue "Open $WEB_PAGE with $WEB_BROWSER?"
echo "$STDOUT_PREFIX Opening $WEB_PAGE with $WEB_BROWSER"
open -a "$WEB_BROWSER" "$WEB_PAGE"

# Change directory
press_enter_to_continue "Start data producer (from ./$DATA_PRODUCER_DIR) part?"
cd "$DATA_PRODUCER_DIR"
echo "$STDOUT_PREFIX Changed directory to $(pwd)"

# Print out producer docker-file
press_enter_to_continue "Stdout docker compose file for data producer ./docker-compose.yaml?"
stdout_file docker-compose.yaml

# Run data-producer
press_enter_to_continue "Run: $DATA_PRODUCER_DIR/docker-compose.yaml ?"
echo "$STDOUT_PREFIX Running data-producer interactively (docker-compose run)"
echo "$STDOUT_PREFIX"
docker-compose run "$DATA_PRODUCER_SERVICE_NAME"

# Clean up
echo "$STDOUT_PREFIX"
echo "$STDOUT_PREFIX Running docker-compose down in $(pwd)"
echo "$STDOUT_PREFIX"
docker-compose down

cd ..
echo "$STDOUT_PREFIX"
echo "$STDOUT_PREFIX Running docker-compose -f $DOCKER_COMPOSE_FILE down in $(pwd)"
echo "$STDOUT_PREFIX"
docker-compose -f "$DOCKER_COMPOSE_FILE" down

live_long_vspu
