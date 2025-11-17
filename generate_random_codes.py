"""
Random 5-Digit Code Generator

PURPOSE:
    Generates 30 random 5-digit codes (10000-99999) and exports to CSV.

USAGE:
    Run: python generate_random_codes.py
    
OUTPUT:
    Creates 'random_codes_TIMESTAMP.csv' with 30 unique random 5-digit values.
"""

import csv
import random
from datetime import datetime

def generate_random_codes(count=30):
    """Generate list of random 5-digit codes"""
    codes = []
    for _ in range(count):
        code = random.randint(10000, 99999)
        codes.append(code)
    return codes

def save_to_csv(codes):
    """Save codes to CSV file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"random_codes_{timestamp}.csv"
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Code'])  # Header
        for code in codes:
            writer.writerow([code])
    
    print(f"✓ Generated {len(codes)} random 5-digit codes")
    print(f"✓ Saved to: {filename}")
    return filename

if __name__ == "__main__":
    codes = generate_random_codes(30)
    save_to_csv(codes)

