#!/bin/env bash

KUBECONFIG=/etc/origin/master/admin.kubeconfig oc get --no-headers users | wc -l
