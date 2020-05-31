#!/usr/bin/bash

gunicorn main:app --bind=0.0.0.0:8080
