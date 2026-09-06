#!/usr/bin/env python3
import json, os, sys, argparse, urllib.request, urllib.error

def send_campaign(dry_run=True):
    queue_file = "reports/outbound_dispatch_queue.json"
    if not os.path.exists(queue_file):
        print(f"[-] Error: {queue_file} not found.")
        sys.exit(1)

    with open(queue_file, "r", encoding="utf-8") as f:
        queue = json.load(f)

    api_key = os.getenv("RESEND_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "kalen@nomadik.site")

    print("\n" + "="*60)
    print(" NOMADIK SECURITY SENTINEL - OUTBOUND DISPATCH ENGINE")
    print(f" Mode: {'DRY RUN (Simulated)' if dry_run else 'LIVE DISPATCH'}")
    print("="*60)

    sent_count = 0
    for idx, msg in enumerate(queue, start=1):
        to_email = msg["to"]
        subject = msg["subject"]
        body = msg["body"]
        role = msg["role_segment"]
        tier = msg["payment_tier"]

        if dry_run or not api_key:
            print(f"[{idx}/{len(queue)}] [SIMULATED] -> {to_email} ({role} | {tier})")
            print(f"      Subject: {subject}")
            print("      Status : SUCCESS (Dry-Run Logged)")
            msg["status"] = "SIMULATED_SENT"
            sent_count += 1
        else:
            payload = {
                "from": sender_email,
                "to": [to_email],
                "subject": subject,
                "text": body
            }
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    print(f"[{idx}/{len(queue)}] [LIVE SENT] -> {to_email} (HTTP {resp.status})")
                    msg["status"] = "SENT_LIVE"
                    sent_count += 1
            except urllib.error.HTTPError as e:
                print(f"[{idx}/{len(queue)}] [FAILED] -> {to_email} (HTTP {e.code}: {e.reason})")
                msg["status"] = f"FAILED_{e.code}"

    with open("reports/outbound_dispatch_queue.json", "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2)

    print("="*60)
    print(f"[✓] Dispatch complete: {sent_count}/{len(queue)} messages processed.")
    print("="*60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outbound Dispatch Engine")
    parser.add_argument("--live", action="store_true", help="Execute live email sending via Resend API")
    args = parser.parse_args()

    send_campaign(dry_run=not args.live)
