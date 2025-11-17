"""
GSR Data Processing Script

PURPOSE:
    Process recorded GSR data files by:
    1. Removing interference spikes from haptic motors
    2. Resampling to uniform 5Hz sampling rate
    3. Generating individual plots for manual inspection

USAGE:
    python process_gsr_data.py

OUTPUT:
    - Cleaned CSV files in GSR-data/processed/
    - Individual plots in GSR-data/plots/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import medfilt
import os
from pathlib import Path

# Configuration
INPUT_DIR = "GSR-data"
OUTPUT_DIR = "GSR-data/processed"
PLOT_DIR = "GSR-data/plots"
TARGET_SAMPLE_RATE = 5  # Hz
MEDIAN_FILTER_SIZE = 5  # Use odd number for median filter
RATE_CHANGE_THRESHOLD = 500  # Max allowed change between consecutive samples

# Create output directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

def remove_spikes(times, values):
    """
    Remove spike artifacts using a two-pass approach:
    1. Median filter to remove sharp spikes
    2. Rate-of-change filter to catch remaining large jumps
    
    Returns: cleaned times and values arrays (preserves all time points)
    """
    times = np.array(times)
    values = np.array(values)
    
    # Pass 1: Apply median filter to smooth out spikes
    # This replaces spikes with the median of surrounding values
    values_filtered = medfilt(values, kernel_size=MEDIAN_FILTER_SIZE)
    
    # Pass 2: Detect remaining spikes by rate of change
    # GSR changes slowly, so large jumps are likely artifacts
    spike_mask = np.zeros(len(values), dtype=bool)
    
    for i in range(1, len(values_filtered)):
        rate_of_change = abs(values_filtered[i] - values_filtered[i-1])
        if rate_of_change > RATE_CHANGE_THRESHOLD:
            spike_mask[i] = True
    
    # For detected spikes, interpolate from neighbors
    if np.any(spike_mask):
        spike_indices = np.where(spike_mask)[0]
        good_indices = np.where(~spike_mask)[0]
        
        if len(good_indices) > 1:
            # Interpolate spike values from good values
            interpolator = interp1d(good_indices, values_filtered[good_indices], 
                                   kind='linear', fill_value='extrapolate')
            values_filtered[spike_indices] = interpolator(spike_indices)
    
    num_spikes_removed = np.sum(spike_mask)
    
    return times, values_filtered, num_spikes_removed

def resample_uniform(times, values, target_hz=5):
    """
    Resample data to uniform sampling rate using linear interpolation.
    
    Returns: uniform time array and interpolated values
    """
    if len(times) < 2:
        return times, values
    
    # Create uniform time array
    start_time = times[0]
    end_time = times[-1]
    duration = end_time - start_time
    
    num_samples = int(duration * target_hz) + 1
    uniform_times = np.linspace(start_time, end_time, num_samples)
    
    # Interpolate values
    interpolator = interp1d(times, values, kind='linear', 
                           bounds_error=False, fill_value='extrapolate')
    uniform_values = interpolator(uniform_times)
    
    return uniform_times, uniform_values

def process_file(filepath):
    """Process a single GSR data file"""
    filename = os.path.basename(filepath)
    timestamp = filename.replace('gsr_', '').replace('.csv', '')
    
    print(f"\nProcessing: {filename}")
    
    # Read data
    df = pd.read_csv(filepath)
    times = df['Time (s)'].values
    values = df['GSR Value'].values
    
    print(f"  Original: {len(values)} samples")
    
    # Step 1: Remove spikes (now preserves all time points)
    times_clean, values_clean, num_spikes = remove_spikes(times, values)
    print(f"  After spike removal: {len(values_clean)} samples ({num_spikes} spikes smoothed)")
    
    # Step 2: Resample to uniform rate
    times_uniform, values_uniform = resample_uniform(times_clean, values_clean, TARGET_SAMPLE_RATE)
    print(f"  After resampling to {TARGET_SAMPLE_RATE}Hz: {len(values_uniform)} samples")
    
    # Step 3: Save processed data
    output_file = os.path.join(OUTPUT_DIR, f"processed_{timestamp}.csv")
    processed_df = pd.DataFrame({
        'Time (s)': times_uniform,
        'GSR Value': values_uniform
    })
    processed_df.to_csv(output_file, index=False)
    print(f"  Saved to: {output_file}")
    
    # Step 4: Create plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: Original vs Spike-removed
    ax1.plot(times, values, 'gray', alpha=0.5, linewidth=0.8, label='Original (with spikes)')
    ax1.plot(times_clean, values_clean, 'b-', linewidth=1.5, label='After median + spike filter')
    ax1.set_xlabel('Time (s)', fontsize=11)
    ax1.set_ylabel('GSR Value', fontsize=11)
    ax1.set_title(f'Step 1: Spike Removal (Median Filter + Rate Limit) - {timestamp}', fontsize=13, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Final processed data
    ax2.plot(times_uniform, values_uniform, 'g-', linewidth=1.5, label=f'Processed ({TARGET_SAMPLE_RATE}Hz)')
    ax2.set_xlabel('Time (s)', fontsize=11)
    ax2.set_ylabel('GSR Value', fontsize=11)
    ax2.set_title(f'Step 2: Uniform Resampling - {timestamp}', fontsize=13, fontweight='bold')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    # Add statistics text
    stats_text = f"Duration: {times_uniform[-1]:.1f}s\n"
    stats_text += f"Samples: {len(values_uniform)}\n"
    stats_text += f"Mean: {np.mean(values_uniform):.1f}\n"
    stats_text += f"Std: {np.std(values_uniform):.1f}"
    ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    fig.tight_layout()
    
    # Save plot
    plot_file = os.path.join(PLOT_DIR, f"plot_{timestamp}.png")
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Plot saved to: {plot_file}")
    
    return {
        'timestamp': timestamp,
        'original_samples': len(values),
        'spikes_smoothed': num_spikes,
        'final_samples': len(values_uniform),
        'duration': times_uniform[-1],
        'mean_gsr': np.mean(values_uniform),
        'std_gsr': np.std(values_uniform)
    }

def main():
    """Process all GSR files in the directory"""
    print("=" * 60)
    print("GSR Data Processing")
    print("=" * 60)
    
    # Find all GSR CSV files
    input_files = sorted(Path(INPUT_DIR).glob("gsr_*.csv"))
    
    print(f"\nFound {len(input_files)} files to process")
    
    # Process each file
    results = []
    for filepath in input_files:
        try:
            result = process_file(filepath)
            results.append(result)
        except Exception as e:
            print(f"  ERROR processing {filepath.name}: {e}")
    
    # Create summary
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    print(f"\nSuccessfully processed {len(results)} files")
    print(f"\nProcessed files saved to: {os.path.abspath(OUTPUT_DIR)}")
    print(f"Plots saved to: {os.path.abspath(PLOT_DIR)}")
    
    # Summary table
    print("\n" + "-" * 80)
    print(f"{'Timestamp':<17} {'Duration':<10} {'Samples':<8} {'Spikes':<8} {'Mean GSR':<10}")
    print("-" * 80)
    for r in results:
        print(f"{r['timestamp']:<17} {r['duration']:>8.1f}s  {r['final_samples']:>6}   "
              f"{r['spikes_smoothed']:>6}   {r['mean_gsr']:>8.1f}")
    print("-" * 80)
    
    print("\n✓ Processing complete!")
    print(f"\nNext step: Review plots in '{PLOT_DIR}' to identify experiments\n")

if __name__ == "__main__":
    main()

