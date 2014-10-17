#!/bin/sh

cd /app

export PYTHONPATH=.:gen
py="/env/bin/python"

cmd=$1

case "$cmd" in
fetch)
  $py kaggle_down.py fetch-all -c d/conf.pb --log-config=logger.json
  ;;
sync-sqlite)
  $py kaggle_update_sqlite.py sync -c d/conf.pb --log-config=logger.json
  ;;
sync-calendar)
  $py kaggle_update_calendar.py sync-all -c d/conf.pb --log-config=logger.json
  ;;
*)
  echo "Usage: $0 {fetch|sync-calendar|sync-calendar}"
  exit 1
esac
