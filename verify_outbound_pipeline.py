#!/usr/bin/env python3
import os, csv, json, re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
VALID_ROLE_SEGMENTS = {"DevOps", "SecOps", "CISO"}
REQUIRED_FIELDS = [
    "lead_id", "first_name", "last_name", "email", "company",
    "domain", "role_segment", "title", "icp_tier", "pain_point",
    "hook_angle", "cta_type", "payment_link_tier", "lead_status"
]

def verify_and_segment(csv_path="leads.csv"):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Database {csv_path} not found.")

    with open(csv_path, "r", encoding="utf-8") as f:
        records = list(csv.DictReader(f))

    errors = []
    segmented = {seg: [] for seg in VALID_ROLE_SEGMENTS}

    for idx, row in enumerate(records, start=1):
        for field in REQUIRED_FIELDS:
            if not row.get(field) or not row[field].strip():
                errors.append(f"Row {idx}: Missing '{field}'")
        
        email = row.get("email", "").strip()
        if email and not EMAIL_REGEX.match(email):
            errors.append(f"Row {idx}: Invalid email '{email}'")

        seg = row.get("role_segment", "").strip()
        if seg not in VALID_ROLE_SEGMENTS:
            errors.append(f"Row {idx}: Invalid segment '{seg}'")
        else:
            segmented[seg].append(row)

    fieldnames = list(records[0].keys())
    for seg, rows in segmented.items():
        with open(f"leads_{seg.lower()}.csv", "w", newline="", encoding="utf-8") as out_f:
            writer = csv.DictWriter(out_f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    report = {
        "status": "VERIFIED_VALID" if not errors else "FAILED",
        "total_evaluated": len(records),
        "hygiene_score": "100%" if not errors else f"{max(0, 100 - len(errors)*10)}%",
        "segment_distribution": {k: len(v) for k, v in segmented.items()},
        "validation_errors": errors
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/outbound_pipeline_verification_report.json", "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=2)

    return report

if __name__ == "__main__":
    rep = verify_and_segment("leads.csv")
    print(f"\n[+] Pipeline Status: {rep['status']} | Hygiene Score: {rep['hygiene_score']}")
    print(f"[+] Total Leads Processed: {rep['total_evaluated']}")
    for k, v in rep["segment_distribution"].items():
        print(f"    - leads_{k.lower()}.csv: {v} records")
