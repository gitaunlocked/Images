#!/usr/bin/env python3
"""One-off HTML email sender via Gmail SMTP (SSL).

Usage:
  GMAIL_USER="you@gmail.com" GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx" \
  python3 send_test.py <recipient> <campus>

campus: bhu | bhilai | kanpur | palakkad

Credentials are read from environment variables only (never hardcoded).
"""
import os
import sys
import ssl
import smtplib
from email.message import EmailMessage

_SUBJECT = "Success Engineering | AI, Careers & the Human Edge | A Multi-IIT & NIT Program"
CAMPAIGNS = {
    "bhu":      ("email-iit-bhu.html", _SUBJECT),
    "bhilai":   ("email-iit-bh.html",  _SUBJECT),
    "kanpur":   ("email-iitk.html",    _SUBJECT),
    "palakkad": ("email-iit-pkd.html", _SUBJECT),
    "agartala": ("email-nita.html",    _SUBJECT),
    "calicut":  ("email-nitc.html",    _SUBJECT),
}

FROM_NAME = "Success Engineering | Gita Unlocked"


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 send_test.py <recipient> <campus: bhu|bhilai|kanpur|palakkad>")

    recipient, campus = sys.argv[1], sys.argv[2].lower()
    if campus not in CAMPAIGNS:
        sys.exit(f"Unknown campus '{campus}'. Choose: {', '.join(CAMPAIGNS)}")

    user = os.environ.get("GMAIL_USER")
    app_pw = os.environ.get("GMAIL_APP_PASSWORD")
    if not user or not app_pw:
        sys.exit("Set GMAIL_USER and GMAIL_APP_PASSWORD environment variables.")
    app_pw = app_pw.replace(" ", "")  # Gmail shows it with spaces

    html_file, subject = CAMPAIGNS[campus]
    subject = os.environ.get("SUBJECT", subject)  # optional override
    cc = os.environ.get("GMAIL_CC", "").strip()
    cc_list = [a.strip() for a in cc.split(",") if a.strip()]

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, html_file), "r", encoding="utf-8") as fh:
        html = fh.read()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{user}>"
    msg["To"] = recipient
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    msg.set_content("Please view this email in an HTML-capable client.")
    msg.add_alternative(html, subtype="html")

    recipients = [recipient] + cc_list
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(user, app_pw)
        server.send_message(msg, to_addrs=recipients)
    print(f"Sent '{campus}' email to {recipient}" + (f" (cc: {', '.join(cc_list)})" if cc_list else ""))


if __name__ == "__main__":
    main()
