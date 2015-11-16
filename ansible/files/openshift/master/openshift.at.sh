#!/bin/env bash

script=$(basename $1)

echo "/usr/local/sbin/$script" | at now
