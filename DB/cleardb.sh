#!/bin/bash
vagrant ssh -c "sudo su landingzone -c \"psql -d seads -c 'DELETE FROM data_raw;'\""
