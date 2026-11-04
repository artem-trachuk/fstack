---
name: gap-analysis
description: >
  Find open questions in confirmed requirements and send a question card.
  Use when feature_status is requirements_confirmed, or when the human is answering an open question card.
  Stop for answers. Do not start requirements collection.
---

# Gap analysis

Read the confirmed requirements and list what is still open.

## When to use

`feature.yaml` says `requirements_status: confirmed`. If the requirements are still a draft, or the file is only the template, stop and tell the human to invoke `/collect-requirements`. Do not follow that skill yourself.

## Steps

1. Follow `build-context` for `gap-analysis`.

2. A question is open when a wrong guess would change the spec, the acceptance criteria, or the scope. Record `record_questions`.

   An empty list is `no_open_questions`. Set `questions_status: none` and `feature_status: ready_to_plan`. Tell the human there is nothing to answer, and log that event. Then continue to `split-into-chunks`.

   A non-empty list sets `questions_status: open` and `feature_status: questions_open`. Each question gets an id `Q-<slug>-<n>`. Leave answers empty.

3. Follow `advisors` for `planner_review` once for this question text. A second call with the same text is a duplicate and does not count. Fold in a critique that names a real missing question. A failed advisor call does not stop you.

4. Send the question card through `tldr`. Partial answers are allowed. Record each answer with `answer_questions` when the human replies. When any answer is still empty, keep `waiting_on` and end the turn.

5. When every answer is filled, set `questions_status: answered` and `feature_status: ready_to_plan`.

## Events

- `record_questions`
- `answer_questions`

## Next

`split-into-chunks` after the status is `ready_to_plan`. While a question is open, stop.
