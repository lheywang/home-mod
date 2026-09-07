#!/bin/bash

echo "Updating ..."
git pull origin main

systemctl restart home-mod

echo "Done !"
