# US-XXX Story Title

> **Pattern G template** — adapted from `hoangnb24/harness-experimental`.
> Generate via `vibe harness story "<title>" --lane <tiny|normal|high-risk>`.

## Status

planned

## Lane

tiny | normal | high-risk

## Product Contract

Describe the behavior this story must make true.  Link to product docs
when they exist.

## Relevant Product Docs

- `docs/product/...`
- (or VibecodeKit `references/...` if no `docs/product/` yet)

## Acceptance Criteria

- Criterion 1.
- Criterion 2.
- Criterion 3.

## Design Notes

- Commands:
- Queries:
- API:
- Tables:
- Domain rules:
- UI surfaces:

## Validation

| Layer | Expected proof |
|:------|:---------------|
| Unit | |
| Integration | |
| E2E | |
| Platform | |
| Release | |

## Risk Flags

(Filled by `vibe harness classify`; see
[`references/43-harness-engineering.md`](../../../references/43-harness-engineering.md)
for the 10-flag taxonomy.)

- [ ] auth
- [ ] authorization
- [ ] data_model
- [ ] audit_security
- [ ] external_systems
- [ ] public_contracts
- [ ] cross_platform
- [ ] existing_behavior
- [ ] weak_proof
- [ ] multi_domain

## Harness Delta

Document any harness updates (templates, classifier rules, RRI question
bank, anti-pattern catalog) made or proposed because of this story.

## Evidence

Add commands, reports, screenshots, or links after validation exists.

## VibecodeKit Cross-Refs

- TIP equivalent (if pipeline crosses to implementation):
- RRI session that fed this story:
- Conformance probe(s) added:
