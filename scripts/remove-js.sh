#!/bin/ash

for app_name in `ls -lx apps`; do
    rm -f `find apps/$app_name/ -type f -name "*.js"`
done
