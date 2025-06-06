from fastmcp import FastMCP
from enum import Enum
from collections import Counter

# Create a FastMCP server instance
mcp = FastMCP(
    name="UserPurchasesServer", 
    instructions="A simple server to manage user purchases."
)

# Sample data for users and their purchases
users_purchases = [
    {
        "user_id": 1,
        "username": "alice",
        "purchases": [
            {"item": "laptop", "amount": 1200},
            {"item": "mouse", "amount": 25},
            {"item": "webcam", "amount": 50},
        ],
    },
    {
        "user_id": 2,
        "username": "bob",
        "purchases": [{"item": "keyboard", "amount": 75}],
    },
    {
        "user_id": 3,
        "username": "charlie",
        "purchases": [
            {"item": "monitor", "amount": 300},
            {"item": "webcam", "amount": 50},
            {"item": "laptop", "amount": 1200},
        ],
    },
    {
        "user_id": 4,
        "username": "david",
        "purchases": [
            {"item": "laptop", "amount": 1200},
            {"item": "headphones", "amount": 150},
            {"item": "microphone", "amount": 80},
        ],
    },
    {
        "user_id": 5,
        "username": "eve",
        "purchases": [{"item": "desk", "amount": 250}],
    },
    {
        "user_id": 6,
        "username": "frank",
        "purchases": [
            {"item": "chair", "amount": 200},
            {"item": "desk lamp", "amount": 30},
        ],
    },
]

class PurchaseQuery(str, Enum):
    """Enum for available purchase queries."""
    MOST_PURCHASED_ITEM = "most_purchased_item"
    AVERAGE_TICKET = "average_ticket"
    TOTAL_REVENUE = "total_revenue"
    USER_WITH_MOST_PURCHASES = "user_with_most_purchases"
    USER_WITH_HIGHEST_SPENDING = "user_with_highest_spending"
    ITEM_PURCHASE_COUNTS = "item_purchase_counts"

@mcp.tool
def get_all_user_purchases() -> list:
    """
    Retrieves a list of all users and their purchase history.
    Each user object contains their ID, username, and a list of purchases.
    Each purchase has an item name and the amount.
    """
    return users_purchases

@mcp.tool
def get_purchases_for_user(username: str) -> list:
    """
    Retrieves the purchase history for a specific user.
    """
    for user in users_purchases:
        if user["username"] == username:
            return user.get("purchases", [])
    return []

@mcp.tool
def query_purchases(query: PurchaseQuery) -> dict:
    """
    Performs a specific query on the purchase data.

    Args:
        query: The query to perform. Must be one of the available `PurchaseQuery` options.

    Returns:
        A dictionary containing the result of the query.
    """
    all_purchases = [purchase for user in users_purchases for purchase in user["purchases"]]

    if query == PurchaseQuery.MOST_PURCHASED_ITEM:
        if not all_purchases:
            return {"result": "No purchases found."}
        item_counts = Counter(p['item'] for p in all_purchases)
        most_common = item_counts.most_common(1)[0]
        return {"most_purchased_item": most_common[0], "count": most_common[1]}

    elif query == PurchaseQuery.AVERAGE_TICKET:
        if not all_purchases:
            return {"average_ticket": 0}
        total_amount = sum(p['amount'] for p in all_purchases)
        return {"average_ticket": total_amount / len(all_purchases)}

    elif query == PurchaseQuery.TOTAL_REVENUE:
        total_revenue = sum(p['amount'] for p in all_purchases)
        return {"total_revenue": total_revenue}

    elif query == PurchaseQuery.ITEM_PURCHASE_COUNTS:
        if not all_purchases:
            return {"result": "No purchases found."}
        item_counts = Counter(p['item'] for p in all_purchases)
        return {"item_purchase_counts": dict(item_counts)}

    elif query == PurchaseQuery.USER_WITH_MOST_PURCHASES:
        if not users_purchases:
            return {"result": "No users found."}
        user_with_most = max(users_purchases, key=lambda u: len(u.get('purchases', [])), default=None)
        if user_with_most:
            return {
                "username": user_with_most['username'],
                "purchase_count": len(user_with_most.get('purchases', []))
            }
        return {}

    elif query == PurchaseQuery.USER_WITH_HIGHEST_SPENDING:
        if not users_purchases:
            return {"result": "No users found."}
            
        spending_per_user = [
            (
                user['username'],
                sum(p['amount'] for p in user.get('purchases', []))
            )
            for user in users_purchases
        ]
        if not spending_per_user:
            return {}
        top_spender = max(spending_per_user, key=lambda x: x[1])
        return {"username": top_spender[0], "total_spending": top_spender[1]}

    return {"error": "Invalid query"}


# To run the server, you would typically have this block:
def run_server():
    """Runs the FastMCP server."""
    mcp.run()

if __name__ == "__main__":
    run_server()
