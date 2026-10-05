# Research template design

Language: English · [简体中文](research-template-design.md)

Use a local derived configuration for a one-off variation. Promote an experiment to a repository template when it establishes a reusable research route. The `strategy_pipeline` package maintains configuration fields and directory structure; `quant-market-research` maintains research questions and validation protocols.

## Quick decision

| Change | Recommendation |
| --- | --- |
| Dates, output directory, run name, or a few parameters | Use a local derived configuration |
| Compare models, features, or parameters within the same route | Start with a local derived configuration |
| Maintain a new frequency, data source, or universe over time | Add a repository template |
| Establish a baseline the team will reuse | Add a repository template |
| Add local assets or data-preparation steps | Add a template and document the assets |

A research unit usually shares the following boundaries:

- Universe and tradability rules
- Data frequency and source
- Labels, holding period, and cost assumptions
- Training and validation protocol
- Local asset dependencies

If these boundaries stay the same, prefer a derived local configuration. This avoids one-off templates and keeps comparisons on a consistent basis.

## Local derived configurations

Local configurations fit parameter searches, small feature experiments, model comparisons, and temporary date changes. Put them in `configs/local/`, change only fields needed for the experiment, and use a stable `run_name` prefix.

Follow the shared comparison protocol for feature experiments: hold the sample, labels, costs, and portfolio construction fixed. For each new feature group, check coverage, run within-family ablations, and check for duplicate fields. See the [Benchmark Ladder](../../concepts/benchmark-ladder.md).

Move a local configuration into a repository-maintained directory when the team needs to reuse it or when it becomes a documented entry point.

## Repository templates

A repository template should represent a stable research route and answer:

1. Which long-term research question does it address?
2. Which data assets and preparation steps does it require?
3. Which sample, labels, costs, and validation protocol does it use?
4. How does it differ from existing templates in a way that can be verified?

Name templates to identify the market or universe, data route, and frequency or research focus. A-share experiment templates usually live in versioned configuration directories maintained by the caller. Trace historical Hong Kong configurations through archived documentation in `quant-market-research`.

## Keep documentation in sync

When adding a repository template, update at least:

1. This repository's [configuration guide](../../orchestration/reference/configuration.md)
2. This repository's [documentation entry point](../../README.md)
3. Data-preparation instructions for any new assets
4. Configuration-loading and template smoke tests
5. Research or asset tests directly related to the route

Derived configurations used only locally usually do not require public documentation changes.

## Decision order

Check these questions in order:

1. Does the change introduce a new frequency, data source, or universe?
2. Does it add an asset-preparation step?
3. Will multiple people reuse the configuration as a stable baseline?
4. Can an existing template already support the experiment?

If the first three answers are no and an existing template fits, keep using a local derived configuration. Decide whether to promote it to a repository template after the experiment is reproducible and validated.
