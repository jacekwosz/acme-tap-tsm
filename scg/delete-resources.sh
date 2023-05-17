ytt -f gateway.yaml -f scg-httpproxy.yaml -f authserver.yaml -f authserver-httpproxy.yaml -f clientreg.yaml -f ../values.yaml --ignore-unknown-comments | kubectl delete -f-
kubectl delete -f routes/