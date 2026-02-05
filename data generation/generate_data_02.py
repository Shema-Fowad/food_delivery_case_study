"""
Zomato Orders Data Generator - Part 2
Generates orders, order items, and related transactional data
"""

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, "1_csv_files")

random.seed(42)
np.random.seed(42)

# ============================================
# CONFIGURATION
# ============================================

CONFIG = {
    'start_date': datetime(2024, 1, 1),
    'end_date': datetime(2024, 12, 31),
    'target_total_orders': 300000,
    'avg_items_per_order': 1.5,
    'power_user_percentage': 0.20,  # 20% users make 80% orders
    'weekend_only_user_percentage': 0.15,
    'bot_users_count': 50,  # Users with suspicious patterns
}

def get_order_hour_with_peaks():
    """Generate order hour with lunch and dinner peaks"""
    rand = random.random()
    
    if rand < 0.40:  # 40% dinner (7-10 PM)
        return random.randint(19, 22)
    elif rand < 0.65:  # 25% lunch (12-3 PM)
        return random.randint(12, 15)
    elif rand < 0.80:  # 15% evening snacks (4-6 PM)
        return random.randint(16, 18)
    elif rand < 0.90:  # 10% morning (8-11 AM)
        return random.randint(8, 11)
    else:  # 10% late night (11 PM - 1 AM)
        return random.choice([23, 0, 1])

