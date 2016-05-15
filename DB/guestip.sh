#!/bin/bash
vagrant ssh-config | head -2 | tail -1 | awk '{print $2}'
