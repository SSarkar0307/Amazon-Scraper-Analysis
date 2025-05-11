import pandas as pd
from utils.visualization import plot_scatter, plot_bar

def load_cleaned_data(file_path):
    """Load the cleaned CSV file."""
    try:
        print(f"Loading cleaned data from {file_path}...")
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} rows.")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def price_vs_rating_analysis(df):
    """Analyze price vs. rating relationship."""
    print("\nPerforming Price vs. Rating Analysis...")
    
    # Filter out rows with missing Price or Rating
    df_filtered = df.dropna(subset=['Price', 'Rating']).copy()
    
    # Create Rating Range column
    df_filtered.loc[:, 'Rating Range'] = pd.cut(
        df_filtered['Rating'], 
        bins=[0, 1, 2, 3, 4, 5], 
        labels=['0-1', '1-2', '2-3', '3-4', '4-5']
    )
    
    # Average Price by Rating Range
    price_by_rating = df_filtered.groupby('Rating Range', observed=True)['Price'].mean().reset_index()
    
    # Actionable Insights
    print("\nActionable Insights:")
    print("- Average Price by Rating Range:")
    for _, row in price_by_rating.iterrows():
        print(f"  {row['Rating Range']}: INR {row['Price']:.2f}")
    
    # High-value products (low price, high rating)
    high_value = df_filtered[(df_filtered['Price'] <= df_filtered['Price'].quantile(0.25)) & 
                             (df_filtered['Rating'] >= 4.5)]
    if not high_value.empty:
        print("- High-Value Products (Low Price, High Rating):")
        for _, row in high_value[['Title', 'Price', 'Rating']].iterrows():
            print(f"  {row['Title'][:40]}...: INR {row['Price']:.2f}, Rating: {row['Rating']:.1f}")
    
    # Overpriced low-rated products
    overpriced = df_filtered[(df_filtered['Price'] >= df_filtered['Price'].quantile(0.75)) & 
                             (df_filtered['Rating'] <= 3.0)]
    if not overpriced.empty:
        print("- Overpriced Low-Rated Products:")
        for _, row in overpriced[['Title', 'Price', 'Rating']].iterrows():
            print(f"  {row['Title'][:40]}...: INR {row['Price']:.2f}, Rating: {row['Rating']:.1f}")
    
    # Visualizations
    plot_scatter(
        data=df_filtered,
        x='Price',
        y='Rating',
        title='Price vs. Rating for Sponsored Soft Toys',
        xlabel='Price (INR)',
        ylabel='Rating',
        filename='price_vs_rating_scatter.png'
    )
    
    plot_bar(
        data=price_by_rating,
        x='Rating Range',
        y='Price',
        title='Average Price by Rating Range',
        xlabel='Rating Range',
        ylabel='Average Price (INR)',
        filename='price_by_rating_bar.png'
    )

def main():
    """Main function for price vs. rating analysis."""
    input_file = "soft_toys_cleaned.csv"
    df = load_cleaned_data(input_file)
    if df is None:
        return
    price_vs_rating_analysis(df)

if __name__ == "__main__":
    main()