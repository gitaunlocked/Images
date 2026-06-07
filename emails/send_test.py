#!/usr/bin/env python3
"""One-off HTML email sender via any SMTP provider.

Gmail (default, backward-compatible):
  GMAIL_USER="you@gmail.com" GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx" \
  python3 send_test.py <recipient> <campus>

Brevo / SES / Mailgun / any SMTP relay (recommended to avoid Gmail throttling):
  SMTP_HOST="smtp-relay.brevo.com" SMTP_PORT=587 \
  SMTP_USER="your-login@example.com" SMTP_PASSWORD="your-smtp-key" \
  FROM_EMAIL="verified-sender@yourdomain.com" \
  python3 send_test.py <recipient> <campus>

campus: bhu | bhilai | kanpur | palakkad | agartala | calicut

Credentials are read from environment variables only (never hardcoded).
"""
import os
import sys
import ssl
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid

_SUBJECT = "Success Engineering | AI, Careers & the Human Edge | A Multi-IIT & NIT Program"
CAMPAIGNS = {
    "bhu":      ("email-iit-bhu.html", _SUBJECT),
    "bhilai":   ("email-iit-bh.html",  _SUBJECT),
    "kanpur":   ("email-iitk.html",    _SUBJECT),
    "palakkad": ("email-iit-pkd.html", _SUBJECT),
    "agartala": ("email-nita.html",    _SUBJECT),
    "calicut":  ("email-nitc.html",    _SUBJECT),
    "jammu":    ("email-iit-jammu.html", _SUBJECT),
    "cu":       ("email-cu.html",       _SUBJECT),
    "rgipt":    ("email-rgipt.html",    _SUBJECT),
}

FROM_NAME = "Success Engineering | Gita Unlocked"

CDN = "https://cdn.jsdelivr.net/gh/gitaunlocked/Images@main"
POSTERS = {
    "bhu":      f"{CDN}/iit-bhu-v2.png",
    "bhilai":   f"{CDN}/iit-bh.png",
    "kanpur":   f"{CDN}/iitk-v3.png",
    "palakkad": f"{CDN}/iit-pkd.png",
    "agartala": f"{CDN}/nita.png",
    "calicut":  f"{CDN}/nitc.png",
    "jammu":    f"{CDN}/iit-jammu.png",
    "cu":       f"{CDN}/cu.png",
    "rgipt":    f"{CDN}/rgipt.png",
}
# Campuses whose poster/body lists Mr. Vaibhav Joshi as a 4th speaker.
WITH_VAIBHAV = {"bhilai", "palakkad", "agartala", "calicut", "jammu", "cu", "rgipt"}
# Campuses with a custom (non IIT/NIT) access-codes block.
CUSTOM_CODES = {
    "cu": [
        ("Chandigarh University", "CU26_SE"), ("IIT Kanpur", "IITK26_SE"),
        ("IIT BHU", "IITBHU26_SE"), ("IIIT Lucknow", "IIITL26_SE"),
        ("HBTU Kanpur", "HBTU26_SE"), ("NIT Allahabad", "NITA26_SE"),
    ],
    "rgipt": [
        ("RGIPT", "RGIPT26_SE"), ("Chandigarh University", "CU26_SE"),
        ("IIT Kanpur", "IITK26_SE"), ("IIT BHU", "IITBHU26_SE"),
        ("IIIT Lucknow", "IIITL26_SE"), ("HBTU Kanpur", "HBTU26_SE"),
        ("NIT Allahabad", "NITA26_SE"),
    ],
}


