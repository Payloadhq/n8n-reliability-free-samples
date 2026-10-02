#!/usr/bin/env python3
"""Generate the two free n8n sample workflows. Standalone, no credentials."""

import json
import os
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
KIT_URL = "https://payloadtools.gumroad.com/l/n8n-agent-reliability-kit"
ECOSYSTEM_URL = "https://payloadtools.gumroad.com"


def node(name, ntype, tver, params, pos):
    return {
        "parameters": params,
        "id": str(uuid.uuid4()),
        "name": name,
        "type": ntype,
        "typeVersion": tver,
        "position": list(pos),
    }


def sticky(content, width=560, height=320):
    return node(
        "SETUP — Read Me First",
        "n8n-nodes-base.stickyNote",
        1,
        {"content": content, "height": height, "width": width, "color": 4},
        [-720, 160],
    )


SETUP_ALERT = """## FREE SAMPLE — Failure Alert Dispatcher

This is a free sample from the **n8n Production AI Agent Reliability Kit**
($99, one-time) — the full kit includes 10 importable workflows, a failure
simulator, an eval runner, readiness scoring, and PDF reports:
{kit}

Get the full kit: {kit}
More Payload tools: {eco}

### What this workflow does
When any n8n workflow fails, this workflow runs as its **Error Workflow**,
extracts the failure context (workflow name, execution id, failed node,
error message), skips alerts for manual test runs, and POSTs a JSON alert
to your webhook (Slack, Discord, PagerDuty, Opsgenie — anything with a URL).

### Setup (2 minutes, no credentials needed)
1. Create a webhook URL at your alerting tool of choice.
2. In the **Build Alert Payload** node, replace `PASTE_YOUR_WEBHOOK_URL_HERE`.
3. In the n8n workflow you want to monitor: open its Settings and set
   **Error Workflow** to this workflow.
4. Trigger a failure (or click Test) and confirm the alert arrives.

The full Reliability Kit adds 8 more workflows on top of this pattern:
guardrailed subworkflows, LLM cost metering, structured-output validation,
retry handoffs, debug tracing, iteration kill-switches, nightly digests,
and output sanitization.
""".format(kit=KIT_URL, eco=ECOSYSTEM_URL)


def build_alert_dispatcher():
    extract_code = """// Extract the failure context n8n passes to an Error Workflow.
const item = $input.first().json;
const exec = item.execution || {};
const workflow = item.workflow || {};
return [{
  json: {
    workflow_name: workflow.name || 'unknown workflow',
    workflow_id: workflow.id || null,
    execution_id: exec.id || null,
    execution_url: exec.url || null,
    execution_mode: exec.mode || 'unknown',
    failed_node: item.nodeName || item.node_name || 'unknown node',
    error_message: (item.error && (item.error.message || item.error.description)) || String(item.error || 'unknown error'),
    failed_at: new Date().toISOString(),
  }
}];"""

    if_params = {
        "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
        "conditions": [
            {
                "id": str(uuid.uuid4()),
                "leftValue": "={{ $json.execution_mode }}",
                "rightValue": "manual",
                "operator": {"type": "string", "operation": "equals", "name": "filter.operator.string.equals"},
            }
        ],
        "combinator": "and",
        "looseTypeValidation": True,
    }

    build_code = """// Build the alert payload. Replace the webhook URL with your own
// (Slack / Discord / PagerDuty / Opsgenie incoming-webhook URL).
const f = $input.first().json;
const alert = {
  text: "n8n workflow FAILED: " + f.workflow_name,
  severity: "high",
  workflow_name: f.workflow_name,
  execution_id: f.execution_id,
  execution_url: f.execution_url,
  failed_node: f.failed_node,
  error_message: f.error_message,
  failed_at: f.failed_at,
};
return [{ json: { webhook_url: "PASTE_YOUR_WEBHOOK_URL_HERE", alert } }];"""

    http_params = {
        "method": "POST",
        "url": "={{ $json.webhook_url }}",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json.alert) }}",
        "options": {"timeout": 10000},
    }

    nodes = [
        sticky(SETUP_ALERT),
        node("On Execution Failure", "n8n-nodes-base.errorTrigger", 1, {}, [-480, 400]),
        node("Extract Failure Context", "n8n-nodes-base.code", 2, {"jsCode": extract_code}, [-240, 400]),
        node("Is Manual Test Run?", "n8n-nodes-base.if", 2, if_params, [0, 400]),
        node("Build Alert Payload", "n8n-nodes-base.code", 2, {"jsCode": build_code}, [0, 160]),
        node("Send Alert Webhook", "n8n-nodes-base.httpRequest", 4.2, http_params, [240, 160]),
        node("Alert Sent", "n8n-nodes-base.noOp", 1, {}, [480, 160]),
        node("Skip Alert (manual run)", "n8n-nodes-base.noOp", 1, {}, [240, 560]),
    ]
    connections = {
        "On Execution Failure": {"main": [[{"node": "Extract Failure Context", "type": "main", "index": 0}]]},
        "Extract Failure Context": {"main": [[{"node": "Is Manual Test Run?", "type": "main", "index": 0}]]},
        "Is Manual Test Run?": {
            "main": [
                [{"node": "Skip Alert (manual run)", "type": "main", "index": 0}],
                [{"node": "Build Alert Payload", "type": "main", "index": 0}],
            ]
        },
        "Build Alert Payload": {"main": [[{"node": "Send Alert Webhook", "type": "main", "index": 0}]]},
        "Send Alert Webhook": {"main": [[{"node": "Alert Sent", "type": "main", "index": 0}]]},
    }
    return {
        "name": "Payload — Failure Alert Dispatcher (FREE SAMPLE)",
        "nodes": nodes,
        "connections": connections,
        "active": False,
        "settings": {"executionOrder": "v1", "timezone": "America/Chicago"},
        "pinData": {},
        "tags": [{"name": "payload"}, {"name": "reliability"}, {"name": "free-sample"}],
    }


