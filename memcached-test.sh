#!/bin/bash

S="--server=localhost:11211"

echo "test" > file.txt

echo "Setting with TTL=2 and waiting for 2 s..."
memcp $S --set --expire 3 file.txt
sleep 1 
echo "add'ing in between"
memcp $S --expire 3 --set file.txt
sleep 2 
echo "Checking key:"
memcat $S file.txt

echo "Setting with TTL=2 and waiting for 1 s..."
memcp $S --set --expire 3 file.txt
sleep 1
echo "Checking key:"
memcat $S file.txt
