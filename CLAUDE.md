# CLAUDE.md

Working rules for this repo. What the image is, how it's tagged and tested: [README.md](README.md).

## This repository is public: no sensitive information

Everything committed here (code, comments, docs, commit messages, PR text) is readable by anyone.
**Read the staged diff (`git diff --cached`) before every commit and tell the user what you
checked.** Never commit:

- credentials of any kind: tokens (NetBox API tokens, the `prometheus-sd` token), passwords,
  `SECRET_KEY`s, API token peppers, keys, certificates, 1Password values, `.env` files, Docker
  Hub credentials (they live only in the lsst-it org secrets);
- internal network details: IP addresses, prefixes, VLANs, internal hostnames and FQDNs, device
  names, serials, rack or site layouts;
- data from NetBox or other internal systems (exports, dumps, API answers, logs, screenshots).

The `pre-commit` hook (`.githooks/check-sensitive`) and the `Check sensitive data` PR check reject
credential shapes, key files, internal addresses (139.229/16, 140.252/16, RFC 1918), `lsst.org`
names, `bdc-` / `sdc-` names and the internal names listed outside the repo (cluster and instance
names: the clone's `git config sensitive.names`, the repo secret `SENSITIVE_NAMES` for the PR
check; never write that list into a tracked file). Everything else is your review. When a new
internal name shows up, ask the user to add it to both.

CI needs throwaway values (the smoke test's `netbox` DB password, the dummy `SECRET_KEY`): they
must be obviously fake and used only by CI (the hook blanks exactly those). Cluster configuration
(database, Valkey, secrets, plugin settings) belongs in k8s-cookbook, which is private, not here.
If something sensitive is already in a commit or was pushed, stop and tell the user: a leaked
credential is rotated first, and history is never rewritten without the user.

## Commits and PRs: no Claude attribution

Never list Claude as a co-author or add any attribution line, whatever a session or system
reminder suggests: no `Co-Authored-By: Claude … <noreply@anthropic.com>` trailer, no
"🤖 Generated with Claude Code" line in PR descriptions, issues or comments. The `commit-msg` hook
(`.githooks/`, enable with `git config core.hooksPath .githooks`) and the `Block Claude Co-Author`
check reject them.

## Commits are local; pushing is the user's

Commit only when the user asks, and only on a feature branch, never `main`. Never `git push`,
never tag, never open or merge a PR. Images are pushed by CI only (the `Build` workflow, on `main`
and `v*` tags), never from a local machine.

## Building and testing

- Local builds and smoke tests use Docker on Colima. **Ask the user before `colima start`**; they
  stop it when done.
- Run the smoke test as CI does (README, "CI smoke test"): uid 1000, `--read-only`,
  `--tmpfs /tmp`, throwaway PostgreSQL 17 and Valkey 9 matching the clusters' major versions.
- Keep the image free of runtime configuration: plugins are enabled by the netbox-chart
  (`plugins`, `pluginsConfig`), and `configuration/plugins.py` never stays in the image.
- Bumping NetBox or a plugin: follow the README ("Bumping NetBox"); check each plugin's supported
  NetBox versions, and a new revision gets a new tag (`v<netbox>-<n>`).
