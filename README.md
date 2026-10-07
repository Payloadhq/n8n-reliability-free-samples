# n8n Reliability Guard — Free Sample Workflows

*by Payload*

Two genuinely useful, fully standalone n8n workflows — **free samples** from the
**n8n Production AI Agent Reliability Kit**
([$99 one-time](https://payloadtools.gumroad.com/l/n8n-agent-reliability-kit)).

These samples are extracts from an earlier kit version; the paid kit is the current version.

## Who it's for

Anyone running AI agents on n8n who wants production reliability patterns — silent-failure alerting and API timeout resilience — before buying the full kit.

## What you receive (free)

Two import-ready n8n workflow JSON files, in this repo, free to use:

Import each JSON into n8n (**Workflows → Import from File**). No credentials,
no setup accounts, no external dependencies beyond the webhook URL you paste
in the alert dispatcher.

### 1. Failure Alert Dispatcher — `free-failure-alert-dispatcher.json`

Catches failures across your n8n workflows and alerts you instead of letting
agents fail silently.

**Flow:** On Execution Failure → Extract Failure Context → Is Manual Test Run?
→ Build Alert Payload → Send Alert Webhook → Alert Sent
(manual test runs are skipped).

**Setup:**
1. Create an incoming webhook URL (Slack, Discord, PagerDuty, Opsgenie).
2. In the **Build Alert Payload** node, replace `PASTE_YOUR_WEBHOOK_URL_HERE`.
3. In each workflow you want to monitor: **Workflow Settings → Error Workflow**
   → select this workflow.
4. Trigger a failure and confirm the alert arrives.

### 2. HTTP Timeout Circuit Breaker — `free-http-timeout-circuit-breaker.json`

Stops one slow API from taking down your whole agent run.

**Flow:** Start → Fragile API Call (4s timeout, continue-on-error)
→ Classify Outcome → Call Succeeded? → Use Live Data **or**
Degraded-Mode Fallback → Use Fallback.

**Try it:** Execute the workflow. It calls `https://httpbin.org/delay/8` with
a 4-second timeout, so it deterministically times out and takes the fallback
path — then replace the URL with your own fragile API and put your real
fallback (cached value, safe default, queued retry) in the fallback node.

## What these free samples do NOT include

- These are two of the workflows in the paid kit. The full
  [$99 kit](https://payloadtools.gumroad.com/l/n8n-agent-reliability-kit) adds:
  - Tool guardrail subworkflow, LLM cost meter, structured-output validator
  - Empty-result retry handoff, subworkflow debug tracer
  - Iteration-cap kill-switch, nightly reliability digest, agent output sanitizer
  - A failure simulator to test your guardrails before production
  - An eval runner + readiness scoring with PDF reports
- The samples are extracts from an earlier kit version. The paid kit is the current version with updates.

## Price

**Free.** These two workflows cost nothing and need no purchase.

The full n8n Production AI Agent Reliability Kit is **$99 one-time**:
https://payloadtools.gumroad.com/l/n8n-agent-reliability-kit

## Support

- Support: kylers.partners@gmail.com
- "Small software that earns its keep."

## Payload Tools ecosystem

- **n8n Production AI Agent Reliability Kit** — https://payloadtools.gumroad.com/l/n8n-agent-reliability-kit
- **All Payload products** — https://payloadtools.gumroad.com
- **More Payload repos** — https://github.com/Payloadhq

---

**Payload** — small, sharp tools for developers.
Developer portal: https://payloadhq.github.io/ ·
All products: https://payloadtools.gumroad.com/ ·
Contact: kylers.partners@gmail.com

---

**More from Payload** · [payloadhq.github.io](https://payloadhq.github.io/) · [all Payload repos](https://github.com/Payloadhq)

Related: [n8n-workflow-linter](https://github.com/Payloadhq/n8n-workflow-linter)
