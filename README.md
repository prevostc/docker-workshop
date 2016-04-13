# Docker workshop

We will learn how to use docker by typing some stuff on a terminal
  
# Pre-requisites

- Vagrant (1.7.4 at the time of writing)
- Virtualbox (5.0.16 at the time of writing)
   
# 0 - The db and the server

The vagrant comes with a PostgreSQL DB and a small python server

- vagrant ssh on 2 consoles 
- Start the server with `python3 server.py`
- Test the server with `curl -XGET http://localhost:8080`

OK, now let's put these inside containers.