#!/bin/env bash

KUBECONFIG=/etc/origin/master/admin.kubeconfig oc get projects | egrep -Ev 'NAME|default|openshift|openshift-infra' | wc -l
