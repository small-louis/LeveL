# Slot Machine GUI Version

A graphical user interface version of the slot machine game with full data logging capabilities for research trials.

## Features

### Visual Interface
- 🎰 **Colorful slot machine display** with 3x3 grid
- 💰 **Real-time balance tracking**
- 🎨 **Color-coded symbols** for easy recognition
  - A (Gold) - Highest value ($5)
  - B (Red) - High value ($4)
  - C (Teal) - Medium value ($3)
  - D (Mint) - Base value ($2)
- ✨ **Animated spinning** effect
- 🎉 **Visual feedback** for winning lines

### Game Controls
- **Bet amount entry**: Set any bet per line (minimum $10, no maximum)
- **Line selection**: Choose 1-3 betting lines
- **Total bet display**: See your total wager before spinning
- **Easy spin button**: Large, clear button to play
- **Quit & Save**: Safely exit and save session data

### Data Logging
All the same behavioral metrics are tracked as the CLI version:
- Participant and group IDs
- Complete spin history
- Bet escalation patterns
- Loss chasing behavior
- All-in detection
- Post-big-win behavior
- Time between spins
- Session duration

Data is saved to `session_data/` directory in CSV format.

## How to Run

### Quick Start
```bash
python app_gui.py
```

### Startup Process
1. **Enter Participant ID** (optional) - for trial organization
2. **Enter Group/Condition ID** (optional) - for experimental conditions
3. **Deposit Initial Balance** - starting money for the session
4. **Play!**

### During Gameplay
1. **Set your bet** - Enter any amount per line (minimum $10, no maximum)
2. **Choose lines** - Select 1, 2, or 3 lines to bet on
3. **Check total bet** - Verify the total amount shown
4. **Click SPIN** - Watch the animation and see results
5. **View results** - Winning lines and amounts are highlighted
6. **Repeat** - Continue playing or click "Quit & Save"

### Ending Session
- Click **"Quit & Save"** button at any time
- Game automatically ends if balance reaches $0
- Session data is saved to CSV file with timestamp
- Confirmation dialog shows save location

## Game Rules

### Winning
- All 3 symbols in a line must match to win
- You can win on multiple lines in one spin
- Winnings = Symbol Value × Bet Per Line

### Symbol Values
| Symbol | Frequency | Payout Multiplier |
|--------|-----------|-------------------|
| A      | Rare (2)  | 5x               |
| B      | Uncommon (4) | 4x            |
| C      | Common (6) | 3x               |
| D      | Very Common (8) | 2x          |

### Betting Lines
- **Line 1**: Top row
- **Line 2**: Middle row
- **Line 3**: Bottom row

## Data Output

Session logs are saved to: `session_data/PARTICIPANTID_YYYYMMDD_HHMMSS.csv`

**Example filenames:**
- `session_data/P001_20251120_143022.csv` (with participant ID)
- `session_data/20251120_143022.csv` (without participant ID)

**Note:** The participant ID is in the **filename**, not in the CSV columns.

### Columns Tracked:
- `group_id` - Group/condition identifier
- `spin_number` - Sequential spin count
- `timestamp` - Unix timestamp of spin
- `bet_per_line` - Amount bet per line
- `num_lines` - Number of lines bet on
- `total_bet` - Total amount wagered
- `winnings` - Amount won
- `winning_lines` - Which lines won (pipe-separated)
- `balance_after_spin` - Remaining balance
- `time_since_last_spin_sec` - Seconds since previous spin
- `bet_escalation` - Whether bet increased
- `loss_chasing` - Bet increase after loss
- `all_in` - Bet entire balance
- `after_big_win` - Following a large win (>30% of initial deposit)
- `session_duration_sec` - Total session time (final row only)

## Technical Details

### Requirements
- Python 3.x
- tkinter (usually included with Python)

### File Structure
```
Slot-Machine/
├── app_gui.py          # GUI version (this file)
├── app.py              # CLI version (original)
├── session_data/       # Logged session data
│   └── *.csv          # Individual session files
└── GUI_README.md       # This file
```

### Threading
The GUI uses threading to prevent the interface from freezing during spins, ensuring smooth animations and responsive controls.

### Color Scheme
- Background: Dark navy (#1a1a2e)
- Panels: Deep blue (#16213e, #0f3460)
- Symbols: Gold, Red, Teal, Mint
- Balance: Green
- Buttons: Green (spin), Red (quit)

## Troubleshooting

### "tkinter not found" Error
If you get an error about tkinter not being installed:

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

**macOS:**
tkinter should be included. If missing, reinstall Python from python.org

**Windows:**
tkinter is included with Python installer. Reinstall Python if needed.

### GUI Window Too Small/Large
You can resize the window by dragging corners. The interface will adjust.

### Session Data Not Saving
- Check that the script has write permissions
- Verify `session_data/` directory is created
- Check console output for save confirmation and file path

## Differences from CLI Version

### Advantages of GUI:
✅ Visual feedback and animations
✅ Easier to use for participants
✅ No typing required (reduces input errors)
✅ More engaging and professional appearance
✅ Real-time display of all information
✅ Better for research lab settings

### Maintained Features:
✅ Identical game logic
✅ Same data logging
✅ Same behavioral metrics
✅ Compatible CSV output format

## For Researchers

This GUI version is ideal for:
- Laboratory studies with controlled environments
- Studies examining gambling behavior
- Risk-taking assessments
- Decision-making under uncertainty research
- Behavioral economics experiments

The data output format is identical to the CLI version, so analysis scripts will work with both versions.

## Support

For issues or questions:
1. Check this README
2. Review the original documentation files
3. Check the code comments in `app_gui.py`

---

**Note**: This GUI version maintains 100% compatibility with the original CLI version's data output format, ensuring seamless integration with existing analysis pipelines.

