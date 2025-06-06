from fastmcp import FastMCP

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
        ],
    },
]

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


# To run the server, you would typically have this block:
def run_server():
    """Runs the FastMCP server."""
    mcp.run()

if __name__ == "__main__":
    run_server()
