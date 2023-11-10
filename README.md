# feup-sdle

### Instructions to run the application: there are two ways to run the project. Please check them below.

## 1st way

1.1 - run server in sdle_t01_lidl directory:

    python -m sdle_t01_lidl.server.server

1.2 - run client in sdle_t01_lidl directory:

    python -m sdle_t01_lidl.client.client

### **IMP!** 
Before start running the application, you must <u>delete all the files from shopping_lists and clients_lists</u> as well as <u>clean the content of user_listsIDs.txt</u>. You can do that by running the following command on the project directory:

    make clean

<u>*NOTE*</u> - This was made to run on Windows prompt. If you're not using Windows, you **must delete this files by hand**.


## 2nd way  =>*(todo - rewrite this 4 Mac too!)*

If windows is your operation system, run the following commands from sdle_t01_lidl directory:

    ./run_server.bat
    ./run_client.bat
