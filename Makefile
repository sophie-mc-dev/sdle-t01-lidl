# This Makefile is running before starting the server by the command:
# ./run_server.bat

clean_file:
	type NUL > database\server_data\user_listsIDs.txt


clean: clean_file
