#!/usr/bin/env bash

echo "  Graceful shutdown ..."
for pid in $(ps -ef | grep index_service | grep -v grep | awk {'print $2'}); do echo "Killing pid: $pid"; kill $pid;  done
echo "    Done."
