#!/bin/bash

pip install -r requirement.txt

cd client
npm install
npm run watch &
cd ..

cd server
PYTHONPATH=$PYTHONPATH:$(pwd)/../../crisp ./run_server.sh

