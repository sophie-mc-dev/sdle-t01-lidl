import sys
from os.path import dirname, abspath
import urllib.parse
import os


parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

db_dir = parent_dir + "/database"


# Data

# NOT USED ANYMORE
#  - is a dictionary used for local storage of shopping lists, (simulated as an in-memory data structure)
local_lists = {}

# NOT USED ANYMORE
# Cloud storage (simulated):
# - is a dictionary simulating cloud storage for shopping lists
cloud_storage = {}

# Local storage:
#  - is a dictionary used for local storage of shopping lists, (simulated as an in-memory data structure)
client_list = {}

# Credentials
user_credentials = {}

# User lists
user_list = {}


# Fetch data

try: # Credentials
    with open(db_dir + "/server_data/user_credentials.txt", 'r') as file:
        for line in file:
            username, password = line.strip().split(':')
            user_credentials[username] = password
except FileNotFoundError:
    pass


try: # User lists
    with open(db_dir + "/server_data/user_listsIDs.txt", 'r') as file:
        for line in file:
            username, listID = line.strip().split(':')
            user_list[username] = listID
except FileNotFoundError:
    pass


# Auxiliar functions

def create_file_from_url(url, folder_path, content):
    # Parse the URL to get the filename
    parsed_url = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed_url.path) + '.txt'

    # Join the folder_path and filename to create the full file path
    file_path = os.path.join(folder_path, filename)

    # Create a file
    try: 
        with open(file_path, 'w') as file:
            for line in content:
                file.write(line)
    except:
        with open(file_path, 'w') as file:
            pass


def is_file_empty(file_path):
    try:
        # Get the size of the file
        file_size = os.path.getsize(file_path)
        return file_size == 0
    except FileNotFoundError:
        # Handle the case where the file does not exist
        return False
    

def save_credentials_to_file(credentials):
    with open(db_dir + '/server_data/user_credentials.txt', 'w') as file:
        for username, password in credentials.items():
            file.write(f"{username}:{password}\n")

def register_user(username, password):
    if username in user_credentials:
        return "Username already exists. Please choose a different one."
    user_credentials[username] = password
    save_credentials_to_file(user_credentials)
    return "Registration successful. You can now log in."


def print_user_list():
    try:
        user_list = {}
        with open(db_dir + '/server_data/user_listsIDs.txt', 'r') as file:

            for line in file:
                username, listID = line.strip().split(':')
                user_list[username] = listID
    except FileNotFoundError:
        pass

    print("\n> User:ListID contents:")
    for username, list_id in user_list.items():
            print(f"{username}:{list_id}")

