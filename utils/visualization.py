import matplotlib.pyplot as plt
import seaborn as sns
import os

def setup_plot_style():
    """Set up consistent plot styling."""
    sns.set_style("whitegrid")
    plt.rcParams['font.size'] = 12
    plt.rcParams['figure.figsize'] = (10, 6)

def save_plot(filename, output_dir="output"):
    """Save the plot to the output directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, bbox_inches='tight', dpi=300)
    print(f"Plot saved to {filepath}")
    plt.close()

def plot_bar(data, x, y, title, xlabel, ylabel, filename, top_n=None, output_dir="output"):
    """Create and save a bar chart."""
    setup_plot_style()
    if top_n:
        data = data.nlargest(top_n, y)
    plt.figure()
    sns.barplot(data=data, x=x, y=y, palette="viridis")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    save_plot(filename, output_dir)

def plot_pie(data, labels, title, filename, output_dir="output"):
    """Create and save a pie chart."""
    setup_plot_style()
    plt.figure()
    plt.pie(data, labels=labels, autopct='%1.1f%%', colors=sns.color_palette("viridis", len(labels)))
    plt.title(title)
    save_plot(filename, output_dir)

def plot_scatter(data, x, y, title, xlabel, ylabel, filename, output_dir="output"):
    """Create and save a scatter plot."""
    setup_plot_style()
    plt.figure()
    sns.scatterplot(data=data, x=x, y=y, hue=y, size=y, palette="viridis")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    save_plot(filename, output_dir)