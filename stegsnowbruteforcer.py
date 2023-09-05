import argparse, subprocess, re, queue, threading 
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor


# ANSI color codes
RED = '\033[91m'
BLUE = '\033[94m'
ENDC = '\033[0m'
GREEN = '\033[92m'

signature = """
***********************************************************
*                                                         *
*         Stegsnow Password Brute-Force Attack            *
*                    made by Assa228                      *
*     https://github.com/Assa228/StegsnowBruteForcer      *
*                                                         *
***********************************************************
"""

print(signature)

def try_password(file_path, password, output_file, keyword=None):
    command = f'stegsnow -C -Q -p "{password}" {file_path}'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='latin-1')

    if keyword and re.search(keyword, result.stdout):
        with open(output_file, 'a') as out_file:
            out_file.write(f'Message extracted with password: {password}\n')
            out_file.write(result.stdout + '\n')
        print(BLUE + f"\nKeyword " + GREEN + f"'{keyword}'" + BLUE + f" found with the password: " + RED + f"{password}" + ENDC)
        print(BLUE + "Here is the decoded message:")
        lines = result.stdout.split('\n')
        for line in lines:
            if keyword in line:
                print(RED + line + ENDC)

    elif result.returncode == 0:
        with open(output_file, 'a') as out_file:
            out_file.write(f'Message extracted with password: {password}\n')
            out_file.write(result.stdout + '\n')
    else:
        with open(output_file, 'a') as out_file:
            out_file.write(f"Attempt with password '{password}' failed.\n")

    # Update the progress bar when the task is completed
    pbar.update(1)

# Define a function to process passwords from the queue
def process_passwords(file_path, output_file, keyword=None):
    while True:
        try:
            password = password_queue.get(timeout=1)  # Wait for a password, timeout to check if we should exit
        except queue.Empty:
            break  # No more passwords, exit the thread
        try_password(file_path, password, output_file, keyword)
        password_queue.task_done()

parser = argparse.ArgumentParser(description='Brute-Force Attack Script for Stegsnow')
parser.add_argument('--file', required=True, help='Path to the target file')
parser.add_argument('--wordlist', required=True, help='Path to the password file')
parser.add_argument('--output', required=True, help='Path to the output results file')
parser.add_argument('--keyword', help='Keyword to search in the results')
parser.add_argument('--threads', type=int, default=2, help='Number of threads (default: 2)')
args = parser.parse_args()

file_path = args.file
password_file = args.wordlist
output_file = args.output
keyword = args.keyword

# Load the list of passwords from the wordlist file
with open(password_file, 'rb') as f:
    lines = f.readlines()

num_threads = args.threads  # Use the value specified by the user or the default value (2)
total_passwords = len(lines)
start_index = int(0.00 * total_passwords)  # progress percentage

# Using the tqdm library to display real progress
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    with tqdm(total=total_passwords - start_index, ncols=80) as pbar:
        # Create a queue for passwords
        password_queue = queue.Queue()
        for line in lines[start_index:]:
            try:
                password = line.decode('latin-1').strip()
            except UnicodeDecodeError:
                continue
            password_queue.put(password)

        # Start worker threads
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=process_passwords, args=(file_path, output_file, keyword))
            thread.start()
            threads.append(thread)

        # Wait for all worker threads to finish
        for thread in threads:
            thread.join()

print("\nBrute-force attack completed. The results have been saved in", output_file)
