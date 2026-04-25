#!/bin/bash

dacpu-test --test-config 1000.json | tee ./logs/1000.log
dacpu-test --test-config 1001.json | tee ./logs/1001.log
dacpu-test --test-config 1002.json | tee ./logs/1002.log
dacpu-test --test-config 1003.json | tee ./logs/1003.log
dacpu-test --test-config 1004.json | tee ./logs/1004.log
dacpu-test --test-config 1005.json | tee ./logs/1005.log
dacpu-test --test-config 1006.json | tee ./logs/1006.log
dacpu-test --test-config 1007.json | tee ./logs/1007.log
dacpu-test --test-config 1008.json | tee ./logs/1008.log
dacpu-test --test-config 1009.json | tee ./logs/1009.log
