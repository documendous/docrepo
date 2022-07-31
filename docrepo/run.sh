#!/usr/bin/env bash

python index_service.py >> logs/index_service.log &
python manage.py runserver
echo "Shutting down the indexing service ..."
./kill_tracker.sh
echo "Done."
