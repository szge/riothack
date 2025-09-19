import matplotlib.pyplot as plt
import json
import numpy as np
from review_analysis import CATEGORIES

with open('experiments/common_complaints/categorized_reviews.json', 'r') as f:
    data = json.load(f)

category_colors = {
    "learning_curve_and_complexity": "#FF6B6B",  # Red
    "hostile_community_environment": "#4ECDC4",  # Teal
    "matchmaking_issues": "#45B7D1",  # Blue
    "time_investment_requirements": "#96CEB4",  # Green
    "technical_and_interface_issues": "#FFEAA7"  # Yellow
}

# Prepare data for visualization
complaints = []
counts = []
colors = []
labels = []

# Extract data and prepare for sorting
for major_category, subcategories in data["complaint_categories"].items():
    for subcategory, count in subcategories.items():
        complaints.append((count, subcategory, major_category))

# Sort by count (descending)
complaints.sort(reverse=True)

# Prepare final data for plotting
for count, subcategory, major_category in complaints:
    counts.append(count)
    colors.append(category_colors[major_category])
    # Get the full description from CATEGORIES
    full_label = CATEGORIES[major_category][subcategory]
    labels.append(full_label)

# Create the visualization
plt.figure(figsize=(14, 10))

# Create horizontal bar chart
bars = plt.barh(range(len(labels)), counts, color=colors, alpha=0.8, edgecolor='white', linewidth=0.5)

# Customize the plot
plt.xlabel('Number of Reviews Mentioning This Complaint', fontsize=12, fontweight='bold')
plt.ylabel('Complaint Categories', fontsize=12, fontweight='bold')
plt.title('League of Legends New Player Complaints Analysis\n(Based on 700 Reviews)', 
          fontsize=14, fontweight='bold', pad=20)

# Set y-axis labels
plt.yticks(range(len(labels)), labels, fontsize=10)
plt.gca().invert_yaxis()  # Highest counts at top

# Add count labels on bars
for i, (bar, count) in enumerate(zip(bars, counts)):
    plt.text(count + 1, i, str(count), va='center', fontweight='bold', fontsize=10)

# Create legend
legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.8, label=category.replace('_', ' ').title()) 
                  for category, color in category_colors.items()]
plt.legend(handles=legend_elements, loc='lower right', fontsize=10, title='Major Categories', title_fontsize=11)

# Add grid for better readability
plt.grid(axis='x', alpha=0.3, linestyle='--')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Add summary statistics
total_complaints = sum(counts)
plt.figtext(0.02, 0.02, f'Total Reviews: {data["num_reviews"]} | Total Complaint Mentions: {total_complaints}', 
           fontsize=10, style='italic')

# Display the plot
plt.show()

# Print summary statistics
print(f"\n=== REVIEW ANALYSIS SUMMARY ===")
print(f"Total reviews processed: {data['num_reviews']}")
print(f"Total complaint mentions: {total_complaints}")
print(f"Average complaints per review: {total_complaints/data['num_reviews']:.2f}")

print(f"\n=== TOP 5 MOST COMMON COMPLAINTS ===")
for i, (count, subcategory, major_category) in enumerate(complaints[:5], 1):
    full_label = CATEGORIES[major_category][subcategory]
    print(f"{i}. {full_label}: {count} mentions")

print(f"\n=== COMPLAINTS BY MAJOR CATEGORY ===")
category_totals = {}
for major_category, subcategories in data["complaint_categories"].items():
    total = sum(subcategories.values())
    category_totals[major_category] = total
    print(f"{major_category.replace('_', ' ').title()}: {total} mentions")

# Sort categories by total mentions
sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
print(f"\nMost problematic category: {sorted_categories[0][0].replace('_', ' ').title()} ({sorted_categories[0][1]} mentions)")