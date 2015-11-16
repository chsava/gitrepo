#!/bin/env bash

KUBECONFIG=/etc/origin/master/admin.kubeconfig /usr/bin/oadm manage-node --list-pods --selector='' | grep -c running 
