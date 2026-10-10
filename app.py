from flask import Flask, render_template_string
import imaplib
import email
import re

app = Flask(__name__)

GMAIL_USER = "livepocketb01@gmail.com"
GMAIL_APP_PASSWORD = "fdlqlngtqcdvlplr"

def get_latest_otps():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, '(FROM "noreply@livepocket.jp")')
    email_ids = messages[0].split()

    otps = []

    for e_id in reversed(email_ids[-15:]):
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        to = msg.get("To", "")
        date = msg.get("Date", "")

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        match = re.search(r"認証コード[：:\s]*(\d{4,8})", body)
        if not match:
            match = re.search(r"\b(\d{6})\b", body)

        if match:
            code = match.group(1)
            alias = "その他"
            if "+1991" in to: alias = "1991"
            elif "+1992" in to: alias = "1992"
            elif "+1993" in to: alias = "1993"
            elif "+1994" in to: alias = "1994"

            otps.append({
                "alias": alias,
                "code": code,
                "to": to,
                "date": date
            })

    mail.logout()

    # 各エイリアスの最新だけ
    latest = {}
    for otp in otps:
        if otp["alias"] not in latest:
            latest[otp["alias"]] = otp

    return list(latest.values())

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LivePocket OTP</title>
  <style>
    body {
      font-family: -apple-system, sans-serif;
      background: #111;
      color: white;
      margin: 0;
      padding: 16px;
      max-width: 480px;
      margin: 0 auto;
    }
    h1 {
      text-align: center;
      font-size: 1.4rem;
      margin-bottom: 20px;
    }
    button {
      width: 100%;
      padding: 14px;
      font-size: 1.1rem;
      background: #16a34a;
      color: white;
      border: none;
      border-radius: 12px;
      margin-bottom: 20px;
    }
    .card {
      background: #1f1f1f;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      color: #aaa;
      margin-bottom: 8px;
    }
    .code {
      font-size: 1.8rem;
      font-weight: bold;
      text-align: center;
      letter-spacing: 4px;
      margin: 10px 0;
    }
    .copy {
      width: 100%;
      padding: 10px;
      background: #333;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 0.9rem;
    }
  </style>
</head>
<body>
  <h1>LivePocket OTP</h1>
  <form method="get">
    <button type="submit">最新を取得</button>
  </form>

  {% if otps %}
    {% for otp in otps %}
    <div class="card">
      <div class="header">
        <span>+{{ otp.alias }}</span>
        <span>{{ otp.date }}</span>
      </div>
      <div class="code">{{ otp.code }}</div>
      <button class="copy" onclick="navigator.clipboard.writeText('{{ otp.code }}')">コピー</button>
    </div>
    {% endfor %}
  {% else %}
    <p style="text-align:center; color:#888;">「最新を取得」を押してください</p>
  {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    otps = get_latest_otps()
    return render_template_string(HTML, otps=otps)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)