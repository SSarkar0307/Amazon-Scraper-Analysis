import pandas as pd
from utils.visualization import plot_bar

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

def review_rating_distribution(df):
    """Analyze top products by reviews and ratings."""
    print("\nPerforming Review & Rating Distribution Analysis...")
    
    # Top 5 by Reviews
    top_reviews = df[['Title', 'Reviews']].sort_values(by='Reviews', ascending=False).head(5)
    
    # Top 5 by Rating (exclude NaN ratings)
    top_ratings = df[['Title', 'Rating']].dropna(subset=['Rating']).sort_values(by='Rating', ascending=False).head(5)
    
    # Actionable Insights
    print("\nActionable Insights:")
    print("- Top 5 Products by Reviews:")
    for _, row in top_reviews.iterrows():
        print(f"  {row['Title'][:40]}...: {row['Reviews']} reviews")
    
    print("- Top 5 Products by Rating:")
    for _, row in top_ratings.iterrows():
        print(f"  {row['Title'][:40]}...: {row['Rating']:.1f}")
    
    # Identify highly rated but less-reviewed products
    high_rated_low_reviews = df[(df['Rating'] >= 4.5) & 
                               (df['Reviews'] <= df['Reviews'].quantile(0.25)) & 
                               (df['Reviews'] > 0)]
    if not high_rated_low_reviews.empty:
        print("- Highly Rated but Less-Reviewed Products (Promotion Potential):")
        for _, row in high_rated_low_reviews[['Title', 'Rating', 'Reviews']].iterrows():
            print(f"  {row['Title'][:40]}...: Rating: {row['Rating']:.1f}, {row['Reviews']} reviews")
    
    # Visualizations
    plot_bar(
        data=top_reviews,
        x='Title',
        y='Reviews',
        title='Top 5 Most-Reviewed Sponsored Soft Toys',
        xlabel='Product Title',
        ylabel='Number of Reviews',
        filename='most_reviewed_products_bar.png'
    )
    
    plot_bar(
        data=top_ratings,
        x='Title',
        y='Rating',
        title='Top 5 Highest-Rated Sponsored Soft Toys',
        xlabel='Product Title',
        ylabel='Rating',
        filename='top_rated_products_bar.png'
    )

def main():
    """Main function for review & rating distribution analysis."""
    input_file = "soft_toys_cleaned.csv"
    df = load_cleaned_data(input_file)
    if df is None:
        return
    review_rating_distribution(df)

if __name__ == "__main__":
    main()