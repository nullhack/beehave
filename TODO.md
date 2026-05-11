# local-merge

> **Flow:** delivery-flow · **Session:** step-decorators-delivery · **Owner:** SE · **Skills:** merge-local · **Git:** main

## Todo

[ ] Pull latest remote main
[ ] Squash-merge feature commits into local main
[ ] Run tests on local main to verify
[ ] Output — merged-commits
[ ] **ANCHOR** — flowr transition merged → publish-decision → rewrite todo

## Flowr Cheatsheet

| What | Command | Key fields |
|------|---------|------------|
| Inspect state | `check --session` | `.attrs.owner` `.attrs.skills` |
| See paths | `next --session` | `.transitions[].status` |
| Advance | `transition <trigger> --session` | `.to` (next state) |