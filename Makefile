clean_file:
	type NUL > database\server_data\active_lists_file.txt

clean_folders:
	del database\server_data\shopping_lists\* /Q
	del database\client_data\shopping_lists\* /Q

clean: clean_file clean_folders