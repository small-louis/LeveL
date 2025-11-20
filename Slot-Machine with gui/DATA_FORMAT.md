# Data Export Format

## Filename Structure

The participant ID is now stored in the **filename**, not within the CSV.

### Filename Format:
```
{participant_id}_{timestamp}.csv
```

### Examples:
- `P001_20251120_143022.csv` - Participant P001's session
- `participant_42_20251120_151530.csv` - Participant 42's session
- `20251120_143022.csv` - Session without participant ID (blank input)

### Location:
All CSV files are saved in the `session_data/` directory.

---

## CSV Structure

### Header Row:
```csv
group_id,spin_number,timestamp,bet_per_line,num_lines,total_bet,winnings,winning_lines,balance_after_spin,time_since_last_spin_sec,bet_escalation,loss_chasing,all_in,after_big_win,session_duration_sec
```

### Column Descriptions:

| Column | Type | Description |
|--------|------|-------------|
| `group_id` | String | Experimental group/condition identifier |
| `spin_number` | Integer | Sequential spin counter (1, 2, 3...) |
| `timestamp` | Float | Unix timestamp of the spin |
| `bet_per_line` | Integer | Dollar amount bet per line (minimum $10) |
| `num_lines` | Integer | Number of lines bet on (1-3) |
| `total_bet` | Integer | Total wager (bet_per_line × num_lines) |
| `winnings` | Integer | Amount won on this spin |
| `winning_lines` | String | Pipe-separated winning line numbers (e.g., "1\|3") |
| `balance_after_spin` | Integer | Remaining balance after spin |
| `time_since_last_spin_sec` | Float | Seconds elapsed since previous spin |
| `bet_escalation` | Boolean | True if bet increased from previous spin |
| `loss_chasing` | Boolean | True if bet increased after a loss |
| `all_in` | Boolean | True if entire balance was wagered |
| `after_big_win` | Boolean | True if previous spin had big win (>30% of initial deposit) |
| `session_duration_sec` | Float | Total session time (only in final row) |

---

## Example CSV Content

**Filename:** `P001_20251120_143022.csv`

```csv
group_id,spin_number,timestamp,bet_per_line,num_lines,total_bet,winnings,winning_lines,balance_after_spin,time_since_last_spin_sec,bet_escalation,loss_chasing,all_in,after_big_win,session_duration_sec
control,1,1732108862.45,10,1,10,0,,490,,False,False,False,False
control,2,1732108875.12,10,1,10,0,,480,12.67,False,False,False,False
control,3,1732108889.34,10,2,20,0,,460,14.22,False,False,False,False
control,4,1732108901.78,10,1,10,0,,450,12.44,False,False,False,False
control,5,1732108915.23,30,3,90,120,1,480,13.45,True,True,False,False
control,6,1732108930.56,10,3,30,0,,450,15.33,False,False,False,False
SESSION END,,,,,,,450,,,,,,487.11
```

### Understanding the Example:

**Initial Deposit:** $500 (so big win threshold = $500 × 0.30 = $150)
**Spin 1-4:** Player starts cautiously with small bets
**Spin 5:** Player escalates bet to $30 after losses (loss_chasing=True), wins $120 (below $150 threshold, not a big win)
**Spin 6:** Returns to smaller bet after win
**Final Row:** Session ended with $450 balance, lasted 487.11 seconds (~8 minutes)

**Note:** If any spin had won more than $150, the next spin would have `after_big_win=True`.

---

## Behavioral Metrics Explained

### Bet Escalation
Occurs when current bet > previous bet. Useful for tracking risk-taking increases.

### Loss Chasing
Occurs when player increases bet immediately after a loss. Classic gambling behavior indicator.

### All-In
Player bets entire remaining balance. Indicates high risk-taking or desperation.

### After Big Win
Tracks behavior following large wins (>30% of initial deposit). For example, if a player deposits $500, any win exceeding $150 is considered a "big win". Research shows big wins affect subsequent betting patterns. This dynamic threshold ensures the metric is meaningful regardless of the initial stake size.

---

## Data Analysis Tips

### Loading the Data:
```python
import pandas as pd

# Load a single session
df = pd.read_csv('session_data/P001_20251120_143022.csv')

# Extract participant ID from filename
participant_id = 'P001_20251120_143022.csv'.split('_')[0]

# Filter out the SESSION END row
df_spins = df[df['group_id'] != 'SESSION END']
df_session = df[df['group_id'] == 'SESSION END']
```

### Common Analyses:
1. **Total money lost/gained:** `final_balance - initial_deposit`
2. **Average bet:** `df['total_bet'].mean()`
3. **Loss chasing frequency:** `df['loss_chasing'].sum()`
4. **Time per spin:** `df['time_since_last_spin_sec'].mean()`
5. **Risk escalation patterns:** Track `bet_per_line` over `spin_number`

### Combining Multiple Sessions:
```python
import os
import glob

all_files = glob.glob('session_data/*.csv')
dfs = []

for file in all_files:
    # Extract participant ID from filename
    participant_id = os.path.basename(file).split('_')[0]
    
    df = pd.read_csv(file)
    df['participant_id'] = participant_id
    dfs.append(df)

# Combine all sessions
combined = pd.concat(dfs, ignore_index=True)
```

---

## Changes from Original Format

### Previous Format:
- Participant ID was **first column** in CSV
- Filename: `YYYYMMDD_HHMMSS.csv`

### Current Format:
- Participant ID is **in filename**
- Filename: `PARTICIPANTID_YYYYMMDD_HHMMSS.csv`
- CSV has one fewer column

### Why This Change?
✅ Easier to identify files by participant
✅ Faster file sorting and organization
✅ Prevents accidental data mixing
✅ Simpler data loading (ID from filename)
✅ Cleaner CSV structure

