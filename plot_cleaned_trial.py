"""
Plot Cleaned GSR Trial with Rolling Average

PURPOSE:
    Process and plot a single GSR trial with:
    1. Spike removal using median filter + rate-of-change detection
    2. Uniform 5Hz resampling
    3. 5-second rolling average overlay
    4. Phase markers (Baseline, Trial, Post)

USAGE:
    python plot_cleaned_trial.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import medfilt
import os

# Configuration
USER_ID = "62206"
TIMESTAMP = "20251120_163627"
INPUT_FILE = f"GSR-data/experiments/gsr_{USER_ID}_StateA_{TIMESTAMP}.csv"
OUTPUT_PLOT = f"GSR-data/plots/cleaned_{USER_ID}_{TIMESTAMP}.png"

TARGET_SAMPLE_RATE = 5  # Hz
MEDIAN_FILTER_SIZE = 5  # Odd number for median filter
RATE_CHANGE_THRESHOLD = 500  # Max allowed change between samples
ROLLING_WINDOW_SEC = 5  # Seconds for rolling average

# Ensure output directory exists
os.makedirs("GSR-data/plots", exist_ok=True)

def remove_spikes(times, values):
    """
    Remove spike artifacts using two-pass approach:
    1. Median filter to remove sharp spikes
    2. Rate-of-change filter to catch remaining large jumps
    """
    times = np.array(times)
    values = np.array(values)
    
    # Pass 1: Apply median filter
    values_filtered = medfilt(values, kernel_size=MEDIAN_FILTER_SIZE)
    
    # Pass 2: Detect remaining spikes by rate of change
    spike_mask = np.zeros(len(values), dtype=bool)
    
    for i in range(1, len(values_filtered)):
        rate_of_change = abs(values_filtered[i] - values_filtered[i-1])
        if rate_of_change > RATE_CHANGE_THRESHOLD:
            spike_mask[i] = True
    
    # Interpolate detected spikes from neighbors
    if np.any(spike_mask):
        spike_indices = np.where(spike_mask)[0]
        good_indices = np.where(~spike_mask)[0]
        
        if len(good_indices) > 1:
            interpolator = interp1d(good_indices, values_filtered[good_indices], 
                                   kind='linear', fill_value='extrapolate')
            values_filtered[spike_indices] = interpolator(spike_indices)
    
    num_spikes = np.sum(spike_mask)
    
    return times, values_filtered, num_spikes

def resample_uniform(times, values, target_hz=5):
    """Resample data to uniform sampling rate"""
    if len(times) < 2:
        return times, values
    
    start_time = times[0]
    end_time = times[-1]
    duration = end_time - start_time
    
    num_samples = int(duration * target_hz) + 1
    uniform_times = np.linspace(start_time, end_time, num_samples)
    
    interpolator = interp1d(times, values, kind='linear', 
                           bounds_error=False, fill_value='extrapolate')
    uniform_values = interpolator(uniform_times)
    
    return uniform_times, uniform_values

def calculate_rolling_average(values, window_samples):
    """Calculate rolling average"""
    return pd.Series(values).rolling(window=window_samples, center=True, min_periods=1).mean().values

def main():
    print("=" * 70)
    print(f"Processing GSR Trial: User {USER_ID}")
    print("=" * 70)
    
    # Read data
    print(f"\nReading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    times = df['Time (s)'].values
    values = df['GSR Value'].values
    phases = df['Phase'].values
    state = df['State'].values[0]
    
    print(f"  Original samples: {len(values)}")
    print(f"  Duration: {times[-1]:.1f}s")
    print(f"  State: {state}")
    
    # Find phase transitions
    phase_changes = []
    current_phase = phases[0]
    for i, phase in enumerate(phases):
        if phase != current_phase:
            phase_changes.append((times[i], phase))
            current_phase = phase
    
    print(f"  Phases detected: {list(set(phases))}")
    
    # Step 1: Remove spikes
    print("\nStep 1: Removing spikes...")
    times_clean, values_clean, num_spikes = remove_spikes(times, values)
    print(f"  Spikes smoothed: {num_spikes}")
    
    # Step 2: Resample to uniform rate
    print(f"\nStep 2: Resampling to {TARGET_SAMPLE_RATE}Hz...")
    times_uniform, values_uniform = resample_uniform(times_clean, values_clean, TARGET_SAMPLE_RATE)
    print(f"  Resampled samples: {len(values_uniform)}")
    
    # Step 3: Calculate rolling average
    print(f"\nStep 3: Calculating {ROLLING_WINDOW_SEC}s rolling average...")
    window_samples = ROLLING_WINDOW_SEC * TARGET_SAMPLE_RATE
    rolling_avg = calculate_rolling_average(values_uniform, window_samples)
    
    # Statistics
    print("\nStatistics (cleaned data):")
    print(f"  Mean GSR: {np.mean(values_uniform):.1f}")
    print(f"  Std Dev: {np.std(values_uniform):.1f}")
    print(f"  Min: {np.min(values_uniform):.1f}")
    print(f"  Max: {np.max(values_uniform):.1f}")
    
    # Create comprehensive plot
    print("\nCreating plot...")
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    
    # --- Plot 1: Original vs Cleaned ---
    ax1 = axes[0]
    ax1.plot(times, values, 'lightgray', alpha=0.6, linewidth=0.8, label='Original (with spikes)')
    ax1.plot(times_clean, values_clean, 'steelblue', linewidth=1.2, label='Spike-removed')
    ax1.set_ylabel('GSR Value', fontsize=12, fontweight='bold')
    ax1.set_title(f'Participant {USER_ID} - GSR Processing Pipeline | State: {state}', 
                  fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.text(0.01, 0.98, 'Step 1: Spike Removal', transform=ax1.transAxes,
            fontsize=11, verticalalignment='top', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Add phase markers
    for phase_time, phase_name in phase_changes:
        ax1.axvline(x=phase_time, color='red', linestyle='--', alpha=0.5, linewidth=2)
        ax1.text(phase_time, ax1.get_ylim()[1]*0.95, f'→ {phase_name}',
                rotation=0, fontsize=9, color='red', fontweight='bold')
    
    # --- Plot 2: Uniform Resampled ---
    ax2 = axes[1]
    ax2.plot(times_uniform, values_uniform, 'forestgreen', linewidth=1.2, 
            label=f'Resampled ({TARGET_SAMPLE_RATE}Hz)')
    ax2.set_ylabel('GSR Value', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.text(0.01, 0.98, 'Step 2: Uniform Resampling', transform=ax2.transAxes,
            fontsize=11, verticalalignment='top', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Add phase markers
    for phase_time, phase_name in phase_changes:
        ax2.axvline(x=phase_time, color='red', linestyle='--', alpha=0.5, linewidth=2)
    
    # --- Plot 3: Final with Rolling Average ---
    ax3 = axes[2]
    ax3.plot(times_uniform, values_uniform, 'lightblue', linewidth=1, alpha=0.7, 
            label=f'Cleaned Data ({TARGET_SAMPLE_RATE}Hz)')
    ax3.plot(times_uniform, rolling_avg, 'darkblue', linewidth=2.5, 
            label=f'{ROLLING_WINDOW_SEC}s Rolling Average')
    ax3.set_xlabel('Time (s)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('GSR Value', fontsize=12, fontweight='bold')
    ax3.legend(loc='upper right', fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # Add statistics box
    stats_text = f"Duration: {times_uniform[-1]:.1f}s\n"
    stats_text += f"Samples: {len(values_uniform)}\n"
    stats_text += f"Mean: {np.mean(values_uniform):.1f}\n"
    stats_text += f"Std: {np.std(values_uniform):.1f}\n"
    stats_text += f"Spikes removed: {num_spikes}"
    ax3.text(0.01, 0.98, stats_text, transform=ax3.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    ax3.text(0.99, 0.98, f'Step 3: Rolling Average ({ROLLING_WINDOW_SEC}s)', 
            transform=ax3.transAxes,
            fontsize=11, verticalalignment='top', horizontalalignment='right',
            fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Add phase markers and colored regions
    phase_colors = {'Baseline': 'lightgreen', 'Trial': 'lightyellow', 'Post': 'lightcoral'}
    
    phase_start = times_uniform[0]
    for phase_time, phase_name in phase_changes:
        ax3.axvline(x=phase_time, color='red', linestyle='--', alpha=0.7, linewidth=2.5)
        ax3.text(phase_time, ax3.get_ylim()[1]*0.95, f'→ {phase_name}',
                rotation=0, fontsize=10, color='red', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        phase_start = phase_time
    
    fig.tight_layout()
    
    # Save plot
    plt.savefig(OUTPUT_PLOT, dpi=200, bbox_inches='tight')
    print(f"\n✓ Plot saved to: {os.path.abspath(OUTPUT_PLOT)}")
    
    # Also save processed data
    output_csv = f"GSR-data/processed/cleaned_{USER_ID}_{TIMESTAMP}.csv"
    os.makedirs("GSR-data/processed", exist_ok=True)
    
    processed_df = pd.DataFrame({
        'Time (s)': times_uniform,
        'GSR Value': values_uniform,
        'Rolling Average': rolling_avg
    })
    processed_df.to_csv(output_csv, index=False)
    print(f"✓ Processed data saved to: {os.path.abspath(output_csv)}")
    
    print("\n" + "=" * 70)
    print("Processing complete!")
    print("=" * 70)
    
    plt.show()

if __name__ == "__main__":
    main()

