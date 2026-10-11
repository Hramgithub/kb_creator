# KB Creator Scope

Status: initial product boundary.

## Purpose

`kb_creator` builds structured knowledge bases from accepted source artifacts.
It is downstream from reconstruction, translation, proofreading, and publishing.

## In Scope

- ingest frozen manifests for accepted scenario/book artifacts;
- validate that inputs have not drifted;
- extract entities, locations, events, clues, handouts, timelines, and other
  KB-facing structures;
- produce KB reports, QA findings, and links back to accepted source anchors;
- keep generated KB output reproducible from declared scripts and configs.

## Out Of Scope

- OCR or PDF text reconstruction;
- translation;
- proofreading;
- HTML/PDF publishing;
- production release approval;
- knowledge-base integration across many books or rulebooks.

## Baseline Principle

The product starts from a frozen input contract. If the input KeeperBook, KB
files, HTML, PDF, QA reports, scripts, config, or required images change, the
freeze manifest must be regenerated and re-reviewed before downstream KB work
continues.
