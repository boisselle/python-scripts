#   This is a simple timer that displays a counter in ascending order. 
#   Specify timer duration in the format HH:MM:SS.
#   Set colors to flash on the command line with the ANSI escape codes below
#   Set sound_file to the absolute path of an m4a or mp3 file.
#   TODO: 
#   - test support for all sound file formats.
#   - allow counter to be descending or ascending via a variable

import time
import os
import threading
import subprocess
import select
import sys

# ANSI escape codes for background colors on command line.
# These colors flash alternately when the alarm sounds
# Uncomment as needed.

# BLACK_BG = "\033[40m"
RED_BG = "\033[41m"
# GREEN_BG = "\033[42m"
# YELLOW_BG = "\033[43m"
BLUE_BG = "\033[44m"
# MAGENTA_BG = "\033[45m"
# CYAN_BG = "\033[46m"
# WHITE_BG = "\033[47m"
# BRIGHT_BLACK_BG = "\033[100m"
# BRIGHT_RED_BG = "\033[101m"
# BRIGHT_GREEN_BG = "\033[102m"
# BRIGHT_YELLOW_BG = "\033[103m"
# BRIGHT_BLUE_BG = "\033[104m"
# BRIGHT_MAGENTA_BG = "\033[105m"
# BRIGHT_CYAN_BG = "\033[106m"
# BRIGHT_WHITE_BG = "\033[107m"
RESET = "\033[0m"

def clear_screen():
    os.system('clear')

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def play_alarm(sound_file):
    return subprocess.Popen(['afplay', sound_file])

def flash_terminal(stop_event):
    while not stop_event.is_set():
        print(BLUE_BG + " " * os.get_terminal_size().columns, end="\r", flush=True)
        time.sleep(0.2)
        print(RED_BG + " " * os.get_terminal_size().columns, end="\r", flush=True)
        time.sleep(0.2)
    print(RESET + " " * os.get_terminal_size().columns, end="\r", flush=True)

def check_for_keypress():
    return select.select([sys.stdin], [], [], 0.1)[0]

def run_timer(alarm_time, sound_file):
    seconds = 0
    try:
        while True:
            clear_screen()
            current_time = format_time(seconds)
            print(f"Timer: {current_time}")
            
            if current_time == alarm_time:
                print("Alarm! Press [Enter] to stop.")
                alarm_process = play_alarm(sound_file)
                stop_event = threading.Event()
                flash_thread = threading.Thread(target=flash_terminal, args=(stop_event,))
                flash_thread.start()
                
                try:
                    while alarm_process.poll() is None:
                        if check_for_keypress():
                            # Key pressed, stop the alarm
                            sys.stdin.readline()  # Clear the input buffer
                            break
                        time.sleep(0.1)
                finally:
                    alarm_process.terminate()
                    stop_event.set()
                    flash_thread.join()
                break
            
            time.sleep(1)
            seconds += 1
    except KeyboardInterrupt:
        print("\nTimer stopped.")
    finally:
        os.system("pkill afplay")  # Stop any playing alarms
        print(RESET, end="")  # Ensure terminal colors are reset

if __name__ == "__main__":
    sound_file = ""
    
    if not os.path.exists(sound_file):
        print(f"Error: Sound file not found at {sound_file}")
        exit()
    
    alarm_time = input("Enter the alarm time in HH:MM:SS format: ")
    run_timer(alarm_time, sound_file)
