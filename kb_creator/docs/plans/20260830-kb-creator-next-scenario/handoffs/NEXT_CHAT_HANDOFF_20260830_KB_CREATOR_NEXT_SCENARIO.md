# Next chat handoff — KB Creator second scenario

Goal id: `20260830-kb-creator-next-scenario`

State: `paused_for_new_chat`

## Purpose

Start a second real scenario as the proof that `kb_creator` can become a
config-driven product rather than a collection of Innsmouth-specific scripts.
Do not carry the old chat transcript; the files below are the canonical state.

## Read first

1. workspace `AGENTS.md`;
2. workspace `docs/governance/nri_goal_governance.md`;
3. `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`;
4. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`;
5. `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`;
6. `kb_creator/README.md` and the current tail of `kb_creator/PROJECT_STATUS.md`.

Restore the repository-policy orchestrator as `gpt-5.6-sol` at `medium` in the
canonical plan. Record actual platform model/effort as `unavailable` unless the
platform exposes it. Do not infer that a model switch occurred.

## First permitted actions

1. Run read-only `git status --short --branch`, `git rev-parse HEAD` and inspect
   current worktrees. Do not restore, stage, commit or delete anything.
2. Confirm whether the Innsmouth cleanup save-point was committed/pushed after
   this handoff. If it is still dirty, ask whether to close it first or create a
   separate clean worktree for the new scenario.
3. Obtain the exact next-scenario title/id and source PDF path from the user if
   they are not supplied in the opening message.
4. Verify the source path read-only; record size, SHA-256, page count and any
   companion assets. Treat source files as immutable.
5. Create/update the runtime goal corresponding to this durable bundle and set
   Step 1 active. Perform only read-only intake/reconnaissance before proposing
   the scenario contract.

## Non-negotiable constraints

- Do not mutate Innsmouth production or accepted r6/r7.
- Do not copy/rename the Innsmouth script family for the new scenario.
- Do not use an old translation as the source of a new `MASTER_RU`.
- Keep reconstruction fidelity separate from publication policy.
- Do not manually edit generated HTML/PDF.
- Do not treat one repaired example as closure without a full-scope audit.
- Do not commit or push without explicit user instructions.
- A release remains pending until a fresh independent `gpt-5.5` release review.

## Expected first-chat result

The first turn should end with a compact scenario intake and proposed
scenario-contract boundary, not with a full build. It must identify:

- exact source and immutable hash;
- document topology and risky classes;
- desired EN/RU/HTML/PDF scope;
- what is reusable from Innsmouth;
- what belongs in scenario config/policy;
- what code, if any, needs generic extraction;
- user acceptance gates and first bounded implementation step.

## Ready-to-paste resume prompt

```text
Продолжи durable goal `20260830-kb-creator-next-scenario`.

Сначала полностью прочитай:
- `AGENTS.md`;
- `docs/governance/nri_goal_governance.md`;
- `kb_creator/docs/KB_CREATOR_PIPELINE_SUMMARY_20260830.md`;
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/plan.md`;
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/context.md`;
- `kb_creator/docs/plans/20260830-kb-creator-next-scenario/handoffs/NEXT_CHAT_HANDOFF_20260830_KB_CREATOR_NEXT_SCENARIO.md`.

Восстанови роль главного оркестратора и runtime goal. Сначала только read-only
проверь Git/worktree и не смешивай новый сценарий с незакоммиченным Innsmouth
cleanup. Если я не указал новый сценарий и source PDF, запроси точные title/id
и путь. После этого выполни read-only intake: hash/page count/source topology,
риски, требуемые outputs и границу declarative scenario contract.

Не копируй Innsmouth-specific скрипты, не используй старый RU как источник
перевода, не изменяй source/accepted/production и не делай commit/push без
отдельного разрешения. Первый результат — intake и минимальная спецификация
следующего bounded шага, а не преждевременная полная сборка.
```
