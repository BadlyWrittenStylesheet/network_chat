import subprocess
import time

# Path to the client script
path = r"C:\Users\Julian\PycharmProjects\local_chat\\"

# Start the server in a new terminal window
subprocess.Popen(['start', 'cmd', '/k', f'python {path}server.py'], shell=True)
instances = 2
# Give the server some time to start
time.sleep(2)

for _ in range(instances):

    # Start the client in a new terminal window with the specified path
    subprocess.Popen(['start', 'cmd', '/k', f'python {path}client.py'], shell=True)