SETUP_BREAKER = """## FREE SAMPLE — HTTP Timeout Circuit Breaker

This is a free sample from the **n8n Production AI Agent Reliability Kit**
($99, one-time) — the full kit includes 10 importable workflows, a failure
simulator, an eval runner, readiness scoring, and PDF reports:
{kit}

Get the full kit: {kit}
More Payload tools: {eco}

### What this workflow does
Calls a slow API with a short timeout. If the call times out or errors,
the workflow **does not crash** — it classifies the outcome and routes to
a degraded-mode fallback (cached/stale data, a safe default, or a queued
retry) instead of failing your agent mid-run.

### Setup (no credentials needed)
1. Click **Execute** — the demo calls https://httpbin.org/delay/8 with a
   4-second timeout, so it deterministically times out and takes the
   fallback path.
2. Replace the URL with your own fragile API, set the timeout that fits
   your SLA, and put your real fallback logic in the
   **Degraded-Mode Fallback** node.
3. Copy this pattern in front of every external call your agents depend on.

The full Reliability Kit adds 8 more workflows: failure alerting, tool
guardrails, LLM cost metering, structured-output validation, retry
handoffs, debug tracing, iteration kill-switches, and nightly digests.
""".format(kit=KIT_URL, eco=ECOSYSTEM_URL)


def build_circuit_breaker():
    classify_code = """// Classify the HTTP outcome. The HTTP node is set to continue on
// error, so a timeout lands here as an error payload instead of a crash.
const j = $input.first().json;
if (j && j.error) {
  return [{ json: { ok: false, reason: "http_error", detail: String(j.error.message || j.error).slice(0, 300) } }];
}
return [{ json: { ok: true, data: j } }];"""

    fallback_code = """// DEGRADED MODE: the live API did not answer in time.
// Put your real fallback here: cached value, stale snapshot, safe default,
// or a queue entry for later retry. This demo returns a safe default.
const c = $input.first().json;
return [{
  json: {
    mode: "degraded_fallback",
    reason: c.reason,
    detail: c.detail,
    data: { note: "fallback data — live API timed out", as_of: new Date().toISOString() },
  }
}];"""

    if_params = {
        "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
        "conditions": [
            {
                "id": str(uuid.uuid4()),
                "leftValue": "={{ $json.ok }}",
                "rightValue": True,
                "operator": {"type": "boolean", "operation": "true", "singleValue": True},
            }
        ],
        "combinator": "and",
        "looseTypeValidation": True,
    }

    http_params = {
        "method": "GET",
        "url": "https://httpbin.org/delay/8",
        "options": {"timeout": 4000},
        "onError": "continueErrorOutput",
    }

    nodes = [
        sticky(SETUP_BREAKER),
        node("Start", "n8n-nodes-base.manualTrigger", 1, {}, [-480, 400]),
        node("Fragile API Call", "n8n-nodes-base.httpRequest", 4.2, http_params, [-240, 400]),
        node("Classify Outcome", "n8n-nodes-base.code", 2, {"jsCode": classify_code}, [0, 400]),
        node("Call Succeeded?", "n8n-nodes-base.if", 2, if_params, [240, 400]),
        node("Use Live Data", "n8n-nodes-base.noOp", 1, {}, [480, 160]),
        node("Degraded-Mode Fallback", "n8n-nodes-base.code", 2, {"jsCode": fallback_code}, [480, 560]),
        node("Use Fallback", "n8n-nodes-base.noOp", 1, {}, [720, 560]),
    ]
    connections = {
        "Start": {"main": [[{"node": "Fragile API Call", "type": "main", "index": 0}]]},
        "Fragile API Call": {"main": [[{"node": "Classify Outcome", "type": "main", "index": 0}]]},
        "Classify Outcome": {"main": [[{"node": "Call Succeeded?", "type": "main", "index": 0}]]},
        "Call Succeeded?": {
            "main": [
                [{"node": "Use Live Data", "type": "main", "index": 0}],
                [{"node": "Degraded-Mode Fallback", "type": "main", "index": 0}],
            ]
        },
        "Degraded-Mode Fallback": {"main": [[{"node": "Use Fallback", "type": "main", "index": 0}]]},
    }
    return {
        "name": "Payload — HTTP Timeout Circuit Breaker (FREE SAMPLE)",
        "nodes": nodes,
        "connections": connections,
        "active": False,
        "settings": {"executionOrder": "v1", "timezone": "America/Chicago"},
        "pinData": {},
        "tags": [{"name": "payload"}, {"name": "reliability"}, {"name": "free-sample"}],
    }


def main():
    for fname, builder in [
        ("free-failure-alert-dispatcher.json", build_alert_dispatcher),
        ("free-http-timeout-circuit-breaker.json", build_circuit_breaker),
    ]:
        wf = builder()
        path = os.path.join(HERE, fname)
        with open(path, "w") as f:
            json.dump(wf, f, indent=2)
            f.write("\n")
        print("wrote", path, "-", len(wf["nodes"]), "nodes")


if __name__ == "__main__":
    main()
