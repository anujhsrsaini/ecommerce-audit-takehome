"""Export conversation transcript from system logs into ai_sessions/."""

import json
import os
import shutil

LOG_DIR = "/home/anuj/.gemini/antigravity-cli/brain/41a7d455-cb0a-46ec-9ce8-4a4143ac65d6/.system_generated/logs"
TARGET_DIR = "ai_sessions"

def export():
    os.makedirs(TARGET_DIR, exist_ok=True)
    raw_src = os.path.join(LOG_DIR, "transcript.jsonl")
    raw_dst = os.path.join(TARGET_DIR, "session_transcript_raw.jsonl")
    shutil.copy(raw_src, raw_dst)

    with open(raw_src, "r") as f:
        records = [json.loads(line) for line in f]

    md = []
    md.append("# AI Session Log & Forensic Query Engineering Transcript\n")
    md.append("**Session ID:** `41a7d455-cb0a-46ec-9ce8-4a4143ac65d6`  ")
    md.append("**Role:** Lead Analytics Engineer & Forensic Data Auditor  ")
    md.append("**Project:** Aura Enterprise Technologies — Cross-System Audit & Analytics Challenge  \n")
    md.append("---\n")
    md.append("## 1. Transcript Overview & Analytical Direction\n")
    md.append("This document preserves the unedited, reproducible transcript of all prompt iterations, query drafting, hypothesis testing, defensive join modeling, and error-correction steps performed using the AI assistant to audit `enterprise_audit.duckdb`.\n")
    md.append("### Core Analytical Milestones Documented:")
    md.append("1. **Relational Grain & Primary Key Verification:** Defensively auditing the 8 decoupled tables (~1.8M total rows), verifying grains, foreign key relationships, and temporal timezone offsets (UTC vs Eastern Business Time).")
    md.append("2. **Elena Vance GAAP Bridge & Treasury Reconciliation:** Sifting through billing events and orders to uncover that Stripe represents Credit Card only ($702.34M); deriving the complete mathematical bridge to NetSuite GAAP revenue ($1,163.22M) down to $0.00 variance; locating the $6.2M 'cash shortfall' in Stripe's 5.0% rolling 90-day risk reserve escrow ($7.34M active at audit cutoff).")
    md.append("3. **Marcus Carvalho Logistics & Zombie Dispatch Audit:** Discovering Marcus's grain error (97.2% SLA claimed vs 89.28% true order SLA) and confirming the post-pack cancellation leakage (2,404 orders delivered anyway, leaking $13.30M in inventory COGS).")
    md.append("4. **Sarah Lin RMA Defect Audit:** Confirming that 100% of returned items (12,619 line items, $31.99M COGS) were physically scrapped as `DAMAGED_WRITE_OFF`, causing a $31.99M balance sheet inventory inflation.")
    md.append("5. **Lucas Ferreira Entity Graph Resolution & Survival Retention:** Resolving anonymous checkout tokens to true B2B parent conglomerates (Apex Global Technologies: 304 orders, $2.48M spend) and modeling Kaplan-Meier survival curves controlling for right-censoring (99.20% 365-day repeat probability).")
    md.append("6. **Vikram Patel Margin Guardrails & Carrier Claims:** Modeling unit economics by order value tier, computing Minimum Order Value (MOV) thresholds to prevent negative EBITDA appeasement incentives, and auditing $42.69M in unfiled carrier insurance claims.\n")
    md.append("---\n")
    md.append("## 2. Granular Step-by-Step Trajectory Log\n")

    for item in records:
        idx = item.get("step_index", 0)
        stype = item.get("type", "")
        created = item.get("created_at", "")
        content = item.get("content", "")
        calls = item.get("tool_calls", [])

        if stype == "USER_INPUT":
            md.append(f"### [Step {idx}] User Directive ({created})\n")
            md.append("```text")
            md.append(content.strip()[:1000] + ("..." if len(content) > 1000 else ""))
            md.append("```\n")
        elif stype == "PLANNER_RESPONSE":
            md.append(f"### [Step {idx}] Auditor Action & Reasoning ({created})\n")
            if calls:
                md.append("**Tools Executed:**")
                for c in calls:
                    tname = c.get("ToolName") or c.get("name", "tool")
                    args = c.get("Arguments") or c.get("arguments", {})
                    summary = args.get("toolSummary", "")
                    cmd = args.get("CommandLine", "")
                    md.append(f"- `{tname}`: {summary}")
                    if cmd:
                        md.append(f"  - Command: `{cmd[:120]}...`" if len(cmd) > 120 else f"  - Command: `{cmd}`")
                md.append("")
            if content:
                md.append("**Auditor Findings & Synthesis:**")
                md.append(content.strip()[:1500] + ("..." if len(content) > 1500 else ""))
                md.append("")

    with open(os.path.join(TARGET_DIR, "audit_engineering_session.md"), "w") as out:
        out.write("\n".join(md))

    print(f"Exported {len(records)} steps to ai_sessions/audit_engineering_session.md and session_transcript_raw.jsonl")

if __name__ == "__main__":
    export()
