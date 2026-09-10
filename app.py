"""
app.py  —  ADJ Technologies Website Backend API
=================================================
Flask application that serves the HTML pages and handles:
  POST /api/contact        — Contact form → email to aneeshkannan0013@gmail.com
  POST /api/career-notify  — Career notify form → email to aneeshkannan0013@gmail.com
  GET  /api/health         — Health-check ping

HOW TO RUN
──────────
1. Install dependencies:
       pip install flask flask-cors flask-mail

2. Set your Gmail App Password in the CONFIG block below
   (Generate one at: https://myaccount.google.com/apppasswords)

3. Start the server:
       python app.py

   The server runs on http://127.0.0.1:5000
   Your HTML pages can be opened directly in the browser (same-origin or
   adjust CORS origins below for a live domain).
"""

import os
import logging
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message

# ─── APP SETUP ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="html", static_url_path="")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ─── CORS (allow your domain in production) ────────────────────────────────────
CORS(app, resources={r"/api/*": {"origins": "*"}})


# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIG  —  update these values before running
# ═══════════════════════════════════════════════════════════════════════════════

# Recipient — enquiry emails land here
OWNER_EMAIL = "aneeshkannan0013@gmail.com"

# Sender Gmail account  (the account that sends the mail)
SENDER_EMAIL    = "aneeshkannan0013@gmail.com"   # your Gmail address
SENDER_NAME     = "ADJ Technologies Website"

# Gmail App Password  (NOT your normal Gmail password)
# Generate at: https://myaccount.google.com/apppasswords
# You can also set this via environment variable: GMAIL_APP_PASSWORD=xxxx
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "ooux zrcu pkih dpsw")

# ───────────────────────────────────────────────────────────────────────────────

app.config.update(
    MAIL_SERVER          = "smtp.gmail.com",
    MAIL_PORT            = 587,
    MAIL_USE_TLS         = True,
    MAIL_USERNAME        = SENDER_EMAIL,
    MAIL_PASSWORD        = GMAIL_APP_PASSWORD,
    MAIL_DEFAULT_SENDER  = (SENDER_NAME, SENDER_EMAIL),
    MAIL_MAX_EMAILS      = None,
)

mail = Mail(app)


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_field(source: dict, *keys: str, default: str = "—") -> str:
    """Return the first non-empty value from source for any of the given keys."""
    for key in keys:
        val = source.get(key, "").strip()
        if val:
            return val
    return default


def _send_email(subject: str, html_body: str, reply_to: str | None = None) -> bool:
    """Send an email to OWNER_EMAIL. Returns True on success."""
    try:
        msg = Message(
            subject    = subject,
            recipients = [OWNER_EMAIL],
            html       = html_body,
        )
        if reply_to:
            msg.reply_to = reply_to
        mail.send(msg)
        log.info("Email sent → %s | subject: %s", OWNER_EMAIL, subject)
        return True
    except Exception as exc:
        log.error("Failed to send email: %s", exc, exc_info=True)
        return False


# ═══════════════════════════════════════════════════════════════════════════════
#  STATIC FILE SERVING  (serves the HTML pages at the root URL)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return app.send_static_file("index.html")


