#!/usr/bin/env bash

clear;

find . -name "*.pyc" -exec rm -f {} \;

echo "Killing Index Tracker ..."
./kill_tracker.sh
echo "  Done."

sudo systemctl restart postgresql

echo "Starting Documendous dev server ..."

init_data() {
  echo "Initializing data ..."
  python initdata.py
  echo "  Done."
}

init_data;

echo "Starting Django dev server ..."
python manage.py runserver
