#!/bin/bash

coverage run --source="." --omit="tests/*" ./manage.py test --settings=settings.settings_docker_test && coverage report