helm install redis bitnami/redis --version 16.12.2 --set "replica.replicaCount=0" --wait
ytt -f acme-cart/config/workload.yaml -f acme-catalog/config/workload.yaml -f acme-identity/config/workload.yaml -f acme-order/config/workload.yaml -f acme-payment/config/workload.yaml -f acme-shopping/config/workload.yaml -f ../values.yaml --ignore-unknown-comments | kubectl apply -f-
