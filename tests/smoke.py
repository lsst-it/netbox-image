"""Smoke test, run by CI inside the built image after `manage.py migrate` (build.yaml).

Neither plugin is tested upstream on our NetBox version (prometheus-sd's CI stops at 4.7.0,
topology-views declares 4.7.3 in its catalog), so this proves they load, migrate and answer:
the http_sd endpoint returns a JSON list (no pagination) and the topology page renders with its
collected static files.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

PLUGINS = ("netbox_prometheus_sd", "netbox_topology_views")

missing = [p for p in PLUGINS if p not in settings.PLUGINS]
if missing:
    raise SystemExit(f"plugins not enabled: {missing}")

user = get_user_model().objects.create_superuser(
    "smoke", "smoke@example.invalid", "smoke-test-only-password"
)
client = Client()
client.force_login(user)

failed = []
for name, url, accept in (
    ("prometheus-sd devices", "/api/plugins/prometheus-sd/devices/", "application/json"),
    # Without a query string the topology page saves the user's options (IndividualOptions, a
    # plugin table) and redirects to itself with them: follow it, but never to the login page.
    ("topology-views home", reverse("plugins:netbox_topology_views:home"), "text/html"),
):
    response = client.get(url, HTTP_ACCEPT=accept, follow=True)
    hops = [hop for hop, _ in response.redirect_chain]
    print(f"{name}: GET {' -> '.join([url, *hops])} -> {response.status_code}")
    if response.status_code != 200 or any("/login/" in hop for hop in hops):
        failed.append(name)
    elif accept == "application/json" and not isinstance(response.json(), list):
        failed.append(f"{name} (not a JSON list)")

if failed:
    raise SystemExit(f"smoke test failed: {', '.join(failed)}")
print("smoke test passed")
