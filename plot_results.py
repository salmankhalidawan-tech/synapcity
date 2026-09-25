"""Generates a publication-ready, high-resolution bar chart from the summary CSV."""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def generate_academic_chart():
    summary_file = "results/comparison_summary.csv"
    if not os.path.exists(summary_file):
        print(f"Error: {summary_file} not found.")
        return

    # Load data
    df = pd.read_csv(summary_file, index_col=0)
    metrics = ["cost_total", "carbon_emissions_total", "ramping_average"]
    plot_df = df[metrics]

    # Clean up the labels for the paper (e.g., "ablation_no_safety_gate" -> "No Safety Gate")
    clean_labels = [label.replace("ablation_", "").replace("_", " ").title().replace("Synapcity", "SynapCity") for label in plot_df.index]
    
    # Use a clean, minimalist style
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Professional color palette (Colorblind friendly & high contrast)
    colors = ['#0072B2', '#D55E00', '#009E73'] 
    metric_names = ['Cost Total', 'Carbon Emissions', 'Ramping Average']

    fig, ax = plt.subplots(figsize=(11, 6.5))
    
    x = np.arange(len(plot_df.index))
    width = 0.22  # Slightly thinner bars for elegance
    
    for i, metric in enumerate(metrics):
        offset = (i - 1) * (width + 0.02) # Add slight padding between grouped bars
        ax.bar(x + offset, plot_df[metric], width, 
               label=metric_names[i], 
               color=colors[i], 
               edgecolor='black', # Crisp borders
               linewidth=0.8)

    # Typography and formatting
    ax.set_ylabel('Normalized Score', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('Ablation Study: System Performance by Configuration', fontsize=14, fontweight='bold', pad=15)
    
    ax.set_xticks(x)
    ax.set_xticklabels(clean_labels, rotation=35, ha='right', fontsize=11)
    ax.tick_params(axis='y', labelsize=10)
    
    # Legend styling
    ax.legend(loc='upper right', fontsize=10, frameon=True, framealpha=0.9, edgecolor='black')
    
    # Grid styling (only horizontal, subtle)
    ax.yaxis.grid(True, linestyle='--', alpha=0.6, color='gray')
    ax.xaxis.grid(False)
    
    plt.tight_layout()
    
    output_path = "results/ablation_kpis_academic_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved publication-ready chart to {output_path}")

if __name__ == "__main__":
    generate_academic_chart()