def generate_orders(users_df, restaurants_df, menu_df, config):
    """Generate orders with realistic patterns"""
    orders_data = []
    order_items_data = []
    order_id = 1
    order_item_id = 1
    
    print("Loading user data...")
    # Categorize users
    total_users = len(users_df)
    num_power_users = int(total_users * config['power_user_percentage'])
    num_weekend_users = int(total_users * config['weekend_only_user_percentage'])
    num_bot_users = config['bot_users_count']
    
    # Power users (20% make 80% of orders)
    power_users = users_df.sample(n=num_power_users)['UserID'].tolist()
    power_user_orders = int(config['target_total_orders'] * 0.80)
    
    # Weekend-only users
    weekend_users = users_df[~users_df['UserID'].isin(power_users)].sample(n=num_weekend_users)['UserID'].tolist()
    
    # Bot users
    bot_users = users_df[~users_df['UserID'].isin(power_users + weekend_users)].sample(n=num_bot_users)['UserID'].tolist()
    
    # Regular users
    regular_users = users_df[
        ~users_df['UserID'].isin(power_users + weekend_users + bot_users)
    ]['UserID'].tolist()
    
    print(f"Power users: {len(power_users)}")
    print(f"Weekend users: {len(weekend_users)}")
    print(f"Bot users: {len(bot_users)}")
    print(f"Regular users: {len(regular_users)}")
    
    # Generate dates for the year
    current_date = config['start_date']
    
    while current_date <= config['end_date']:
        # Daily order count with growth and day-of-week pattern
        days_passed = (current_date - config['start_date']).days
        month_factor = 1 + (days_passed / 30) * 0.03  # 3% monthly growth
        
        base_daily_orders = config['target_total_orders'] / 365
        
        # Weekend boost
        if current_date.weekday() >= 5:  # Saturday, Sunday
            daily_orders = int(base_daily_orders * 1.4 * month_factor)
        else:
            daily_orders = int(base_daily_orders * month_factor)
        
        # Generate orders for this day
        for _ in range(daily_orders):
            # User selection based on day
            if current_date.weekday() >= 5:  # Weekend
                user_id = random.choice(power_users + weekend_users + regular_users)
            else:  # Weekday
                user_id = random.choice(power_users + regular_users)
            
            # Restaurant selection (prefer restaurants in same city)
            user_city = users_df[users_df['UserID'] == user_id].iloc[0]['CityID']
            city_restaurants = restaurants_df[
                (restaurants_df['CityID'] == user_city) & 
                (restaurants_df['IsActive'] == True)
            ]
            
            if len(city_restaurants) == 0:
                city_restaurants = restaurants_df[restaurants_df['IsActive'] == True]
            
            restaurant = city_restaurants.sample(1).iloc[0]
            
            # Order time
            order_hour = get_order_hour_with_peaks()
            order_minute = random.randint(0, 59)
            order_time = current_date.replace(hour=order_hour, minute=order_minute)
            
            # Order items
            restaurant_menu = menu_df[
                (menu_df['RestaurantID'] == restaurant['RestaurantID']) & 
                (menu_df['IsAvailable'] == True)
            ]
            
            if len(restaurant_menu) == 0:
                continue
            
            num_items = np.random.choice([1, 2, 3, 4], p=[0.55, 0.30, 0.10, 0.05])
            selected_items = restaurant_menu.sample(n=min(num_items, len(restaurant_menu)))
            
            total_amount = 0
            order_items_for_order = []
            
            for _, item in selected_items.iterrows():
                quantity = random.choice([1, 1, 1, 2])
                item_price = item['Price']
                subtotal = item_price * quantity
                total_amount += subtotal
                
                order_items_for_order.append({
                    'OrderItemID': order_item_id,
                    'OrderID': order_id,
                    'MenuID': item['MenuID'],
                    'Quantity': quantity,
                    'ItemPrice': item_price,
                    'Subtotal': subtotal
                })
                order_item_id += 1
            
            # Calculate fees and discounts
            delivery_fee = random.choice([0, 0, 30, 40, 50, 60])  # Free delivery common
            discount_amount = 0
            
            if total_amount > 500:
                discount_amount = round(total_amount * random.choice([0, 0, 0.10, 0.15]), 2)
            
            final_amount = total_amount + delivery_fee - discount_amount
            
            orders_data.append({
                'OrderID': order_id,
                'UserID': user_id,
                'RestaurantID': restaurant['RestaurantID'],
                'OrderTime': order_time,
                'OrderDate': current_date.date(),
                'OrderDay': current_date.strftime('%A'),
                'OrderHour': order_hour,
                'TotalAmount': round(total_amount, 2),
                'DeliveryFee': delivery_fee,
                'DiscountAmount': discount_amount,
                'FinalAmount': round(final_amount, 2),
                'OrderStatus': random.choice(['Delivered'] * 90 + ['Cancelled'] * 10),
                'DeliveryAddress': users_df[users_df['UserID'] == user_id].iloc[0]['Address'],
                'PaymentMethod': random.choice(['Credit Card', 'Debit Card', 'UPI', 'UPI', 'UPI', 'Cash on Delivery'])
            })
            
            order_items_data.extend(order_items_for_order)
            order_id += 1
        
        current_date += timedelta(days=1)
        
        if current_date.day == 1:
            print(f"Processed {current_date.strftime('%B %Y')}")
    
    # Generate bot user orders (50+ orders per day for some users)
    print("\nGenerating bot user patterns...")
    for bot_user in bot_users[:25]:  # Only some are heavy bots
        bot_date = config['start_date'] + timedelta(days=random.randint(0, 300))
        
        for _ in range(random.randint(50, 100)):  # 50-100 orders in one day
            restaurant = restaurants_df.sample(1).iloc[0]
            restaurant_menu = menu_df[
                (menu_df['RestaurantID'] == restaurant['RestaurantID']) & 
                (menu_df['IsAvailable'] == True)
            ]
            
            if len(restaurant_menu) == 0:
                continue
            
            item = restaurant_menu.sample(1).iloc[0]
            order_hour = random.randint(0, 23)
            order_minute = random.randint(0, 59)
            order_time = bot_date.replace(hour=order_hour, minute=order_minute)
            
            total_amount = item['Price']
            
            orders_data.append({
                'OrderID': order_id,
                'UserID': bot_user,
                'RestaurantID': restaurant['RestaurantID'],
                'OrderTime': order_time,
                'OrderDate': bot_date.date(),
                'OrderDay': bot_date.strftime('%A'),
                'OrderHour': order_hour,
                'TotalAmount': total_amount,
                'DeliveryFee': 0,
                'DiscountAmount': 0,
                'FinalAmount': total_amount,
                'OrderStatus': 'Delivered',
                'DeliveryAddress': users_df[users_df['UserID'] == bot_user].iloc[0]['Address'],
                'PaymentMethod': 'UPI'
            })
            
            order_items_data.append({
                'OrderItemID': order_item_id,
                'OrderID': order_id,
                'MenuID': item['MenuID'],
                'Quantity': 1,
                'ItemPrice': item['Price'],
                'Subtotal': item['Price']
            })
            
            order_item_id += 1
            order_id += 1
    
    return pd.DataFrame(orders_data), pd.DataFrame(order_items_data)

