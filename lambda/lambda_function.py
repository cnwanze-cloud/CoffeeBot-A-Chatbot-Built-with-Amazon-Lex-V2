"""
CoffeeBot fulfillment Lambda for Amazon Lex V2.

Lex invokes this function after the user confirms an OrderCoffee intent.
It calculates the price, generates an order number, and returns a response
in the format Lex V2 expects.

Runtime: Python 3.12 (or any current Python Lambda runtime)
Handler: lambda_function.lambda_handler
"""

import json
import random

# Base price by cup size
PRICES = {
    "Small": 2.50,
    "Medium": 3.25,
    "Large": 4.00,
}

# Extra charge by coffee type
EXTRA = {
    "Latte": 0.75,
    "Cappuccino": 0.75,
    "Espresso": 0.25,
    "Americano": 0.00,
}


def get_slot(slots, name):
    """Return the interpreted value of a slot, or None if it isn't filled."""
    slot = (slots or {}).get(name)
    if slot and slot.get("value"):
        return slot["value"].get("interpretedValue")
    return None


def close(intent, message, state="Fulfilled"):
    """Build a Lex V2 response that closes the conversation turn."""
    intent["state"] = state
    return {
        "sessionState": {
            "dialogAction": {"type": "Close"},
            "intent": intent,
        },
        "messages": [{"contentType": "PlainText", "content": message}],
    }


def handle_order_coffee(intent):
    """Fulfill the OrderCoffee intent."""
    # The user said "no" at the confirmation prompt
    if intent.get("confirmationState") == "Denied":
        return close(intent, "No problem, your order was cancelled.", "Failed")

    slots = intent.get("slots", {})
    coffee = get_slot(slots, "CoffeeType")
    size = get_slot(slots, "Size")

    # Guard against missing or unexpected slot values
    if coffee not in EXTRA or size not in PRICES:
        return close(
            intent,
            "Sorry, I couldn't read your order. Please try again.",
            "Failed",
        )

    total = PRICES[size] + EXTRA[coffee]
    order_id = random.randint(1000, 9999)

    message = (
        f"Done! Your {size} {coffee} is on its way. "
        f"Total: ${total:.2f}. Order number: #{order_id}."
    )
    return close(intent, message)


def lambda_handler(event, context):
    # Logged to CloudWatch Logs: /aws/lambda/CoffeeBotFulfillment
    print("Event:", json.dumps(event))

    intent = event["sessionState"]["intent"]

    if intent["name"] == "OrderCoffee":
        return handle_order_coffee(intent)

    return close(intent, "Sorry, I can't handle that request.", "Failed")