# ═══════════════════════════════════════════════════════════════════════════════
#  API  —  POST /api/contact
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/contact", methods=["POST"])
def api_contact():
    """
    Accepts JSON or multipart/form-data from the contact form.
    Sends an enquiry email to OWNER_EMAIL.
    """
    # ── parse payload ──────────────────────────────────────────────────────────
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    name         = _get_field(data, "name")
    email        = _get_field(data, "email")
    mobile       = _get_field(data, "mobile")
    country_code = _get_field(data, "country_code", default="+91")
    service      = _get_field(data, "service")
    subject_line = _get_field(data, "subject", default="(no subject)")
    message      = _get_field(data, "message")
    timestamp    = datetime.now().strftime("%d %b %Y, %I:%M %p IST")

    # ── basic validation ───────────────────────────────────────────────────────
    if name == "—" or email == "—" or message == "—":
        return jsonify(success=False, message="Name, email and message are required."), 400

    # ── build HTML email ───────────────────────────────────────────────────────
    phone_display = f"{country_code} {mobile}" if mobile != "—" else "Not provided"

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fb; margin: 0; padding: 0; }}
        .wrap {{ max-width: 600px; margin: 32px auto; background: #ffffff; border-radius: 12px;
                 box-shadow: 0 4px 24px rgba(0,0,0,0.08); overflow: hidden; }}
        .header {{ background: #08080D; padding: 28px 36px; }}
        .header h1 {{ color: #E8431A; font-size: 22px; margin: 0 0 4px; letter-spacing: -0.5px; }}
        .header p  {{ color: #A8B4CC; font-size: 12px; margin: 0; letter-spacing: 0.06em; text-transform: uppercase; }}
        .body {{ padding: 32px 36px; }}
        .row {{ display: flex; margin-bottom: 18px; border-bottom: 1px solid #f0f0f0; padding-bottom: 14px; }}
        .row:last-child {{ border-bottom: none; }}
        .label {{ font-size: 11px; font-weight: 600; color: #8a94a8; text-transform: uppercase;
                  letter-spacing: 0.08em; width: 130px; flex-shrink: 0; padding-top: 2px; }}
        .value {{ font-size: 15px; color: #1a1a2e; line-height: 1.6; word-break: break-word; }}
        .message-box {{ background: #f8f9fc; border-left: 3px solid #E8431A; border-radius: 0 8px 8px 0;
                        padding: 16px 20px; font-size: 14px; color: #2d3250; line-height: 1.75;
                        white-space: pre-wrap; }}
        .footer {{ background: #f8f9fc; padding: 18px 36px; font-size: 11px; color: #aab0be;
                   border-top: 1px solid #eef0f4; }}
        .badge {{ display: inline-block; background: #fff3ef; color: #E8431A; border: 1px solid #f5c4b5;
                  border-radius: 100px; padding: 3px 12px; font-size: 12px; font-weight: 600; }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="header">
          <h1>🔔 New Enquiry — ADJ Technologies</h1>
          <p>Website Contact Form · {timestamp}</p>
        </div>
        <div class="body">
          <div class="row">
            <span class="label">Name</span>
            <span class="value"><strong>{name}</strong></span>
          </div>
          <div class="row">
            <span class="label">Email</span>
            <span class="value"><a href="mailto:{email}" style="color:#E8431A;">{email}</a></span>
          </div>
          <div class="row">
            <span class="label">Phone</span>
            <span class="value">{phone_display}</span>
          </div>
          <div class="row">
            <span class="label">Service</span>
            <span class="value"><span class="badge">{service}</span></span>
          </div>
          <div class="row">
            <span class="label">Subject</span>
            <span class="value">{subject_line}</span>
          </div>
          <div class="row" style="flex-direction:column;">
            <span class="label" style="margin-bottom:10px;">Message</span>
            <div class="message-box">{message}</div>
          </div>
        </div>
        <div class="footer">
          This email was sent automatically from the ADJ Technologies website contact form.<br>
          Reply directly to this email to respond to <strong>{name}</strong>.
        </div>
      </div>
    </body>
    </html>
    """

    email_subject = f"[ADJ Website] New Enquiry from {name} — {service}"
    ok = _send_email(email_subject, html_body, reply_to=email)

    if ok:
        return jsonify(success=True, message="Your message has been sent successfully!"), 200
    else:
        # Still return 200 to the user — log the failure server-side
        log.warning("Email delivery failed for enquiry from %s <%s>", name, email)
        return jsonify(success=True, message="Message received. We'll be in touch soon."), 200


# ═══════════════════════════════════════════════════════════════════════════════
#  API  —  POST /api/career-notify
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/career-notify", methods=["POST"])
def api_career_notify():
    """
    Accepts JSON or form-data from the career page notification form.
    Sends a notification email to OWNER_EMAIL.
    """
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    name      = _get_field(data, "name")
    email     = _get_field(data, "email")
    phone     = _get_field(data, "phone", "mobile", default="Not provided")
    role      = _get_field(data, "role", default="Not specified")
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p IST")

    if name == "—" or email == "—":
        return jsonify(success=False, message="Name and email are required."), 400

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fb; margin: 0; padding: 0; }}
        .wrap {{ max-width: 560px; margin: 32px auto; background: #ffffff; border-radius: 12px;
                 box-shadow: 0 4px 24px rgba(0,0,0,0.08); overflow: hidden; }}
        .header {{ background: #08080D; padding: 28px 36px; }}
        .header h1 {{ color: #22C55E; font-size: 20px; margin: 0 0 4px; }}
        .header p  {{ color: #A8B4CC; font-size: 12px; margin: 0; text-transform: uppercase; letter-spacing: 0.06em; }}
        .body {{ padding: 28px 36px; }}
        .row {{ margin-bottom: 14px; padding-bottom: 14px; border-bottom: 1px solid #f0f0f0; }}
        .row:last-child {{ border-bottom: none; }}
        .label {{ font-size: 11px; font-weight: 600; color: #8a94a8; text-transform: uppercase; letter-spacing: 0.08em; }}
        .value {{ font-size: 15px; color: #1a1a2e; margin-top: 4px; }}
        .footer {{ background: #f8f9fc; padding: 16px 36px; font-size: 11px; color: #aab0be; border-top: 1px solid #eef0f4; }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="header">
          <h1>💼 Career Notification — ADJ Technologies</h1>
          <p>Job Alert Registration · {timestamp}</p>
        </div>
        <div class="body">
          <div class="row"><div class="label">Name</div><div class="value"><strong>{name}</strong></div></div>
          <div class="row"><div class="label">Email</div><div class="value"><a href="mailto:{email}" style="color:#E8431A;">{email}</a></div></div>
          <div class="row"><div class="label">Phone</div><div class="value">{phone}</div></div>
          <div class="row"><div class="label">Interested Role</div><div class="value">{role}</div></div>
        </div>
        <div class="footer">
          This person registered to be notified when ADJ Technologies is hiring.
          Reach out to <strong>{name}</strong> directly at <a href="mailto:{email}">{email}</a>.
        </div>
      </div>
    </body>
    </html>
    """

    email_subject = f"[ADJ Careers] Job Alert Registration — {name} ({role})"
    ok = _send_email(email_subject, html_body, reply_to=email)

    if ok:
        return jsonify(success=True, message="We've saved your details — we'll reach out when we're hiring!"), 200
    else:
        return jsonify(success=True, message="Registered successfully!"), 200


# ═══════════════════════════════════════════════════════════════════════════════
#  API  —  GET /api/health
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify(success=True, status="ok", timestamp=datetime.utcnow().isoformat() + "Z"), 200


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("-" * 60)
    print(" ADJ Technologies - Flask API Server")
    print(" Enquiry emails -> " + OWNER_EMAIL)
    print(" Listening on   -> http://127.0.0.1:5000")
    print("-" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
