WELCOME TO OUR APPLICATION --- SIMPLE FILE SHARING.

--------------------- When using the terminal --------------------

--Run the server
    1. Execute the file `main_server.py`.
    2. Choose a port for your server; for example, enter the port: `12000`.
    3. Ping a client (only if the client is online, connected, and logged in): `ping username number`.
        + Using `ping username`: The server will ping the client only once.
        + Using `ping username number`: The server will ping the client the specified number of times.
        + Replace username and number as needed.
    4. Discover a client's repository: `discover username` will display all files in the username's repository.
    5. Show: `show` will return all the usernames and their hashed passwords on the server.

--Run the client
    1. Execute the file `main_client.py`.
    2. Connect to the server: `connect IP Port` with the server's IP and Port, for example: `connect 172.16.1.61 12001`.
    3. Login/Register
        + If you already have an account on the server: `login that 123`.
        + Alternatively, you can create a new account: `register that 123`.
    4. Publish a local file to your repository: `publish lname fname`
        + lname: path to your local file on your computer.
        + fname: your file will be published as fname in your repository.
        + Example: `publish "D:\abc mnp\thai5.zip" that1.zip`.
    5. Search for a file: `search fname`.
    6. Fetch a file from another client and save it in your repository: `fetch fname rname`
        + `fetch fname`: The file will be saved as fname in your repository.
        + `fetch fname rname`: The file will be saved as rname in your repository.
        + Example: `fetch that5.zip that2.zip`.
        + Note: fetch will only succeed when the client owning the file `that5.zip` is online (connected to the server and logged in).
    7. View all files in your repository: `view`.
    8. Delete a file in your repository: `delete fname`.
    9. Change your password: `change_password old_password new_password`.
    10. Log out of your account: `logout`.
    11. Disconnect from the server: `disconnect`.
