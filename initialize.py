import os
import subprocess
import sys
import importlib.util

def check_requirements(input_file):
    """Check for required libraries and input file."""
    print("Checking requirements...")
    
    # Check for required libraries
    required_libraries = ['pandas', 'matplotlib', 'seaborn']
    for lib in required_libraries:
        if importlib.util.find_spec(lib) is None:
            print(f"Error: {lib} is not installed. Installing it now...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                print(f"{lib} installed successfully.")
            except subprocess.CalledProcessError:
                print(f"Error: Failed to install {lib}. Please install it manually with 'pip install {lib}'.")
                sys.exit(1)
    
    # Check for input CSV
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found in the current directory.")
        sys.exit(1)
    
    # Check for utils/visualization.py
    if not os.path.exists("utils/visualization.py"):
        print("Error: 'utils/visualization.py' not found. Ensure it is in the 'utils/' folder.")
        sys.exit(1)
    
    print("All requirements met.")

def run_script(script_name, input_file=None):
    """Run a Python script and handle errors."""
    print(f"\nRunning {script_name}...")
    try:
        # Pass input file as argument for part2_cleaning.py
        cmd = [sys.executable, script_name]
        if script_name == "part2_cleaning.py" and input_file:
            cmd.append(input_file)
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings/Errors from {script_name}:\n{result.stderr}")
        print(f"Completed {script_name} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:\n{e.output}\n{e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Error: {script_name} not found in the current directory.")
        return False
    return True

def main():
    """Main function to run all scripts sequentially."""
    print("Starting complete analysis pipeline...")
    
    # Specify input file (change to "soft_toys_sponsored_dummy.csv" for testing)
    input_file = "soft_toys_sponsored_dummy.csv"  # Or "soft_toys_sponsored.csv" for actual data
    
    # Check requirements
    check_requirements(input_file)
    
    # List of scripts to run in order
    scripts = [
        "part2_cleaning.py",
        "part3_analysis_brand.py",
        "part3_analysis_price_rating.py",
        "part3_analysis_reviews.py"
    ]
    
    # Run each script
    for script in scripts:
        if not run_script(script, input_file if script == "part2_cleaning.py" else None):
            print(f"Pipeline stopped due to error in {script}.")
            sys.exit(1)
    
    # Verify outputs
    print("\nVerifying outputs...")
    if os.path.exists("soft_toys_cleaned.csv"):
        print("✓ Cleaned data saved to 'soft_toys_cleaned.csv'.")
    else:
        print("✗ Cleaned data file 'soft_toys_cleaned.csv' not found.")
    
    output_dir = "output"
    if os.path.exists(output_dir):
        plots = [
            "brand_frequency_bar.png",
            "brand_share_pie.png",
            "price_vs_rating_scatter.png",
            "price_by_rating_bar.png",
            "most_reviewed_products_bar.png",
            "top_rated_products_bar.png"
        ]
        for plot in plots:
            if os.path.exists(os.path.join(output_dir, plot)):
                print(f"✓ Plot saved: {output_dir}/{plot}")
            else:
                print(f"✗ Plot missing: {output_dir}/{plot}")
    else:
        print(f"✗ Output directory '{output_dir}' not found.")
    
    print("\n✅ Complete analysis pipeline finished!")

if __name__ == "__main__":
    main()