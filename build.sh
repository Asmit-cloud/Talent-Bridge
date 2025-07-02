#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

python manage.py migrate SkillSwap_Network 0011_remove_message_room_remove_message_sender_and_more --fake

python manage.py migrate

python manage.py collectstatic --no-input