# Q4: Reflection and Next Steps — Mira
**Submitted by:** Venkat Ranganathan, AI PM/TPM, Nexora Pvt. Ltd.
**Course:** Applied Agentic AI for PMs/TPMs
**Date:** June 2026

---

## 1. Trace Findings and Observations

Connecting Langfuse observability to the Mira workflow revealed several
important insights that would not have been visible from outputs alone.

### What the Traces Showed

**Token usage patterns:** The Status Reporter agent consistently consumed
the highest tokens (~1,822 per run) due to the combination of pre-computed
task summary, full task board CSV, and timeline data all being passed in the
same context window. This is a known trade-off — data richness improves
accuracy but increases cost. For a $0.09/user/month system, this is
acceptable. At scale (1,000+ users), this would warrant context window
optimization.

**Hallucination detection via traces:** Reviewing traces for vague input
tests (T2, T4, T6, T9) confirmed that guardrails fired correctly — the
orchestrator returned insufficient data responses rather than routing to
agents that would have fabricated outputs. This was only verifiable by
examining the trace flow, not just the final output.

**Routing accuracy:** Every intent classification in the trace log routed
to the correct specialist agent. The one known edge case — compound requests
where sub-phrases are occasionally flagged as unknown_intent — was visible
in traces but did not affect final output quality since the primary intent
was correctly routed.

**Cost per run:** Average cost per pipeline run was ~$0.000204, with total
daily cost for 15 runs at ~$0.003/user/day. This is well within the target
budget and confirms gpt-4o-mini as the right model choice for this use case.

---

## 2. Improvement Plan

### Immediate Improvements (Next 30 Days)

**1. Capture agent output in Langfuse traces**
Currently traces capture input, session, and metadata but not the full agent
output. Adding output capture to the Langfuse HTTP Request node would enable
end-to-end input/output visibility per trace — essential for production
quality monitoring.

**2. Dynamic session IDs per run**
The current implementation uses a static session ID. Replacing this with a
dynamic timestamp-based ID would enable proper session-level grouping in
Langfuse, making it possible to correlate multiple turns in a single user
conversation.

**3. Expand DeepEval test coverage**
The current DeepEval evaluation covers 3 of 12 test cases. Expanding to all
12 baseline tests with additional metrics (HallucinationMetric,
ContextualRelevancyMetric) would provide comprehensive automated quality
assurance before each deployment.

**4. Resolve compound intent sub-phrase flagging**
The orchestrator occasionally flags sub-phrases in compound requests as
unknown_intent. Refining the intent classifier prompt with additional
compound intent examples would eliminate this edge case.

### Medium-Term Improvements (30-90 Days)

**5. Add Jira/Trello API integration**
Replace CSV file reads with live task board API calls. This would eliminate
the manual CSV export step and give Mira access to real-time task data,
making status reports truly live rather than point-in-time snapshots.

**6. Human-in-the-Loop review step**
Add an optional review checkpoint where the PM/TPM can approve or edit
Mira's output before it is shared with stakeholders. This is particularly
important for stakeholder update emails where tone and content require
human judgment.

**7. RAG implementation for historical projects**
Build a retrieval layer over Nexora's historical project documentation.
This would allow Mira to ground new project plans in patterns from similar
past projects rather than generating from scratch, improving plan quality
and reducing generic outputs.

---

## 3. Evaluation and Fine-Tuning Connection

### Current Evaluation State

DeepEval evaluation confirmed 100% pass rate across Answer Relevancy and
Faithfulness metrics for the three core test cases evaluated. The evaluation
loop followed the course framework:
Evaluate → Find failure (T10 partial) → Fix prompt + architecture

→ Re-evaluate → Confirm improvement (T10 full pass)
This loop was executed once during Phase 2 and is documented in
`baseline_test_results.md` with before/after comparison.

### Fine-Tuning Candidate

If fine-tuning were applied, the **Status Reporter Agent** is the strongest
candidate. It was the only agent that required architectural intervention
(JavaScript pre-computation) rather than prompt-only fixes. Fine-tuning on
examples showing correct CSV row-by-row counting behavior could eliminate
the need for the pre-computation workaround and make the agent more robust
to different CSV formats.

Training data would consist of 15-20 examples:
- 10 examples: task board CSV input → correct status report with verified
  counts
- 5 examples: vague input → correct insufficient data response
- 5 examples: CSV with different column orders → correct count extraction

### Continuous Evaluation Strategy

For production, the following evaluation cadence is recommended:

| Frequency | Activity |
|---|---|
| Every run | Langfuse trace capture (input, session, metadata) |
| Weekly | Manual review of 5 random traces for quality |
| Monthly | DeepEval re-run on full 12-test baseline dataset |
| Quarterly | Full prompt review and optimization cycle |
| On any hallucination report | Immediate prompt fix + full re-test before re-deploy |

---

## 4. Privacy Considerations

### Data Flow Analysis

Mira's data flow involves sending project data to the OpenAI API for LLM
processing. For the ABCDE Ltd. engagement, this includes:
- Project descriptions (scope, goals, approach)
- Task board data (task names, assignees, statuses, due dates)
- Risk data (risk descriptions, mitigations)
- Timeline data (phases, milestones, activities)