def build_plaintext(campus):
    """Full plain-text version so strict gateways see real content,
    not just an 'enable HTML' placeholder (a common spam signal)."""
    speakers = [
        "- Mr. Gaurav Rai - Senior Product Manager, Microsoft Copilot (Seattle)",
        "- Mr. Samyak Jain - PhD Researcher in AI, UC Berkeley",
        "- Mr. Yashas Tadikamalla - AI Engineer, Texas Instruments | BTech AI, IIT Hyderabad",
    ]
    if campus in WITH_VAIBHAV:
        speakers.append("- Mr. Vaibhav Joshi - AI Operations Specialist, GlobalLogic | MBA, IESEG Paris")
    poster = POSTERS.get(campus, "https://gitaunlocked.com/")
    if campus in CUSTOM_CODES:
        codes_title = "A MULTI-PREMIER COLLEGE INITIATIVE - INSTITUTIONAL ACCESS CODES"
        codes_block = "\n".join(f"{name}: {code}" for name, code in CUSTOM_CODES[campus])
    else:
        codes_title = "A MULTI-IIT & NIT INITIATIVE - INSTITUTIONAL ACCESS CODES"
        codes_block = (
            "IIT Bombay: IITB26_SE      IIT Delhi: IITD26_SE\n"
            "IIT Kanpur: IITK26_SE      IIT Guwahati: IITG26_SE\n"
            "IIT Palakkad: IITPKD26_SE  IIT BHU: IITBHU26_SE\n"
            "IIT Jammu: IITJ26_SE       IIT Bhilai: IITBH26_SE\n"
            "NIT Trichy: NITT26_SE      NIT Calicut: NITC26_SE\n"
            "NIT Agartala: NITA26_SE    NIT Silchar: NITS26_SE"
        )
    return f"""Dear Students,

As AI continues to reshape industries, hiring and careers, success in the future
will require far more than technical expertise. The ability to learn continuously,
think clearly, make sound decisions and develop uniquely human strengths is
becoming increasingly important.

Success Engineering is your opportunity to learn from accomplished professionals
and explore the skills, mindsets and human qualities that drive long-term success
in a rapidly changing world.

SUCCESS ENGINEERING - Building the Human Edge in the Age of AI
A 3-part live interactive series with IIT alumni, industry leaders and global
technology professionals.

LEARN FROM INDUSTRY LEADERS
{chr(10).join(speakers)}

THREE POWERFUL SESSIONS
01. The Success Code - AI, Careers & Future Readiness  (7 June)
02. The Missing Dimension - Human Potential Beyond IQ  (10 June)
03. The Human Edge - What Makes Us Stand Out?  (13 June)

WHAT YOU WILL GAIN
- Career & Internship insights from industry leaders
- Networking with IIT alumni & professionals
- Certificate of Participation
- Exciting prizes & quizzes
- Sponsored trip opportunities
- Human Potential Assessment Report

{codes_title}
{codes_block}
Use the code corresponding to your institution during registration.

Mode: Online (Zoom)  |  Starts: 7 June 2026  |  Fee: FREE with your institutional code

REGISTER FREE: https://gitaunlocked.com/
View the event poster: {poster}

--
Gita Unlocked
Empowering youth through timeless wisdom, modern insights and meaningful growth.
Register at https://gitaunlocked.com/  (c) 2026 Gita Unlocked.
"""


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 send_test.py <recipient> <campus: bhu|bhilai|kanpur|palakkad>")

    recipient, campus = sys.argv[1], sys.argv[2].lower()
    if campus not in CAMPAIGNS:
        sys.exit(f"Unknown campus '{campus}'. Choose: {', '.join(CAMPAIGNS)}")

    # SMTP config: defaults to Gmail, override via SMTP_* for any provider.
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    user = os.environ.get("SMTP_USER") or os.environ.get("GMAIL_USER")
    app_pw = os.environ.get("SMTP_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD")
    if not user or not app_pw:
        sys.exit("Set SMTP_USER/SMTP_PASSWORD (or GMAIL_USER/GMAIL_APP_PASSWORD).")
    app_pw = app_pw.replace(" ", "")  # Gmail shows app passwords with spaces
    # Visible From address (Brevo etc. require a verified sender, not the login).
    from_email = os.environ.get("FROM_EMAIL", user)

    html_file, subject = CAMPAIGNS[campus]
    subject = os.environ.get("SUBJECT", subject)  # optional override
    cc = os.environ.get("GMAIL_CC", "").strip()
    cc_list = [a.strip() for a in cc.split(",") if a.strip()]

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, html_file), "r", encoding="utf-8") as fh:
        html = fh.read()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{from_email}>"
    msg["To"] = recipient
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    # Standard outreach headers (improve deliverability / pass spam checks).
    msg["Message-ID"] = make_msgid(domain=from_email.split("@")[-1])
    msg["List-Unsubscribe"] = f"<mailto:{from_email}?subject=unsubscribe>"
    msg.set_content(build_plaintext(campus))
    msg.add_alternative(html, subtype="html")

    recipients = [recipient] + cc_list
    context = ssl.create_default_context()
    debug = bool(os.environ.get("SMTP_DEBUG"))
    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            if debug:
                server.set_debuglevel(1)
            server.login(user, app_pw)
            refused = server.send_message(msg, to_addrs=recipients)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if debug:
                server.set_debuglevel(1)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(user, app_pw)
            refused = server.send_message(msg, to_addrs=recipients)
    if refused:
        print("REFUSED recipients:", refused)
    print(f"Sent '{campus}' email to {recipient} via {smtp_host}"
          + (f" (cc: {', '.join(cc_list)})" if cc_list else ""))


if __name__ == "__main__":
    main()
