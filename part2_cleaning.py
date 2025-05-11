import pandas as pd
import re
import os
import sys

def load_data(file_path):
    """Load the CSV file and return a DataFrame."""
    try:
        print(f"Loading data from {file_path}...")
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def clean_price(price):
    """Clean price by removing currency symbols, commas, and converting to float."""
    if pd.isna(price) or price == "N/A":
        return None
    try:
        # Remove ₹, commas, and other non-numeric characters
        cleaned_price = re.sub(r'[^\d.]', '', str(price))
        return float(cleaned_price) if cleaned_price else None
    except (ValueError, TypeError):
        return None

def clean_reviews(reviews):
    """Clean reviews by removing commas and converting to int."""
    if pd.isna(reviews) or reviews == "N/A":
        return 0
    try:
        # Remove commas and non-numeric characters
        cleaned_reviews = re.sub(r'[^\d]', '', str(reviews))
        return int(cleaned_reviews) if cleaned_reviews else 0
    except (ValueError, TypeError):
        return 0

def clean_rating(rating):
    """Clean rating by converting to float."""
    if pd.isna(rating) or rating == "N/A":
        return None
    try:
        return float(rating)
    except (ValueError, TypeError):
        return None

def clean_data(df):
    """Clean and prepare the DataFrame."""
    print("Starting data cleaning...")
    
    # Remove duplicates based on Product URL (unique identifier)
    initial_rows = len(df)
    df = df.drop_duplicates(subset=['Product URL'], keep='first')
    print(f"Removed {initial_rows - len(df)} duplicate rows. {len(df)} rows remain.")
    
    # Convert text columns to string type, handling NaN
    text_columns = ['Title', 'Brand', 'Image URL', 'Product URL']
    for col in text_columns:
        df[col] = df[col].astype(str).fillna('').replace('nan', '')
    
    # Clean and convert numeric columns
    df['Price'] = df['Price'].apply(clean_price)
    df['Reviews'] = df['Reviews'].apply(clean_reviews)
    df['Rating'] = df['Rating'].apply(clean_rating)
    
    # Standardize text columns
    df['Title'] = df['Title'].str.strip().replace('N/A', '')
    df['Brand'] = df['Brand'].str.strip().replace('Unknown', '')
    df['Image URL'] = df['Image URL'].str.strip()
    df['Product URL'] = df['Product URL'].str.strip()
    
    # Handle missing values
    # - Price/Rating: Keep as None (will handle in analysis)
    # - Title/Brand: Replace empty with 'Unknown'
    # - Image URL/Product URL: Keep as is
    df['Title'] = df['Title'].replace('', 'Unknown')
    df['Brand'] = df['Brand'].replace('', 'Unknown')
    
    # Drop 'Is Sponsored' column if present (not needed for analysis)
    if 'Is Sponsored' in df.columns:
        df = df.drop(columns=['Is Sponsored'])
        print("Dropped 'Is Sponsored' column.")
    
    # Verify data types
    print("\nData types after cleaning:")
    print(df.dtypes)
    
    # Summary of missing values
    print("\nMissing values after cleaning:")
    print(df.isna().sum())
    
    return df

def save_cleaned_data(df, output_path):
    """Save the cleaned DataFrame to a CSV file."""
    try:
        df.to_csv(output_path, index=False)
        print(f"Cleaned data saved to {output_path} with {len(df)} rows.")
    except Exception as e:
        print(f"Error saving cleaned data: {e}")

def main(input_file="soft_toys_sponsored.csv"):
    """Main function to clean and prepare the scraped data."""
    output_file = "soft_toys_cleaned.csv"
    
    # Load data
    df = load_data(input_file)
    if df is None:
        sys.exit(1)
    
    # Clean data
    df_cleaned = clean_data(df)
    
    # Save cleaned data
    save_cleaned_data(df_cleaned, output_file)

if __name__ == "__main__":
    # Check for command-line argument for input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "soft_toys_sponsored.csv"  # Default fallback
    main(input_file)