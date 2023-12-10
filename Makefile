clean_active_lists_file:
	type NUL > database\server_data\active_lists_file.txt

delete_server_lists:
	del database\server_data\shopping_lists\* /Q

delete_clients_folders:
	rd /s /q database\client_data
	mkdir database\client_data

clean: clean_active_lists_file delete_server_lists delete_clients_folders