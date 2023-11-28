# HOW TO RUN
### Server:
1. On the first terminal, run `python Asm1_CN/main_server.py`.
2. Enter port `12000`.
3. Test with following commands (after running at least one client):
    - List all files in `username`'s repo: `discover username`
    - Live check the client named `username`: `ping username`
    - List all registered hosts and their information: `host_info`

### Client:
1. On the second terminal, run `python Asm1_CN/main_client.py`.
2. Enter port `13000`.
3. Connect to the server using IP address and listening port, for example `connect 26.152.222.248 12001`.
4. Register / Log in (if registered), for example `register dat 123` / `login dat 123`.
5. Test with following commands (recently `lname` and `fname` isn't allowed to have space):
    - Publish local file at `lname` to the client's repo as `fname`: `publish lname fname`
    - Fetch a copy of the file named `fname` to the client's repo: `fetch fname`.
