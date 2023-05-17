ytt -f authserver.yaml -f authserver-httpproxy.yaml -f clientreg.yaml -f ../values.yaml --ignore-unknown-comments | kubectl apply -f- --wait
ytt -f gateway.yaml -f scg-httpproxy.yaml -f ../values.yaml --ignore-unknown-comments | kubectl apply -f- --wait
kubectl apply -f routes/