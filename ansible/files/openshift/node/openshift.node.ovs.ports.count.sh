#!/bin/env bash

echo $(/usr/bin/ovs-vsctl show | grep -c Port)
