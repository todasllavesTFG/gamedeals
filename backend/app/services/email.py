import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "") or SMTP_USER


def send_price_alert_email(
    to_email: str,
    username: str,
    game_title: str,
    target_price: float,
    current_price: float,
    store_name: str,
    deal_url: str,
) -> bool:
    """
    Envía un email de alerta de precio al usuario.

    Si SMTP_HOST o SMTP_USER no están configurados, simula el envío
    logueando el evento (no lanza excepción — never fail silently).

    Returns True si el email se envió (o se simuló), False si hubo un
    error real de red/autenticación.
    """
    subject = f"🎮 Alerta GameDeals: {game_title} por {current_price:.2f}€"

    html_body = f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0a0a0f;font-family:'Inter',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0f;padding:32px 16px;">
    <tr><td align="center">
      <table width="480" cellpadding="0" cellspacing="0"
             style="background:#14141f;border-radius:12px;border:1px solid #2a2a3d;overflow:hidden;">

        <!-- Header -->
        <tr>
          <td style="background:#1c1c2b;padding:24px 32px;border-bottom:1px solid #2a2a3d;">
            <span style="font-size:1.1rem;font-weight:700;color:#a3ff12;letter-spacing:0.05em;">
              🎮 GameDeals
            </span>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:32px;">
            <h1 style="margin:0 0 8px 0;font-size:1.3rem;color:#e8e8f0;">
              ¡Tu alerta se ha disparado!
            </h1>
            <p style="margin:0 0 24px 0;color:#8b8ba3;font-size:0.9rem;">
              Hola <strong style="color:#e8e8f0;">{username}</strong>,
              el juego que estabas esperando ya está por debajo de tu precio objetivo.
            </p>

            <!-- Game card -->
            <div style="background:#1c1c2b;border-radius:8px;padding:20px;
                        border:1px solid #2a2a3d;margin-bottom:24px;">
              <p style="margin:0 0 4px 0;font-size:1rem;font-weight:600;color:#e8e8f0;">
                {game_title}
              </p>
              <p style="margin:0 0 12px 0;font-size:0.8rem;color:#8b8ba3;">
                en {store_name}
              </p>
              <div style="display:flex;align-items:baseline;gap:12px;">
                <span style="font-size:1.75rem;font-weight:700;color:#a3ff12;">
                  {current_price:.2f}€
                </span>
                <span style="font-size:0.85rem;color:#8b8ba3;">
                  Tu objetivo: {target_price:.2f}€
                </span>
              </div>
            </div>

            <!-- CTA -->
            <a href="{deal_url}"
               style="display:inline-block;background:#a3ff12;color:#0a0a0f;
                      padding:12px 28px;border-radius:8px;text-decoration:none;
                      font-weight:700;font-size:0.95rem;">
              Ver oferta →
            </a>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:16px 32px;border-top:1px solid #2a2a3d;">
            <p style="margin:0;font-size:0.75rem;color:#8b8ba3;">
              Recibes este email porque configuraste una alerta en GameDeals.
              La alerta ha sido desactivada automáticamente.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""

    # Sin configuración SMTP → simular y devolver OK
    if not SMTP_HOST or not SMTP_USER:
        logger.info(
            "[EMAIL SIMULADO] to=%s | juego='%s' | precio=%.2f€ | objetivo=%.2f€ | tienda=%s",
            to_email,
            game_title,
            current_price,
            target_price,
            store_name,
        )
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, [to_email], msg.as_string())

        logger.info(
            "Email de alerta enviado a %s para '%s' (%.2f€)",
            to_email,
            game_title,
            current_price,
        )
        return True

    except Exception:
        logger.exception("Error enviando email de alerta a %s", to_email)
        return False
