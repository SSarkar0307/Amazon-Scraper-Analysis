import pandas as pd
from utils.visualization import plot_bar, plot_pie

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

def brand_performance_analysis(df):
    """Analyze brand frequency and average rating."""
    print("\nPerforming Brand Performance Analysis...")
    
    # Brand Frequency
    brand_counts = df['Brand'].value_counts().reset_index()
    brand_counts.columns = ['Brand', 'Frequency']
    
    # Average Rating by Brand
    brand_ratings = df.groupby('Brand')['Rating'].mean().reset_index()
    brand_ratings = brand_ratings[brand_ratings['Rating'].notna()]
    
    # Merge frequency and ratings
    brand_analysis = brand_counts.merge(brand_ratings, on='Brand', how='left')
    brand_analysis = brand_analysis.sort_values('Frequency', ascending=False)
    
    # Actionable Insights
    print("\nActionable Insights:")
    top_brands = brand_analysis.head(5)
    print("- Top 5 Brands by Frequency:")
    for _, row in top_brands.iterrows():
        print(f"  {row['Brand']}: {row['Frequency']} products, Avg Rating: {row['Rating']:.2f}")
    
    high_rated_low_freq = brand_analysis[(brand_analysis['Rating'] >= 4.5) & 
                                        (brand_analysis['Frequency'] <= brand_analysis['Frequency'].quantile(0.25))]
    if not high_rated_low_freq.empty:
        print("- High-Rated but Less Frequent Brands (Potential Opportunities):")
        for _, row in high_rated_low_freq.iterrows():
            print(f"  {row['Brand']}: {row['Frequency']} products, Avg Rating: {row['Rating']:.2f}")
    
    # Visualizations
    plot_bar(
        data=brand_analysis,
        x='Brand',
        y='Frequency',
        title='Top 5 Brands by Frequency',
        xlabel='Brand',
        ylabel='Number of Sponsored Products',
        filename='brand_frequency_bar.png',
        top_n=5
    )
    
    plot_pie(
        data=brand_analysis['Frequency'].head(5),
        labels=brand_analysis['Brand'].head(5),
        title='Percentage Share of Top 5 Brands',
        filename='brand_share_pie.png'
    )

def main():
    """Main function for brand performance analysis."""
    input_file = "soft_toys_cleaned.csv"
    df = load_cleaned_data(input_file)
    if df is None:
        return
    brand_performance_analysis(df)

if __name__ == "__main__":
    main()