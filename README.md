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

# ½ - Why whould I do that ?

Our application server works well, but the install procedure is quite long, you need python, postgres, 
some build tools, a database, and some scripts (@see Vagrantfile:$install_project_requirements)

Containers will allow us to start our app on any machine without any provisioning process. The final container will
 be shipped with his dependencies and will be (near) totally isolated from any other program running alongside.

How is that possible ? https://www.docker.com/what-docker

IMPORTANT: A quick reminder if you don't remember what is an image and what is a container: http://stackoverflow.com/a/21499102/2523414

# 1 - Run the web server as a container

* Check that no container is already running with `docker ps -a` 
* Use the provided Dockerfile to build a docker image named "workshop-app" with `docker build`
* You should see the image with `docker images`
* Create a new container based on this image with `docker run` (also try background mode), check with `docker ps`
* Inspect the running container with `docker top` and `docker stats`
* Find out the ip of the container image with `docker inspect --format '{{ .NetworkSettings.IPAddress }}'`
* Send HTTP requests to this container and observe the logs with `docker logs`. 
* What are you seeing ? Why ? What should we do about it ?

Experiments:
* Start a shell inside the running container and compare inside and outside basic command outputs like `ls`, `ps` or `top`   
* Uninstall python with `sudo apt-get purge python3` and check your container health
* Don't forget to take a look at the Dockerfile 

Answers: `git checkout exercise-1-answer`

# 2 - Run the database as a container

Get a fresh start with `git checkout exercise-1-answer`

* Create a postgres container using the postgres image from docker hub: https://hub.docker.com/_/postgres/
* Check your available images
* Check your running containers
* 

Answers: `git checkout exercise-1-answer`

# 2 - Run the database as a container

Exercise: git checkout exercise-1
Answer: git checkout exercise-1-answer
