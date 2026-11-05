# netbox-image

NetBox for LSST IT: the upstream [netbox-docker](https://github.com/netbox-community/netbox-docker)
image with the plugins we run, published as **`docker.io/lsstit/netbox`** and deployed by
k8s-cookbook (`fleet/lib/netbox`, the netbox-chart) on our dev and production NetBox instances.

| Plugin | Version | Why |
|---|---|---|
| [netbox-plugin-prometheus-sd](https://github.com/FlxPeters/netbox-plugin-prometheus-sd) | 2.2.0 | Prometheus `http_sd`: scrape targets from NetBox's devices (`/api/plugins/prometheus-sd/devices/`) |
| [netbox-topology-views](https://github.com/netbox-community/netbox-topology-views) | 5.0.1 | Topology drawings from NetBox's cables |

## What's in the image

- `FROM ghcr.io/netbox-community/netbox:v4.7.4`, the chart's appVersion.
- The plugins installed into NetBox's venv (`plugin_requirements.txt`).
- Their static files, collected at build time. The clusters run NetBox with a read-only root
  filesystem, so nothing can be collected or uploaded at runtime (custom topology images
  included: bake them in).
- **No runtime configuration.** The plugins are installed but not enabled: the chart enables them
  with `plugins` and configures them with `pluginsConfig`. `configuration/plugins.py` is used
  only for `collectstatic` and the CI smoke test, and the Dockerfile removes it from the image
  (left in `/etc/netbox/config/`, netbox-docker would load it and override the chart's values).

## Tags and releases

`v<NetBox version>-<revision>`, e.g. `v4.7.4-1`: the NetBox version, then this image's revision
for that version (plugin bumps, build changes). A release is a git tag:

```sh
git tag v4.7.4-1 && git push origin v4.7.4-1
```

The `Build` workflow then builds, smoke-tests and pushes `docker.io/lsstit/netbox:v4.7.4-1`.
Pushes to `main` publish `main` and `sha-<short>` (for trials); pull requests build and test
only.

**Bumping NetBox**: change the `FROM` tag together with the chart version in k8s-cookbook (its
appVersion), check that each plugin supports the new version (their compatibility tables), tag
`v<new version>-1`, deploy on the dev instance first. Renovate proposes base-image and plugin bumps.

## CI smoke test

Neither plugin is tested upstream on NetBox 4.7.4 (prometheus-sd's CI stops at 4.7.0;
topology-views' catalog says up to 4.7.3, its code sets no maximum), so every build runs the image
against throwaway PostgreSQL 17 and Valkey 9 containers (CI only; the image contains no database):
`migrate` (the plugins' migrations included), then `tests/smoke.py` checks that both plugins are
enabled, the http_sd endpoint returns a JSON list and the topology page renders. It runs as the
chart does: uid 1000, read-only root filesystem, only `/tmp` writable.

In the clusters the database is netbox-pg (CNPG, `fleet/lib/netbox-pg`) and the cache is the
chart's Valkey subchart; the chart's own `configuration.py` replaces netbox-docker's and reads
`plugins` / `pluginsConfig` from its values. None of that changes with this image: only
`image.registry`, `image.repository` and `image.tag`.

## Registry

Docker Hub, organization `lsstit` (with our other images: cnpg-backup, cnpgsphere, …):
<https://hub.docker.com/orgs/lsstit/repositories>. The workflow logs in with the lsst-it org
secrets `DOCKERHUB_LSSTIT_USERNAME` / `DOCKERHUB_LSSTIT_PASSWORD` (as cnpg-backup does); they
must be available to this repository. The repository `lsstit/netbox` must be **public**: the
clusters pull without `imagePullSecrets`.

## Git hooks

Enable the shared hooks once per clone:

```sh
git config core.hooksPath .githooks
```

`commit-msg` rejects commits with a `Co-Authored-By` trailer for Claude
(`<noreply@anthropic.com>`); the `Block Claude Co-Author` workflow enforces the same on every pull
request.

This repository is public: `pre-commit` (`.githooks/check-sensitive`) rejects credentials and
internal network details (addresses, `lsst.org` names, site and device names). The `Check
sensitive data` workflow runs the same on every pull request: credentials on every commit,
network details on the net diff. A false positive is committed with `--no-verify` after a person
has checked it.

Internal names (clusters, instances) are not listed in this public repository. Each clone sets
them as an extended-regex alternation, and the PR check reads the same value from the repository
secret `SENSITIVE_NAMES` (a secret because the logs are public):

```sh
git config sensitive.names '<name>|<name>|...'
```
