#!/usr/bin/env bash

clear;

find . -name "*.pyc" -exec rm -f {} \;

echo "Restarting Postgresql ..."
sudo systemctl restart postgresql
echo "  Done."

# sudo su - postgres -c "dropdb documendous"
# sudo su - postgres -c "createdb documendous -O admin"

rm -rf contentfiles/*
mkdir contentfiles/tmp
rm -rf tmp/*
rm -rf media/*
rm -rf logs/*

python manage.py makemigrations
python manage.py makemigrations repo
python manage.py makemigrations transformations
python manage.py migrate

python initdata.py
