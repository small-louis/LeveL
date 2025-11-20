import random
import time
import os
import csv
from datetime import datetime

MAX_LINES = 3
MIN_BET = 10
ROWS = 3
COLS = 3

symbol_count = { "A": 2, "B": 4, "C": 6, "D": 8 }
symbol_value = { "A": 5, "B": 4, "C": 3, "D": 2 }

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

def print_slot_machine_spin(columns):
    for row in range(len(columns[0])):
        for i, column in enumerate(columns):
            if i != len(columns) - 1:
                print(column[row], end=" | ")
            else:
                print(column[row], end="")
        print()

def deposit():
    while True:
        amount = input("What would you like to deposit? $")
        if amount.isdigit():
            amount = int(amount)
            if amount > 0:
                break
            else:
                print("Amount must be greater than 0.")
        else:
            print("Amount must be a number.")
    return amount

def get_number_of_lines():
    while True:
        lines = input(f"Enter number of lines to bet on (1-{MAX_LINES}): ")
        if lines.isdigit():
            lines = int(lines)
            if 1 <= lines <= MAX_LINES:
                break
            else:
                print(f"Number of lines must be between 1 and {MAX_LINES}.")
        else:
            print("Please enter a number.")
    return lines

def get_bet():
    while True:
        bet = input(f"How much would you like to bet on each line? (min ${MIN_BET}): ")
        if bet.isdigit():
            bet = int(bet)
            if bet >= MIN_BET:
                break
            else:
                print(f"Bet must be at least ${MIN_BET}.")
        else:
            print("Please enter a number.")
    return bet

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
            final_time - self.start_time  # session duration
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

def main():
    # Optionally ask for participant/group here:
    participant_id = input("Enter participant ID (or leave blank): ").strip()
    group_id = input("Enter group/condition ID (or leave blank): ").strip()
    logger = SessionLogger(participant_id=participant_id, group_id=group_id)
    balance = deposit()
    initial_deposit = balance
    spin_count = 0
    prev_bet = None
    prev_was_loss = False
    prev_balance = balance
    prev_spin_time = logger.start_time
    after_big_win = False

    while True:
        print(f"Current balance is ${balance}.")
        spin = input("Press enter to play (q to quit).")
        if spin == "q" or balance <= 0:
            session_end_time = time.time()
            logger.log_quit(balance, spin_count, session_end_time)
            break
        spin_count += 1

        curr_time = time.time()
        time_since_last = curr_time - prev_spin_time if spin_count > 1 else None
        bet = get_bet()
        lines = get_number_of_lines()
        total_bet = bet * lines
        if total_bet > balance:
            print(f"You do not have enough money to bet ${total_bet}. Your current balance is ${balance}.")
            continue

        slots = get_slot_machine_spin(ROWS, COLS, symbol_count)
        print_slot_machine_spin(slots)
        winnings, winning_lines = check_winnings(slots, lines, bet, symbol_value)
        print(f"You won ${winnings}.")
        print(f"You won on lines:", *winning_lines)
        prev_prev_balance = prev_balance
        prev_balance = balance
        balance += winnings - total_bet

        # Derived metrics
        bet_escalation = False
        if prev_bet is not None and bet > prev_bet:
            bet_escalation = True
        prev_bet = bet

        loss_chase = prev_was_loss and bet_escalation
        prev_was_loss = (winnings - total_bet) < 0

        # All-in detection
        is_all_in = total_bet == prev_balance

        # After big win
        after_big_win_flag = after_big_win
        # Big win threshold: >30% of initial deposit
        big_win_threshold = initial_deposit * 0.30
        if winnings > big_win_threshold:
            after_big_win = True
        else:
            after_big_win = False

        logger.log_spin(
            spin_number=spin_count,
            timestamp=curr_time,
            bet=bet,
            lines=lines,
            total_bet=total_bet,
            winnings=winnings,
            winning_lines=winning_lines,
            balance=balance,
            bet_escalation=bet_escalation,
            loss_chase=loss_chase,
            time_since_last_spin=time_since_last,
            is_all_in=is_all_in,
            after_big_win=after_big_win_flag
        )
        prev_spin_time = curr_time

    logger.save()

if __name__ == "__main__":
    main()
