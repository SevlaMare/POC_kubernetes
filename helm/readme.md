Chart.yaml  - entry point \
/templates  - kubernetes yamls \
values      - default values to be injected

# 1 write the kubernetes yamls at /templates

# 2 render to verify, injecting all templates
```
cd helm
helm template <chart_name> <chart_folder>
```

# 3 install chart
kubernetes cluster must be running.
```
cd helm
helm template apichart api
```

# 4 see current deploy version
```
helm list
```
