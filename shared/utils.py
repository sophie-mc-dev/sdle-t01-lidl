import sys
from os.path import dirname, abspath
import urllib.parse
import os


parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

db_dir = parent_dir + "/database"


# ----------------------------- Data -----------------------------

# Local storage:
#  - is a dictionary used for local storage of shopping lists, (simulated as an in-memory data structure)
client_list = {}

# Credentials
user_credentials = {}

# User lists
user_list = {}



# ----------------------------- Fetch data -----------------------------

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
            username, lists_IDs = line.strip().split(':')
            lists_IDs = line.strip().split(',')
            user_list[username] = lists_IDs
except FileNotFoundError:
    pass



# ----------------------------- Auxiliar functions -----------------------------

# extracts listID from server message
def extract_list_id(message):
    start_index = message.find("Your list id is '")

    if start_index != -1:
        end_index = message.find("'", start_index + len("Your list id is '"))

        if end_index != -1:
            list_id = message[start_index + len("Your list id is '"):end_index]
            return list_id
        else:
            print("Closing single quote not found.")
    else:
        print("Message format not recognized.")
    return None

# prints current client local list
# function only called by the client
def print_user_list(username):
    print("\n> Your List content:")
    for item in client_list[username].items:
        print(item.__str__())
    print("------------------------------\n")
    
