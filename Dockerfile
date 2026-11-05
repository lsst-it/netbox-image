# NetBox with the plugins LSST IT runs (see README.md).
# The base tag follows the netbox-chart appVersion that k8s-cookbook deploys (fleet/lib/netbox):
# bump them together.
FROM ghcr.io/netbox-community/netbox:v4.7.4

# Into NetBox's venv (the base image sets VIRTUAL_ENV=/opt/netbox/venv).
COPY plugin_requirements.txt /opt/netbox/plugin_requirements.txt
RUN /usr/local/bin/uv pip install -r /opt/netbox/plugin_requirements.txt

# Static files. netbox-topology-views ships JS / CSS and loads its images from
# STATIC_ROOT/netbox_topology_views/img; the clusters run with a read-only root filesystem, so
# everything is collected here. collectstatic needs the plugins enabled, but only now: the chart
# mounts only /etc/netbox/config/configuration.py and netbox-docker loads every other *.py in
# that directory, so a plugin file left there would override the chart's `plugins` /
# `pluginsConfig`. It is copied in, used and removed in the same layer.
COPY configuration/plugins.py /tmp/build_plugins.py
RUN mkdir -p /opt/netbox/netbox/static/netbox_topology_views/img \
 && cp /tmp/build_plugins.py /etc/netbox/config/zz_build_plugins.py \
 && DEBUG=true SECRET_KEY="build-only-dummy-key-build-only-dummy-key-0123456789" \
    /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py collectstatic --no-input \
 && rm -rf /etc/netbox/config/zz_build_plugins.py /etc/netbox/config/__pycache__ \
    /tmp/build_plugins.py
