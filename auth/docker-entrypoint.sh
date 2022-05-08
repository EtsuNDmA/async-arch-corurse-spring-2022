#!/bin/bash
set -e

trap exit SIGINT

serve() {
#  wait_for_postgresql
#  wait_for_kafka

  export HOST=${APP_HOST:-0.0.0.0}
  export PORT=${APP_PORT:-8080}
  exec python -m uvicorn app.main:app --host "${HOST}" --port "${PORT}" --reload
}

wait_for_kafka() {
  until kafkacat -b "${KAFKA_BOOTSTRAP_SERVERS:-kafka}" -L  > /dev/null 2>&1
  do
    echo "Waiting for kafka ..."
    sleep 1
  done
}

wait_for_postgresql() {
  until psql -h "${PG_HOST:-postgresql}" -c "select 1" > /dev/null 2>&1
  do
    echo "Waiting for postgresql ..."
    sleep 1
  done
}

help() {
  echo "auth service"
  echo ""
  echo "Usage:"
  echo ""
  echo "help -- show this help"
  echo "serve -- start auth backend with hot-reloading"
  echo ""
}

case "$1" in
  help)
    shift
    help
    ;;
  serve)
    shift
    serve
    ;;
  *)
    exec "$@"
    ;;
esac
