# This Makefile is running before starting the server by the command:
# ./run_server.bat

clean_file:
	type NUL > database\server_data\user_listsIDs.txt

clean_folders:
	del database\server_data\shopping_lists\* /Q
	del database\client_data\clients_lists\* /Q

clean: clean_file clean_folders
