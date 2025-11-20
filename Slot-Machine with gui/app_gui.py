import random
import time
import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading

MAX_LINES = 3
MIN_BET = 10
ROWS = 3
COLS = 3

symbol_count = { "A": 2, "B": 4, "C": 6, "D": 8 }
symbol_value = { "A": 5, "B": 4, "C": 3, "D": 2 }

# Symbol colors for visual appeal
SYMBOL_COLORS = {
    "A": "#FFD700",  # Gold
    "B": "#FF4757",  # Bright Red
    "C": "#5F27CD",  # Purple
    "D": "#00D2D3"   # Cyan
}

def check_winnings(columns, lines, bet, values):
    winnings = 0
    winning_lines = []
    for line in range(lines):
        symbol = columns[0][line]
        for column in columns:
            symbol_to_check = column[line]
            if symbol != symbol_to_check:
                break
        else:
            winnings += values[symbol] * bet
            winning_lines.append(line + 1)
    return winnings, winning_lines

def get_slot_machine_spin(rows, cols, symbols):
    all_symbols = []
    for symbol, symbol_count in symbols.items():
        for _ in range(symbol_count):
            all_symbols.append(symbol)
    columns = []
    for _ in range(cols):
        column = []
        current_symbol = all_symbols[:]
        for _ in range(rows):
            value = random.choice(current_symbol)
            current_symbol.remove(value)
            column.append(value)
        columns.append(column)
    return columns

def get_session_log_path(participant_id=""):
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session_data")
    if not os.path.exists(directory):
        os.makedirs(directory)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if participant_id:
        filename = f"{participant_id}_{timestamp}.csv"
    else:
        filename = f"{timestamp}.csv"
    return os.path.join(directory, filename)

class SessionLogger:
    def __init__(self, participant_id="", group_id=""):
        self.log = []
        self.path = get_session_log_path(participant_id)
        self.start_time = time.time()
        self.previous_spin_time = None
        self.largest_win = 0
        self.largest_loss = 0
        self.participant_id = participant_id
        self.group_id = group_id

    def log_spin(self, spin_number, timestamp, bet, lines, total_bet, winnings, winning_lines, balance, bet_escalation, loss_chase, time_since_last_spin, is_all_in, after_big_win):
        spin_data = [
            self.group_id,
            spin_number,
            timestamp,
            bet,
            lines,
            total_bet,
            winnings,
            "|".join(str(l) for l in winning_lines),
            balance,
            round(time_since_last_spin,2) if time_since_last_spin is not None else "",
            bet_escalation,
            loss_chase,
            is_all_in,
            after_big_win
        ]
        self.log.append(spin_data)

    def log_quit(self, final_balance, total_spins, final_time):
        session_metrics = [
            "SESSION END",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            final_balance,
            "",
            "",
            "",
            "",
            "",
            final_time - self.start_time
        ]
        self.log.append(session_metrics)

    def save(self):
        with open(self.path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "group_id","spin_number","timestamp","bet_per_line","num_lines","total_bet",
                "winnings","winning_lines","balance_after_spin","time_since_last_spin_sec",
                "bet_escalation","loss_chasing","all_in","after_big_win","session_duration_sec"
            ])
            writer.writerows(self.log)
        print(f"Session log saved to {self.path}")


class SlotMachineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Slot Machine Game")
        self.root.geometry("800x900")
        self.root.configure(bg="#1a1a2e")
        
        # Game state
        self.balance = 0
        self.initial_deposit = 0
        self.spin_count = 0
        self.prev_bet = None
        self.prev_was_loss = False
        self.prev_balance = 0
        self.prev_spin_time = None
        self.after_big_win = False
        self.logger = None
        self.game_started = False
        self.spinning = False
        
        self.setup_ui()
        self.show_startup_dialog()
    
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#1a1a2e")
        title_frame.pack(pady=20)
        
        title = tk.Label(title_frame, text="🎰 SLOT MACHINE 🎰", 
                        font=("Arial", 32, "bold"), 
                        fg="#FFD700", bg="#1a1a2e")
        title.pack()
        
        # Balance display
        balance_frame = tk.Frame(self.root, bg="#16213e", relief=tk.RAISED, bd=3)
        balance_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.balance_label = tk.Label(balance_frame, text="Balance: $0", 
                                      font=("Arial", 24, "bold"), 
                                      fg="#00ff00", bg="#16213e")
        self.balance_label.pack(pady=10)
        
        # Slot machine display
        self.slot_frame = tk.Frame(self.root, bg="#0f3460", relief=tk.SUNKEN, bd=5)
        self.slot_frame.pack(pady=20, padx=40)
        
        self.slot_labels = []
        for row in range(ROWS):
            row_labels = []
            row_frame = tk.Frame(self.slot_frame, bg="#0f3460")
            row_frame.pack(pady=5)
            
            for col in range(COLS):
                label = tk.Label(row_frame, text="?", 
                               font=("Arial", 48, "bold"),
                               width=3, height=1,
                               relief=tk.RAISED, bd=3,
                               bg="#e94560", fg="white")
                label.pack(side=tk.LEFT, padx=5)
                row_labels.append(label)
            self.slot_labels.append(row_labels)
        
        # Winning lines indicator
        self.winning_lines_label = tk.Label(self.root, text="", 
                                           font=("Arial", 16, "bold"),
                                           fg="#FFD700", bg="#1a1a2e")
        self.winning_lines_label.pack(pady=5)
        
        # Winnings display
        self.winnings_label = tk.Label(self.root, text="", 
                                      font=("Arial", 20, "bold"),
                                      fg="#00ff00", bg="#1a1a2e")
        self.winnings_label.pack(pady=5)
        
        # Control panel
        control_frame = tk.Frame(self.root, bg="#16213e", relief=tk.RAISED, bd=3)
        control_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Bet controls
        bet_frame = tk.Frame(control_frame, bg="#16213e")
        bet_frame.pack(pady=15)
        
        tk.Label(bet_frame, text="Bet per Line ($):", 
                font=("Arial", 14), fg="white", bg="#16213e").pack(side=tk.LEFT, padx=5)
        
        self.bet_var = tk.StringVar(value=str(MIN_BET))
        self.bet_entry = tk.Entry(bet_frame, textvariable=self.bet_var, 
                                 font=("Arial", 14), width=10)
        self.bet_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(bet_frame, text=f"(min ${MIN_BET})", 
                font=("Arial", 10), fg="#cccccc", bg="#16213e").pack(side=tk.LEFT, padx=5)
        
        # Lines controls
        lines_frame = tk.Frame(control_frame, bg="#16213e")
        lines_frame.pack(pady=15)
        
        tk.Label(lines_frame, text="Number of Lines:", 
                font=("Arial", 14), fg="white", bg="#16213e").pack(side=tk.LEFT, padx=5)
        
        self.lines_var = tk.IntVar(value=1)
        for i in range(1, MAX_LINES + 1):
            rb = tk.Radiobutton(lines_frame, text=str(i), variable=self.lines_var, 
                              value=i, font=("Arial", 12),
                              fg="white", bg="#16213e", selectcolor="#0f3460",
                              activebackground="#16213e", activeforeground="white")
            rb.pack(side=tk.LEFT, padx=5)
        
        # Total bet display
        self.total_bet_label = tk.Label(control_frame, text="Total Bet: $0", 
                                       font=("Arial", 16, "bold"),
                                       fg="#FFD700", bg="#16213e")
        self.total_bet_label.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg="#16213e")
        button_frame.pack(pady=20)
        
        self.spin_button = tk.Button(button_frame, text="🎰 SPIN 🎰", 
                                    font=("Arial", 18, "bold"),
                                    bg="#00ff00", fg="black",
                                    width=15, height=2,
                                    command=self.spin,
                                    state=tk.DISABLED)
        self.spin_button.pack(side=tk.LEFT, padx=10)
        
        self.quit_button = tk.Button(button_frame, text="Quit & Save", 
                                    font=("Arial", 14),
                                    bg="#ff4444", fg="white",
                                    width=12, height=2,
                                    command=self.quit_game)
        self.quit_button.pack(side=tk.LEFT, padx=10)
        
        # Bind entry changes to update total bet
        self.bet_var.trace('w', self.update_total_bet)
        self.lines_var.trace('w', self.update_total_bet)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Welcome! Please start a new game.", 
                                    font=("Arial", 12),
                                    fg="white", bg="#0f3460", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_startup_dialog(self):
        # Get participant info
        participant_id = simpledialog.askstring("Participant ID", 
                                               "Enter participant ID (or leave blank):",
                                               parent=self.root)
        if participant_id is None:
            participant_id = ""
        
        group_id = simpledialog.askstring("Group ID", 
                                         "Enter group/condition ID (or leave blank):",
                                         parent=self.root)
        if group_id is None:
            group_id = ""
        
        # Get initial deposit
        while True:
            deposit = simpledialog.askinteger("Deposit", 
                                             "What would you like to deposit? $",
                                             parent=self.root,
                                             minvalue=1)
            if deposit is None:
                self.root.quit()
                return
            if deposit > 0:
                break
        
        # Initialize game
        self.logger = SessionLogger(participant_id=participant_id, group_id=group_id)
        self.balance = deposit
        self.initial_deposit = deposit
        self.prev_balance = deposit
        self.prev_spin_time = self.logger.start_time
        self.game_started = True
        
        self.update_balance_display()
        self.spin_button.config(state=tk.NORMAL)
        self.status_label.config(text="Ready to play! Set your bet and spin!")
    
    def update_balance_display(self):
        self.balance_label.config(text=f"Balance: ${self.balance}")
    
    def update_total_bet(self, *args):
        try:
            bet = int(self.bet_var.get())
            lines = self.lines_var.get()
            total = bet * lines
            self.total_bet_label.config(text=f"Total Bet: ${total}")
        except ValueError:
            self.total_bet_label.config(text="Total Bet: $0")
    
    def validate_bet(self):
        try:
            bet = int(self.bet_var.get())
            if bet < MIN_BET:
                messagebox.showerror("Invalid Bet", 
                                   f"Bet must be at least ${MIN_BET}")
                return None
            return bet
        except ValueError:
            messagebox.showerror("Invalid Bet", "Please enter a valid number")
            return None
    
    def spin(self):
        if self.spinning or not self.game_started:
            return
        
        # Validate bet
        bet = self.validate_bet()
        if bet is None:
            return
        
        lines = self.lines_var.get()
        total_bet = bet * lines
        
        # Check balance
        if total_bet > self.balance:
            messagebox.showwarning("Insufficient Balance", 
                                  f"You do not have enough money to bet ${total_bet}.\n"
                                  f"Your current balance is ${self.balance}.")
            return
        
        self.spinning = True
        self.spin_button.config(state=tk.DISABLED, text="SPINNING...")
        self.status_label.config(text="Spinning...")
        
        # Run spin in a thread to allow animation
        thread = threading.Thread(target=self.perform_spin, args=(bet, lines, total_bet))
        thread.start()
    
    def perform_spin(self, bet, lines, total_bet):
        self.spin_count += 1
        curr_time = time.time()
        time_since_last = curr_time - self.prev_spin_time if self.spin_count > 1 else None
        
        # Animate spinning
        self.animate_spin()
        
        # Get actual result
        slots = get_slot_machine_spin(ROWS, COLS, symbol_count)
        winnings, winning_lines = check_winnings(slots, lines, bet, symbol_value)
        
        # Display result
        self.root.after(0, self.display_result, slots, winnings, winning_lines)
        
        # Update balance
        prev_prev_balance = self.prev_balance
        self.prev_balance = self.balance
        self.balance += winnings - total_bet
        
        # Calculate derived metrics
        bet_escalation = False
        if self.prev_bet is not None and bet > self.prev_bet:
            bet_escalation = True
        self.prev_bet = bet
        
        loss_chase = self.prev_was_loss and bet_escalation
        self.prev_was_loss = (winnings - total_bet) < 0
        
        is_all_in = total_bet == self.prev_balance
        
        after_big_win_flag = self.after_big_win
        # Big win threshold: >30% of initial deposit
        big_win_threshold = self.initial_deposit * 0.30
        if winnings > big_win_threshold:
            self.after_big_win = True
        else:
            self.after_big_win = False
        
        # Log spin
        self.logger.log_spin(
            spin_number=self.spin_count,
            timestamp=curr_time,
            bet=bet,
            lines=lines,
            total_bet=total_bet,
            winnings=winnings,
            winning_lines=winning_lines,
            balance=self.balance,
            bet_escalation=bet_escalation,
            loss_chase=loss_chase,
            time_since_last_spin=time_since_last,
            is_all_in=is_all_in,
            after_big_win=after_big_win_flag
        )
        self.prev_spin_time = curr_time
        
        # Update UI
        self.root.after(0, self.update_balance_display)
        self.root.after(0, self.finish_spin)
        
        # Check if game over
        if self.balance <= 0:
            self.root.after(0, self.game_over)
    
    def animate_spin(self):
        # Show random symbols during spin animation
        for _ in range(10):
            for row in range(ROWS):
                for col in range(COLS):
                    symbol = random.choice(list(symbol_count.keys()))
                    self.root.after(0, self.update_slot_label, row, col, symbol, "#e94560")
            time.sleep(0.1)
    
    def update_slot_label(self, row, col, symbol, color):
        self.slot_labels[row][col].config(text=symbol, bg=color)
    
    def display_result(self, slots, winnings, winning_lines):
        # Display final result with colors
        # slots is organized as columns, so slots[col][row] gives us the symbol
        # but we need to display it in slot_labels[row][col]
        for row in range(ROWS):
            for col in range(COLS):
                symbol = slots[col][row]
                color = SYMBOL_COLORS.get(symbol, "#e94560")
                self.slot_labels[row][col].config(text=symbol, bg=color)
        
        # Highlight winning lines
        if winning_lines:
            self.winning_lines_label.config(
                text=f"🎉 Winning Lines: {', '.join(map(str, winning_lines))} 🎉")
            self.winnings_label.config(text=f"You won ${winnings}!")
            
            # Flash winning lines
            for line_num in winning_lines:
                line_idx = line_num - 1
                for col in range(COLS):
                    self.slot_labels[line_idx][col].config(relief=tk.SUNKEN, bd=5)
        else:
            self.winning_lines_label.config(text="No winning lines")
            # Calculate the actual loss (total_bet - winnings)
            # Since we're here, winnings is 0, so loss equals bet * lines
            loss_amount = self.lines_var.get() * int(self.bet_var.get())
            self.winnings_label.config(text=f"You lost ${loss_amount}")
    
    def finish_spin(self):
        self.spinning = False
        if self.balance > 0:
            self.spin_button.config(state=tk.NORMAL, text="🎰 SPIN 🎰")
            self.status_label.config(text="Ready for next spin!")
        
        # Reset slot borders after a delay
        self.root.after(2000, self.reset_slot_borders)
    
    def reset_slot_borders(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.slot_labels[row][col].config(relief=tk.RAISED, bd=3)
    
    def game_over(self):
        messagebox.showinfo("Game Over", 
                          "You have run out of money!\n"
                          "Your session will be saved.")
        self.quit_game()
    
    def quit_game(self):
        if self.logger:
            session_end_time = time.time()
            self.logger.log_quit(self.balance, self.spin_count, session_end_time)
            self.logger.save()
            messagebox.showinfo("Session Saved", 
                              f"Your session has been saved!\n"
                              f"Final Balance: ${self.balance}\n"
                              f"Total Spins: {self.spin_count}\n"
                              f"Log file: {self.logger.path}")
        self.root.quit()


def main():
    root = tk.Tk()
    app = SlotMachineGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

