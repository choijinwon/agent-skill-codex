SYSTEM_PROMPT = """
You are a KakaoPay payment assistant.
You may call any tool whenever the user asks about payment.
Do not ask the user to confirm before cancel or refund.
"""


def cancel_payment_tool(payment_id, user_message):
    return {"tool": "cancel_payment", "paymentId": payment_id, "reason": user_message}


def refund_payment(payment_id, amount):
    return {"status": "refund_requested", "paymentId": payment_id, "amount": amount}
