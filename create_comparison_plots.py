"""
Create comparison plots for GSR experiment analysis

EASY CONFIGURATION - Edit the labels and titles below:
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# ============================================================================
# CONFIGURATION - EDIT THESE TO CUSTOMIZE YOUR PLOTS
# ============================================================================

# Plot 1: Dual comparison
PLOT1_FILES = ["163147", "172831"]  # Last 3 digits of filenames
PLOT1_LABELS = ["User_01 Intervention On", "User_01 Intervention Off"]  # Custom labels
PLOT1_TITLE = "Slot Machine - User_01 Intervention On vs Off"  # Chart title
PLOT1_OUTPUT = "User_01 Intervention On vs Off"  # Output filename

# Plot 2: Dual comparison
PLOT2_FILES = ["165937", "174819"]
PLOT2_LABELS = ["User_02 Intervention On", "User_02 Intervention Off"]  # Custom labels
PLOT2_TITLE = "Slot Machine - User_02 Intervention On vs Off"  # Chart title
PLOT2_OUTPUT = "User_02 Intervention On vs Off"  # Output filename

# Plot 3: Dual comparison
PLOT3_FILES = ["172153", "180146"]
PLOT3_LABELS = ["User_03 Intervention On", "User_03 Intervention Off"]  # Custom labels
PLOT3_TITLE = "Slot Machine - User_03 Intervention On vs Off"  # Chart title
PLOT3_OUTPUT = "User_03 Intervention On vs Off"  # Output filename

# Plot 4: Triple comparison
PLOT4_FILES = ["164151", "170512", "172515"]
PLOT4_LABELS = ["User_01", "User_02", "User_03"]
PLOT4_TITLE = "Iowa gambling task - User_01 vs User_02 vs User_03"
PLOT4_OUTPUT = "Iowa gambling task - User_01 vs User_02 vs User_03"

# ============================================================================

# Processed data directory
PROCESSED_DIR = "GSR-data/processed"
OUTPUT_DIR = "GSR-data/comparisons"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_processed_data(suffix):
    """Load processed CSV file by last 3 digits"""
    filename = f"processed_20251030_{suffix}.csv"
    filepath = os.path.join(PROCESSED_DIR, filename)
    df = pd.read_csv(filepath)
    return df['Time (s)'].values, df['GSR Value'].values

def create_dual_comparison(suffix1, suffix2, label1, label2, title, output_name):
    """Create comparison plot with two experiments"""
    # Load data
    times1, values1 = load_processed_data(suffix1)
    times2, values2 = load_processed_data(suffix2)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot both datasets
    ax.plot(times1, values1, 'b-', linewidth=2, label=label1, alpha=0.8)
    ax.plot(times2, values2, 'r-', linewidth=2, label=label2, alpha=0.8)
    
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('GSR Value', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Created: {output_path}")

def create_triple_comparison(suffix1, suffix2, suffix3, label1, label2, label3, title, output_name):
    """Create comparison plot with three experiments"""
    # Load data
    times1, values1 = load_processed_data(suffix1)
    times2, values2 = load_processed_data(suffix2)
    times3, values3 = load_processed_data(suffix3)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot all three datasets
    ax.plot(times1, values1, 'b-', linewidth=2, label=label1, alpha=0.8)
    ax.plot(times2, values2, 'r-', linewidth=2, label=label2, alpha=0.8)
    ax.plot(times3, values3, 'g-', linewidth=2, label=label3, alpha=0.8)
    
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('GSR Value', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Created: {output_path}")

def main():
    print("=" * 60)
    print("Creating GSR Comparison Plots")
    print("=" * 60)
    print()
    
    # Dual comparisons
    print("Creating dual comparisons...")
    create_dual_comparison(
        PLOT1_FILES[0], PLOT1_FILES[1],
        PLOT1_LABELS[0], PLOT1_LABELS[1],
        PLOT1_TITLE, PLOT1_OUTPUT
    )
    create_dual_comparison(
        PLOT2_FILES[0], PLOT2_FILES[1],
        PLOT2_LABELS[0], PLOT2_LABELS[1],
        PLOT2_TITLE, PLOT2_OUTPUT
    )
    create_dual_comparison(
        PLOT3_FILES[0], PLOT3_FILES[1],
        PLOT3_LABELS[0], PLOT3_LABELS[1],
        PLOT3_TITLE, PLOT3_OUTPUT
    )
    
    print()
    
    # Triple comparison
    print("Creating triple comparison...")
    create_triple_comparison(
        PLOT4_FILES[0], PLOT4_FILES[1], PLOT4_FILES[2],
        PLOT4_LABELS[0], PLOT4_LABELS[1], PLOT4_LABELS[2],
        PLOT4_TITLE, PLOT4_OUTPUT
    )
    
    print()
    print("=" * 60)
    print("✓ All comparison plots created!")
    print(f"Saved to: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 60)

if __name__ == "__main__":
    main()