### Privacy Risks Identified

**1. Client data sent to third-party LLM provider**
Project data from ABCDE Ltd. is processed by OpenAI's gpt-4o-mini model.
Depending on the OpenAI API data processing agreement in effect, this data
may be used for model training unless explicitly opted out via the OpenAI
enterprise agreement.

**Mitigation:** Review and confirm OpenAI's data processing agreement.
Opt out of training data usage via OpenAI API settings. For highly
sensitive client data, consider on-premise LLM deployment (e.g., Ollama
with Llama 3) as a future architecture option.

**2. Assignee names in task board data**
The task board CSV contains real team member names (Arjun Mehta, Sarah Lin,
Priya Nair, James Wong, Ravi Kumar). These are personal data under GDPR
given Nexora is headquartered in London, UK.

**Mitigation:** Anonymize assignee names before passing to the LLM (replace
with role identifiers such as "Data Scientist 1", "PM Lead") for production
deployment. Update the JavaScript combination node to strip or anonymize
PII fields.

**3. Observability data in Langfuse**
User inputs and session metadata are stored in Langfuse Cloud (US region).
For EU-based Nexora, this may create cross-border data transfer concerns
under GDPR.

**Mitigation:** Evaluate Langfuse EU region deployment or self-hosted
Langfuse instance for production. Ensure data processing agreement with
Langfuse covers GDPR compliance requirements.

### Privacy-by-Design Principles Applied

1. **Minimum data principle:** Only the fields required for each agent are
   passed in context — full database exports are not used
2. **No persistent storage:** n8n Cloud does not persist project data
   between workflow runs — data exists only during execution
3. **Access control:** Google Drive files accessible only via Nexora's
   authenticated Google OAuth2 connection

---

## 5. Rollout Plan for 10 PMs/TPMs

### Readiness Assessment

Before rolling out to the full PM/TPM team, the following gates must be met:

| Gate | Criteria | Current Status |
|---|---|---|
| Quality gate | 12/12 baseline tests passing | ✅ Met |
| Observability gate | Langfuse traces confirmed | ✅ Met |
| Cost gate | ≤ $0.20/user/month | ✅ Met ($0.09) |
| Security gate | IT/Security review completed | ⏳ Pending |
| Privacy gate | OpenAI data processing reviewed | ⏳ Pending |

### Rollout Approach

**Week 1-2: Pilot (2-3 PMs)**
- Select early adopters comfortable with AI tools
- Run Mira on their active projects
- Collect structured feedback via weekly form
- Monitor Langfuse traces daily for anomalies

**Week 3-4: Expand (5-7 PMs)**
- Incorporate pilot feedback into prompts
- Add project plan generation and risk assessment to rollout
- Run DeepEval evaluation after any prompt changes

**Week 5-6: Full team (all 10 PMs/TPMs)**
- Enable all 6 agent capabilities
- 1-hour onboarding workshop covering:
  - How to write effective Mira prompts
  - How to validate Mira outputs before sharing
  - How to report issues or hallucinations
- Distribute 1-page Mira Quick Reference Guide

### Change Management

The biggest adoption risk is PM resistance to AI-generated outputs —
particularly concern that Mira's reports will be taken as authoritative
without human review. This will be addressed by:

1. **Positioning Mira as a first-draft assistant**, not a replacement for
   PM judgment — all outputs are reviewed before sharing with clients
2. **Showing time savings data** from the pilot phase — concrete evidence
   that Mira saves 6+ hours/week per PM is the most effective adoption driver
3. **Celebrating early wins** — sharing examples of high-quality
   Mira-generated plans and reports in team meetings builds confidence
4. **Making it easy to give feedback** — a simple Slack channel where PMs
   can flag issues ensures continuous improvement and demonstrates that
   feedback leads to actual fixes

---

## 6. Key Lessons Learned

1. **Prompt engineering is not enough for structured data tasks.** The T10
   task counting failure demonstrated that LLMs are unreliable at precise
   counting from raw CSV data — even with explicit counting instructions.
   Moving counting logic to deterministic code (JavaScript) and using the
   LLM only for formatting was the correct architectural decision.

2. **Observability must be connected early, not as an afterthought.** The
   Langfuse connection revealed trace-level insights about routing accuracy
   and token usage that were invisible from outputs alone. Future projects
   will connect observability in Week 1, not Week 5.

3. **Data quality affects output quality more than prompt quality.**
   The escaped `\n` characters in the taskboard string caused more output
   failures than any prompt issue. Validating data format at ingestion time
   is as important as writing good prompts.

4. **Guardrails are the most important part of the prompt.** The vague input
   tests (T2, T4, T6, T9) all passed because every agent prompt included an
   explicit rule for insufficient input. Without these rules, the LLM would
   have fabricated outputs for all four tests.

5. **Router pattern scales well for varied input types.** The 6-route
   dispatcher handled all 12 test cases correctly with zero misroutes.
   For a system with diverse user request types, the router pattern is
   significantly more efficient than a sequential pipeline.