def generate_delivery_tracking(orders_df):
    """Generate delivery tracking data"""
    delivery_data = []
    
    for _, order in orders_df.iterrows():
        if order['OrderStatus'] == 'Delivered':
            # Dispatch time: 5-15 minutes after order
            dispatch_time = order['OrderTime'] + timedelta(minutes=random.randint(5, 15))
            
            # Estimated delivery: 20-40 minutes
            estimated_minutes = random.randint(20, 40)
            estimated_delivery = dispatch_time + timedelta(minutes=estimated_minutes)
            
            # Actual delivery: Usually within estimated ± 10 minutes
            actual_variation = random.randint(-10, 15)
            actual_minutes = estimated_minutes + actual_variation
            actual_delivery = dispatch_time + timedelta(minutes=actual_minutes)
            
            # Some outliers for anomaly detection
            if random.random() < 0.05:  # 5% outliers
                actual_minutes = random.randint(60, 120)
                actual_delivery = dispatch_time + timedelta(minutes=actual_minutes)
            
            delivery_data.append({
                'DeliveryID': order['OrderID'],
                'OrderID': order['OrderID'],
                'DispatchTime': dispatch_time,
                'EstimatedDeliveryTime': estimated_delivery,
                'ActualDeliveryTime': actual_delivery,
                'ActualDeliveryMinutes': actual_minutes,
                'DeliveryPartnerID': random.randint(1, 1000),
                'DeliveryStatus': 'Delivered'
            })
    
    return pd.DataFrame(delivery_data)

def generate_reviews(orders_df, users_df, restaurants_df, review_rate=0.33):
    """Generate reviews for orders"""
    reviews_data = []
    review_id = 1
    
    # Sample orders for reviews
    reviewed_orders = orders_df[orders_df['OrderStatus'] == 'Delivered'].sample(frac=review_rate)
    
    for _, order in reviewed_orders.iterrows():
        # Rating distribution (skewed toward positive)
        rating = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.05, 0.15, 0.35, 0.40])
        
        # Review date: 0-7 days after delivery
        review_date = order['OrderTime'] + timedelta(days=random.randint(0, 7))
        
        comments = [
            "Great food and quick delivery!",
            "Loved the taste, will order again.",
            "Food was cold when it arrived.",
            "Excellent service and quality.",
            "Not up to the mark, expected better.",
            "Amazing experience!",
            "Decent food, nothing special.",
            "Highly recommended!",
            "Won't order again.",
            "Best restaurant in the area!"
        ]
        
        reviews_data.append({
            'ReviewID': review_id,
            'UserID': order['UserID'],
            'RestaurantID': order['RestaurantID'],
            'OrderID': order['OrderID'],
            'Rating': rating,
            'Comment': random.choice(comments) if random.random() < 0.7 else None,
            'ReviewDate': review_date,
            'IsVerifiedPurchase': True
        })
        review_id += 1
    
    return pd.DataFrame(reviews_data)

# ============================================
# MAIN EXECUTION
# ============================================

print("Loading base data...")
users_df = pd.read_csv(os.path.join(CSV_DIR, 'users.csv'))
users_df['SignUpDate'] = pd.to_datetime(users_df['SignUpDate'])
restaurants_df = pd.read_csv(os.path.join(CSV_DIR, 'restaurants.csv'))
menu_df = pd.read_csv(os.path.join(CSV_DIR, 'menu.csv'))

print("\n" + "="*50)
print("GENERATING ORDERS DATA")
print("="*50)

print("\n1. Generating Orders and Order Items...")
orders_df, order_items_df = generate_orders(users_df, restaurants_df, menu_df, CONFIG)
print(f"   Created {len(orders_df)} orders")
print(f"   Created {len(order_items_df)} order items")

print("\n2. Generating Delivery Tracking...")
delivery_df = generate_delivery_tracking(orders_df)
print(f"   Created {len(delivery_df)} delivery records")

print("\n3. Generating Reviews...")
reviews_df = generate_reviews(orders_df, users_df, restaurants_df)
print(f"   Created {len(reviews_df)} reviews")

print("\n4. Saving to CSV files...")
orders_df.to_csv('orders.csv', index=False)
order_items_df.to_csv('order_items.csv', index=False)
delivery_df.to_csv('delivery_tracking.csv', index=False)
reviews_df.to_csv('reviews.csv', index=False)

print("\n" + "="*50)
print("ORDERS DATA GENERATION COMPLETE!")
print("="*50)
print("Generated files:")
print("  - orders.csv")
print("  - order_items.csv")
print("  - delivery_tracking.csv")
print("  - reviews.csv")
print("\nNext: Run generate_sessions_and_carts.py")