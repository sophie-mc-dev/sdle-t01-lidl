clean_file:
	type NUL > database\active_lists_file.txt

clean_folder:
	del database\shopping_lists\* /Q

clean: clean_file clean_folder