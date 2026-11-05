# Plugins enabled at build time (collectstatic, see the Dockerfile) and in the CI smoke test.
# Not part of the image's runtime configuration: in the clusters the netbox-chart sets
# `plugins` and `pluginsConfig` (k8s-cookbook, fleet/lib/netbox/values.yaml).
PLUGINS = [
    "netbox_prometheus_sd",
    "netbox_topology_views",
]
