#!/usr/bin/env bash

clear;

restart_db() {
    echo "  Restarting Postgresql ..."
    sudo systemctl restart postgresql
    echo "    Done."
}

create_dirs() {
    echo "  Creating directories ..."
    mkdir contentfiles/tmp
    echo "    Done."
}

clear_repo() {
    echo "  Dropping and recreating database ..."
    sudo su - postgres -c "dropdb documendous"
    sudo su - postgres -c "createdb documendous -O admin"
    echo "    Done."

    echo "  Clearing folder content ..."
    rm -rf contentfiles/*
    rm -rf tmp/*
    rm -rf media/*
    rm -rf logs/*
    echo "    Done."

    echo "  Removing all pyc files ..."
    find . -name "*cpython*.pyc" -exec rm -f {} \;
    echo "    Done."
}

migrate() {
    echo "  Migrating database schema ..."
    python manage.py makemigrations
    python manage.py makemigrations repo
    python manage.py makemigrations transformations
    python manage.py migrate
    echo "    Done."
}

main() {
    echo "Resetting Documendous repository ..."
    restart_db;
    clear_repo;
    create_dirs;
    migrate;
    python initdata.py
    echo "  Done."
}

main
