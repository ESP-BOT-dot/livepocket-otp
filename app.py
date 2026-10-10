from flask import Flask, render_template_string, request
import imaplib
import email
import re

app = Flask(__name__)

GMAIL_USER = "livepocketb01@gmail.com"
GMAIL_APP_PASSWORD = "fdlqlngtqcdvlplr"

def get_latest_otps():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, '(FROM "noreply@livepocket.jp")')
        email_ids = messages[0].split()

        otps = []

        for e_id in reversed(email_ids[-12:]):
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
    except Exception as e:
        print(e)
        return []

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>LivePocket OTP</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      background: #0f0f0f;
      color: #fff;
      margin: 0;
      padding: 16px;
      max-width: 480px;
      margin: 0 auto;
    }
    h1 {
      text-align: center;
      font-size: 1.3rem;
      margin: 12px 0 20px;
      font-weight: 600;
    }
    button {
      width: 100%;
      padding: 14px;
      font-size: 1rem;
      border: none;
      border-radius: 12px;
      cursor: pointer;
    }
    .btn-main {
      background: #16a34a;
      color: white;
      margin-bottom: 20px;
      font-weight: 600;
    }
    .btn-main:active {
      background: #15803d;
    }
    .card {
      background: #1c1c1c;
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 12px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      font-size: 0.8rem;
      color: #888;
      margin-bottom: 6px;
    }
    .code {
      font-size: 1.9rem;
      font-weight: 700;
      text-align: center;
      letter-spacing: 3px;
      margin: 12px 0;
    }
    .copy {
      background: #2a2a2a;
      color: #ddd;
      font-size: 0.9rem;
      padding: 10px;
    }
    .copy:active {
      background: #3a3a3a;
    }
    .toast {
      position: fixed;
      bottom: 30px;
      left: 50%;
      transform: translateX(-50%);
      background: #16a34a;
      color: white;
      padding: 10px 20px;
      border-radius: 20px;
      font-size: 0.9rem;
      opacity: 0;
      transition: opacity 0.3s;
      pointer-events: none;
    }
    .toast.show {
      opacity: 1;
    }
    .empty {
      text-align: center;
      color: #666;
      margin-top: 40px;
      font-size: 0.95rem;
    }
  </style>
</head>
<body>
  <h1>LivePocket OTP</h1>
  
  <form method="get">
    <button type="submit" class="btn-main">最新を取得</button>
  </form>

  {% if otps %}
    {% for otp in otps %}
    <div class="card">
      <div class="header">
        <span>+{{ otp.alias }}</span>
        <span>{{ otp.date }}</span>
      </div>
      <div class="code">{{ otp.code }}</div>
      <button class="copy" onclick="copyCode('{{ otp.code }}')">コピー</button>
    </div>
    {% endfor %}
  {% else %}
    <p class="empty">「最新を取得」を押してください</p>
  {% endif %}

  <div class="toast" id="toast">コピーしました</div>

  <script>
    function copyCode(code) {
      navigator.clipboard.writeText(code).then(() => {
        const toast = document.getElementById('toast');
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 1500);
      });
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    otps = get_latest_otps()
    return render_template_string(HTML, otps=otps)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)