#!/usr/bin/env python3
import csv, json, os

PAYMENT_LINKS = {
    "Starter": "https://nomadik.site/api/checkout?plan=starter",
    "Pro Enterprise": "https://nomadik.site/api/checkout?plan=pro"
}

MESSAGING_MATRIX = {
    "DevOps": {
        "subject": "Eliminating CI/CD security build blockers at {company}",
        "template": (
            "Hi {first_name},\n\n"
            "Saw your team is scaling infrastructure at {company}. Most platform teams lose hours to false-positive scanner blocks.\n\n"
            "Nomadik Security Sentinel embeds CodeMender into your git pipeline to score vulnerability reachability at runtime and generate patch PRs autonomously—with zero source code retention.\n\n"
            "You can spin up an automated pipeline audit with our Starter Plan here:\n"
            "{checkout_url}\n\n"
            "Best,\n"
            "Kalen Vandenbos\n"
            "Nomadik Security Operations"
        )
    },
    "SecOps": {
        "subject": "Reducing CVE alert fatigue & passkey threat detection at {company}",
        "template": (
            "Hi {first_name},\n\n"
            "Handling SOC triage for high-volume CVE streams creates massive operational overhead.\n\n"
            "Nomadik Security Sentinel correlates Wazuh EDR telemetry against active exploits (including CVE-2026-34348 passkey replay detection) and uses Chokepoint Finder to collapse thousands of noisy alerts into single-action remediation tasks.\n\n"
            "We are onboarding 3 enterprise design cohorts for our 30-day pilot:\n"
            "{checkout_url}\n\n"
            "Best,\n"
            "Kalen Vandenbos\n"
            "Nomadik Security Operations"
        )
    },
    "CISO": {
        "subject": "Cryptographic compliance evidence & usage-based security for {company}",
        "template": (
            "Hi {first_name},\n\n"
            "Preparing audit-ready proof for SOC 2 Type II, ISO 27001, and multi-cloud environments (AWS/GCP) shouldn't require unpredictable annual software licensing.\n\n"
            "Nomadik Security Sentinel generates deterministic, auditor-ready evidence sidecars while scaling costs via usage-based Singularity Credits.\n\n"
            "Review our enterprise tier and pilot terms here:\n"
            "{checkout_url}\n\n"
            "Best,\n"
            "Kalen Vandenbos\n"
            "Nomadik Security Operations"
        )
    }
}

def build_dispatch_queue():
    queue = []
    for segment in ["DevOps", "SecOps", "CISO"]:
        filename = f"leads_{segment.lower()}.csv"
        if not os.path.exists(filename):
            continue
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                first_name = row.get("first_name") or (row.get("name", "").split()[0] if row.get("name") else "")
                plan = "Starter" if segment == "DevOps" else "Pro Enterprise"
                url = PAYMENT_LINKS[plan]
                cfg = MESSAGING_MATRIX[segment]
                body = cfg["template"].format(
                    first_name=first_name,
                    company=row["company"],
                    checkout_url=url
                )
                subject = cfg["subject"].format(company=row["company"])
                queue.append({
                    "lead_id": row["lead_id"],
                    "to": row["email"],
                    "role_segment": segment,
                    "subject": subject,
                    "body": body,
                    "payment_tier": plan,
                    "checkout_url": url,
                    "status": "QUEUED"
                })

    with open("reports/outbound_dispatch_queue.json", "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)

    print(f"[✓] Outbound dispatch queue built: {len(queue)} messages ready.")

if __name__ == "__main__":
    build_dispatch_queue()
