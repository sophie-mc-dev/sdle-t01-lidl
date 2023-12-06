# This Makefile is running before starting the server by the command:
# ./run_server.bat

clean_file:
	type NUL > database\server_data\active_lists_file.txt

clean: clean_file
