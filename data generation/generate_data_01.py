"""
Zomato Data Generator
Generates 1 year of realistic data for SQL interview practice
Author: SQL Interview Prep
Date: 2024
"""

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import json

# Initialize Faker
fake = Faker('en_IN')  # Indian locale
random.seed(42)
np.random.seed(42)

# ============================================
# CONFIGURATION
# ============================================

CONFIG = {
    'start_date': datetime(2024, 1, 1),
    'end_date': datetime(2024, 12, 31),
    'num_users': 10000,
    'num_restaurants': 500,
    'num_cities': 50,
    'avg_menu_items_per_restaurant': 30,
    'target_total_orders': 300000,
    'abandoned_cart_rate': 0.30,
    'session_to_order_conversion': 0.18,
    'review_rate': 0.33,
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_dates_with_patterns(start, end, num_events):
    """Generate dates with realistic patterns (weekends higher, peaks)"""
    dates = []
    current = start
    days_diff = (end - start).days
    
    for _ in range(num_events):
        # Random day with slight weekend bias
        random_days = random.randint(0, days_diff)
        date = start + timedelta(days=random_days)
        
        # Weekend bias (40% more likely)
        if date.weekday() >= 5:  # Saturday, Sunday
            if random.random() < 0.4:
                dates.append(date)
        
        dates.append(date)
    
    return sorted(dates)[:num_events]

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

def generate_realistic_price(category):
    """Generate realistic menu prices based on category"""
    price_ranges = {
        'Appetizer': (50, 250),
        'Main Course': (150, 600),
        'Dessert': (80, 200),
        'Beverage': (30, 150),
        'Bread': (20, 80),
        'Salad': (100, 250),
        'Soup': (80, 180),
    }
    
    min_price, max_price = price_ranges.get(category, (100, 400))
    return round(random.uniform(min_price, max_price), 2)

# ============================================
# DATA GENERATION FUNCTIONS
# ============================================

def generate_cities(num_cities=50):
    """Generate cities data"""
    indian_cities = [
        ('Mumbai', 'Maharashtra'), ('Delhi', 'Delhi'), ('Bangalore', 'Karnataka'),
        ('Hyderabad', 'Telangana'), ('Chennai', 'Tamil Nadu'), ('Kolkata', 'West Bengal'),
        ('Pune', 'Maharashtra'), ('Ahmedabad', 'Gujarat'), ('Jaipur', 'Rajasthan'),
        ('Surat', 'Gujarat'), ('Lucknow', 'Uttar Pradesh'), ('Kanpur', 'Uttar Pradesh'),
        ('Nagpur', 'Maharashtra'), ('Indore', 'Madhya Pradesh'), ('Thane', 'Maharashtra'),
        ('Bhopal', 'Madhya Pradesh'), ('Visakhapatnam', 'Andhra Pradesh'), ('Pimpri-Chinchwad', 'Maharashtra'),
        ('Patna', 'Bihar'), ('Vadodara', 'Gujarat'), ('Ghaziabad', 'Uttar Pradesh'),
        ('Ludhiana', 'Punjab'), ('Agra', 'Uttar Pradesh'), ('Nashik', 'Maharashtra'),
        ('Faridabad', 'Haryana'), ('Meerut', 'Uttar Pradesh'), ('Rajkot', 'Gujarat'),
        ('Kalyan-Dombivali', 'Maharashtra'), ('Vasai-Virar', 'Maharashtra'), ('Varanasi', 'Uttar Pradesh'),
        ('Srinagar', 'Jammu and Kashmir'), ('Aurangabad', 'Maharashtra'), ('Dhanbad', 'Jharkhand'),
        ('Amritsar', 'Punjab'), ('Navi Mumbai', 'Maharashtra'), ('Allahabad', 'Uttar Pradesh'),
        ('Ranchi', 'Jharkhand'), ('Howrah', 'West Bengal'), ('Coimbatore', 'Tamil Nadu'),
        ('Jabalpur', 'Madhya Pradesh'), ('Gwalior', 'Madhya Pradesh'), ('Vijayawada', 'Andhra Pradesh'),
        ('Jodhpur', 'Rajasthan'), ('Madurai', 'Tamil Nadu'), ('Raipur', 'Chhattisgarh'),
        ('Kota', 'Rajasthan'), ('Chandigarh', 'Chandigarh'), ('Guwahati', 'Assam'),
        ('Solapur', 'Maharashtra'), ('Hubli-Dharwad', 'Karnataka')
    ]
    
    cities_data = []
    for i, (city, state) in enumerate(indian_cities[:num_cities], 1):
        cities_data.append({
            'CityID': i,
            'CityName': city,
            'State': state
        })
    
    return pd.DataFrame(cities_data)

def generate_acquisition_channels():
    """Generate acquisition channels"""
    channels = [
        ('Organic Search', 'Users from search engines'),
        ('Google Ads', 'Google advertising'),
        ('Facebook Ads', 'Facebook advertising'),
        ('Instagram Ads', 'Instagram advertising'),
        ('Referral Program', 'User referrals'),
        ('App Store Featured', 'App store featuring'),
        ('Email Marketing', 'Email campaigns'),
        ('Influencer Marketing', 'Influencer promotions'),
        ('Direct', 'Direct visits'),
        ('YouTube Ads', 'YouTube advertising'),
    ]
    
    channels_data = []
    for i, (name, desc) in enumerate(channels, 1):
        channels_data.append({
            'ChannelID': i,
            'ChannelName': name,
            'Description': desc
        })
    
    return pd.DataFrame(channels_data)

def generate_users(num_users, cities_df, channels_df, start_date, end_date):
    """Generate users with realistic patterns"""
    users_data = []
    
    # Distribution of users across channels
    channel_weights = [0.30, 0.15, 0.12, 0.10, 0.15, 0.05, 0.05, 0.03, 0.03, 0.02]
    
    # Generate signup dates with growth pattern
    signup_dates = []
    current_date = start_date
    base_signups_per_day = num_users // 365
    
    while current_date <= end_date:
        # Monthly growth factor (2-5% growth)
        months_passed = (current_date - start_date).days // 30
        growth_factor = 1 + (months_passed * 0.03)
        
        daily_signups = int(base_signups_per_day * growth_factor * random.uniform(0.7, 1.3))
        signup_dates.extend([current_date] * daily_signups)
        current_date += timedelta(days=1)
    
    signup_dates = signup_dates[:num_users]
    
    for i in range(1, num_users + 1):
        city = cities_df.sample(1).iloc[0]
        channel_id = np.random.choice(channels_df['ChannelID'], p=channel_weights)
        
        signup_date = signup_dates[i-1] if i-1 < len(signup_dates) else start_date + timedelta(days=random.randint(0, 364))
        
        users_data.append({
            'UserID': i,
            'Username': fake.user_name(),
            'Email': fake.email(),
            'PasswordHash': fake.sha256(),
            'Phone': fake.phone_number(),
            'Address': fake.address().replace('\n', ', '),
            'CityID': city['CityID'],
            'SignUpDate': signup_date,
            'AcquisitionChannelID': channel_id,
            'ReferredBy': None,  # Will be set later for some users
            'LastLoginDate': signup_date + timedelta(days=random.randint(0, 30)),
            'IsActive': random.choice([True] * 95 + [False] * 5),
            'Preferences': json.dumps({'dietary': random.choice(['None', 'Vegetarian', 'Vegan', 'Jain'])})
        })
    
    return pd.DataFrame(users_data)

def add_referrals(users_df, referral_percentage=0.15):
    """Add referral relationships"""
    referrals_data = []
    users_with_channel_5 = users_df[users_df['AcquisitionChannelID'] == 5].copy()
    
    for idx, user in users_with_channel_5.iterrows():
        # Find a potential referrer (signed up before this user)
        potential_referrers = users_df[
            (users_df['SignUpDate'] < user['SignUpDate']) &
            (users_df['UserID'] != user['UserID'])
        ]
        
        if len(potential_referrers) > 0:
            referrer = potential_referrers.sample(1).iloc[0]
            users_df.at[idx, 'ReferredBy'] = referrer['UserID']
            
            referrals_data.append({
                'ReferralID': len(referrals_data) + 1,
                'ReferrerUserID': referrer['UserID'],
                'ReferredUserID': user['UserID'],
                'ReferralDate': user['SignUpDate'],
                'RewardAmount': random.choice([50, 75, 100]),
                'RewardStatus': random.choice(['Paid', 'Paid', 'Paid', 'Pending'])
            })
    
    return users_df, pd.DataFrame(referrals_data)

def generate_restaurants(num_restaurants, cities_df):
    """Generate restaurants"""
    restaurants_data = []
    
    cuisines = ['North Indian', 'South Indian', 'Chinese', 'Italian', 'Continental', 
                'Fast Food', 'Desserts', 'Beverages', 'Bakery', 'Street Food',
                'Mughlai', 'Bengali', 'Punjabi', 'Gujarati', 'Rajasthani']
    
    restaurant_names = [
        'The Great Kabab Factory', 'Barbeque Nation', 'Mainland China', 'Paradise Biryani',
        'Dominos Pizza', 'Pizza Hut', 'KFC', 'McDonalds', 'Subway', 'Burger King',
        'Cafe Coffee Day', 'Starbucks', 'The Beer Cafe', 'Social', 'The Brew House',
        'Haldirams', 'Bikanervala', 'Sagar Ratna', 'Saravana Bhavan', 'MTR',
        'Kareem\'s', 'Moti Mahal', 'Punjab Grill', 'Oh! Calcutta', 'Arsalan',
        'Empire Restaurant', 'Meghana Foods', 'Truffles', 'Toit', 'Smoke House Deli'
    ]
    
    for i in range(1, num_restaurants + 1):
        city = cities_df.sample(1).iloc[0]
        cuisine = random.choice(cuisines)
        
        # Some cities have more restaurants
        if city['CityName'] in ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai']:
            rating_bias = 0.3
        else:
            rating_bias = 0
        
        restaurants_data.append({
            'RestaurantID': i,
            'Name': random.choice(restaurant_names) + f" - {city['CityName']} {i}",
            'Address': fake.address().replace('\n', ', '),
            'CityID': city['CityID'],
            'Cuisine': cuisine,
            'Rating': round(random.uniform(3.0, 5.0) + rating_bias, 2),
            'OperatingHours': '10:00 AM - 11:00 PM',
            'ContactNumber': fake.phone_number(),
            'IsActive': random.choice([True] * 95 + [False] * 5),
            'OpeningDate': fake.date_between(start_date='-5y', end_date='-6m')
        })
    
    return pd.DataFrame(restaurants_data)

def generate_menu(restaurants_df):
    """Generate menu items"""
    menu_data = []
    menu_id = 1
    
    categories = ['Appetizer', 'Main Course', 'Dessert', 'Beverage', 'Bread', 'Salad', 'Soup']
    
    menu_items_by_cuisine = {
        'North Indian': ['Paneer Tikka', 'Butter Chicken', 'Dal Makhani', 'Naan', 'Biryani', 'Tandoori Chicken'],
        'South Indian': ['Dosa', 'Idli', 'Vada', 'Uttapam', 'Sambar', 'Coconut Chutney'],
        'Chinese': ['Fried Rice', 'Chowmein', 'Manchurian', 'Spring Rolls', 'Soup', 'Hakka Noodles'],
        'Italian': ['Pizza Margherita', 'Pasta Alfredo', 'Lasagna', 'Garlic Bread', 'Bruschetta', 'Tiramisu'],
        'Fast Food': ['Burger', 'French Fries', 'Pizza', 'Sandwich', 'Wrap', 'Nuggets'],
        'Desserts': ['Ice Cream', 'Cake', 'Brownie', 'Pastry', 'Gulab Jamun', 'Rasmalai'],
    }
    
    for _, restaurant in restaurants_df.iterrows():
        num_items = random.randint(20, 40)
        cuisine = restaurant['Cuisine']
        
        base_items = menu_items_by_cuisine.get(cuisine, ['Special Dish', 'House Special', 'Chef Special'])
        
        for i in range(num_items):
            category = random.choice(categories)
            item_name = random.choice(base_items) + f" {random.choice(['Deluxe', 'Special', 'Classic', 'Royal', ''])}"
            
            menu_data.append({
                'MenuID': menu_id,
                'RestaurantID': restaurant['RestaurantID'],
                'ItemName': item_name.strip(),
                'Description': fake.sentence(nb_words=10),
                'Price': generate_realistic_price(category),
                'Category': category,
                'CuisineType': cuisine,
                'IsVegetarian': random.choice([True, False]),
                'IsAvailable': random.choice([True] * 90 + [False] * 10)
            })
            menu_id += 1
    
    return pd.DataFrame(menu_data)

print("Starting data generation...")
print("="*50)

# Generate base data
print("1. Generating Cities...")
cities_df = generate_cities(CONFIG['num_cities'])
print(f"   Created {len(cities_df)} cities")

print("2. Generating Acquisition Channels...")
channels_df = generate_acquisition_channels()
print(f"   Created {len(channels_df)} channels")

print("3. Generating Users...")
users_df = generate_users(
    CONFIG['num_users'], 
    cities_df, 
    channels_df, 
    CONFIG['start_date'], 
    CONFIG['end_date']
)
print(f"   Created {len(users_df)} users")

print("4. Adding Referral Relationships...")
users_df, referrals_df = add_referrals(users_df)
print(f"   Created {len(referrals_df)} referrals")

print("5. Generating Restaurants...")
restaurants_df = generate_restaurants(CONFIG['num_restaurants'], cities_df)
print(f"   Created {len(restaurants_df)} restaurants")

print("6. Generating Menu Items...")
menu_df = generate_menu(restaurants_df)
print(f"   Created {len(menu_df)} menu items")

# Save to CSV
print("\n7. Saving to CSV files...")
cities_df.to_csv('cities.csv', index=False)
channels_df.to_csv('acquisition_channels.csv', index=False)
users_df.to_csv('users.csv', index=False)
referrals_df.to_csv('referrals.csv', index=False)
restaurants_df.to_csv('restaurants.csv', index=False)
menu_df.to_csv('menu.csv', index=False)

print("\nPhase 1 Complete!")
print("="*50)
print("Generated files:")
print("  - cities.csv")
print("  - acquisition_channels.csv")
print("  - users.csv")
print("  - referrals.csv")
print("  - restaurants.csv")
print("  - menu.csv")
print("\nNext: Run generate_orders.py to create orders data")