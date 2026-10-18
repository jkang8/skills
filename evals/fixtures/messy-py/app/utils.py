import datetime
import os
import smtplib


def format_money(cents):
    return "$%.2f" % (cents / 100)


def parse_date(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def send_email(to, body):
    if os.environ.get("SEND_EMAIL") == "1":
        with smtplib.SMTP("localhost") as s:
            s.sendmail("shop@example.com", [to], body)


def compute_total(subtotal_cents, is_vip, tax_rate):
    if is_vip:
        subtotal_cents = int(subtotal_cents * 0.9)
    return int(subtotal_cents * (1 + tax_rate))
