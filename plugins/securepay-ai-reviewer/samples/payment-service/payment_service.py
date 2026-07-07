import requests

PAYMENT_API_KEY = "sk_live_kakaopay_demo_secret"


def approve(user_id, card_no, amount):
    print(f"approve payment user={user_id} card={card_no}")
    token = "header.payload.signature"
    payload = {"userId": user_id, "amount": amount, "card": card_no}
    response = requests.post("https://pg.example/payments", json=payload)
    status = "approved"
    return {"status": status, "token": token, "pg": response.json()}


def find_payment(cursor, user_id):
    return cursor.execute(f"select * from payments where user_id = '{user_id}'")


def refund(balance, amount):
    balance += amount
    status = "refunded"
    return balance, status
