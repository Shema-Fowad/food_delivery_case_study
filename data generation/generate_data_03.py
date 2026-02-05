"""
Zomato Sessions and Cart Data Generator - Part 3
Generates user sessions and cart items (abandoned carts)
"""

import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# =====================================================
# PATH SETUP (MATCHES YOUR REAL PROJECT STRUCTURE)
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MASTER_DIR = os.path.join(BASE_DIR, "1_csv_files")   # users, restaurants, menu
TXN_DIR = BASE_DIR                                   # orders, order_items
OUTPUT_DIR = BASE_DIR                                # write outputs here

# =====================================================
# SAFETY CHECKS
# =====================================================

required_master = [
    "users.csv",
    "restaurants.csv",
    "menu.csv"
]

required_txn = [
    "orders.csv",
    "order_items.csv"
]

for f in required_master:
    path = os.path.join(MASTER_DIR, f)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing master file: {path}")

for f in required_txn:
    path = os.path.join(TXN_DIR, f)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing transaction file: {path}")

random.seed(42)
np.random.seed(42)

# =====================================================
# CONFIG
# =====================================================

CONFIG = {
    "sessions_per_user_per_month": 8,
    "abandoned_cart_rate": 0.30
}

# =====================================================
# SESSION GENERATION
# =====================================================

def generate_user_sessions(users_df, orders_df):
    sessions = []
    session_id = 1

    orders_df["OrderTime"] = pd.to_datetime(orders_df["OrderTime"])

    for _, user in users_df.iterrows():
        user_id = user["UserID"]
        signup_date = pd.to_datetime(user["SignUpDate"])
        end_date = datetime(2024, 12, 31)

        months_active = max(1, int((end_date - signup_date).days / 30))
        total_sessions = months_active * CONFIG["sessions_per_user_per_month"]

        user_orders = orders_df[orders_df["UserID"] == user_id]

        for _ in range(total_sessions):
            random_days = random.randint(0, (end_date - signup_date).days)
            session_start = signup_date + timedelta(days=random_days)

            duration = random.randint(2, 30)
            session_end = session_start + timedelta(minutes=duration)

            order_match = user_orders[
                (user_orders["OrderTime"] >= session_start) &
                (user_orders["OrderTime"] <= session_end)
            ]

            order_placed = not order_match.empty
            order_id = order_match.iloc[0]["OrderID"] if order_placed else None

            sessions.append({
                "SessionID": session_id,
                "UserID": user_id,
                "SessionStart": session_start,
                "SessionEnd": session_end,
                "OrderPlaced": order_placed,
                "OrderID": order_id,
                "PagesViewed": random.randint(5, 20) if order_placed else random.randint(1, 8),
                "DeviceType": random.choice(["Mobile", "Mobile", "Mobile", "Desktop", "Tablet"])
            })

            session_id += 1

    return pd.DataFrame(sessions)

# =====================================================
# CART GENERATION
# =====================================================

def generate_cart_items(users_df, restaurants_df, menu_df, orders_df, order_items_df):
    cart = []
    cart_id = 1

    orders_df["OrderTime"] = pd.to_datetime(orders_df["OrderTime"])

    # Cart items from completed orders
    for _, order in orders_df.iterrows():
        items = order_items_df[order_items_df["OrderID"] == order["OrderID"]]

        for _, item in items.iterrows():
            cart.append({
                "CartID": cart_id,
                "UserID": order["UserID"],
                "RestaurantID": order["RestaurantID"],
                "MenuID": item["MenuID"],
                "Quantity": item["Quantity"],
                "AddedAt": order["OrderTime"] - timedelta(minutes=random.randint(1, 10)),
                "IsOrdered": True,
                "OrderID": order["OrderID"]
            })
            cart_id += 1

    # Abandoned carts
    target_abandoned = int(len(cart) * CONFIG["abandoned_cart_rate"] / (1 - CONFIG["abandoned_cart_rate"]))

    for _ in range(target_abandoned):
        user = users_df.sample(1).iloc[0]
        restaurant = restaurants_df[restaurants_df["IsActive"] == True].sample(1).iloc[0]

        menu_items = menu_df[
            (menu_df["RestaurantID"] == restaurant["RestaurantID"]) &
            (menu_df["IsAvailable"] == True)
        ]

        if menu_items.empty:
            continue

        item = menu_items.sample(1).iloc[0]

        cart.append({
            "CartID": cart_id,
            "UserID": user["UserID"],
            "RestaurantID": restaurant["RestaurantID"],
            "MenuID": item["MenuID"],
            "Quantity": random.choice([1, 1, 2]),
            "AddedAt": datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364)),
            "IsOrdered": False,
            "OrderID": None
        })
        cart_id += 1

    return pd.DataFrame(cart)

# =====================================================
# MAIN
# =====================================================

print("Loading data...")

users_df = pd.read_csv(os.path.join(MASTER_DIR, "users.csv"))
restaurants_df = pd.read_csv(os.path.join(MASTER_DIR, "restaurants.csv"))
menu_df = pd.read_csv(os.path.join(MASTER_DIR, "menu.csv"))

orders_df = pd.read_csv(os.path.join(TXN_DIR, "orders.csv"))
order_items_df = pd.read_csv(os.path.join(TXN_DIR, "order_items.csv"))

print("Generating sessions...")
sessions_df = generate_user_sessions(users_df, orders_df)

print("Generating cart items...")
cart_df = generate_cart_items(users_df, restaurants_df, menu_df, orders_df, order_items_df)

sessions_df.to_csv(os.path.join(OUTPUT_DIR, "user_sessions.csv"), index=False)
cart_df.to_csv(os.path.join(OUTPUT_DIR, "cart_items.csv"), index=False)

print("\n" + "=" * 50)
print("STEP 3 COMPLETE")
print("=" * 50)
print(f"User Sessions: {len(sessions_df)}")
print(f"Cart Items: {len(cart_df)}")
print("Ready for analytics / SQL 🚀")
