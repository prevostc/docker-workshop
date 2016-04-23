# Docker workshop

We will learn how to use docker by typing some stuff on a terminal

# Pre-requisites

- Vagrant (1.7.4 at the time of writing)
- VirtualBox (5.0.16 at the time of writing)

# 0 - The db and the server

The vagrant comes with a PostgreSQL DB and a small python server

- vagrant ssh on 2 consoles
- Start the server with `python3 server.py`
- Test the server with `curl -XGET http://localhost:8080`

OK, now let's put these inside containers.

# ½ - Why would I do that ?

Our application server works well, but the install procedure is quite long, you need python, PostgreSQL, some build tools, a database, and some scripts (@see Vagrantfile:$install_project_requirements)

Containers will allow us to start our app on any machine without any provisioning process.
The final container will be shipped with his dependencies and will be (near) totally isolated from any other program running alongside.

How is that possible ? https://www.docker.com/what-docker

IMPORTANT: A quick reminder if you don't remember what is an image and what is a container: http://stackoverflow.com/a/21499102/2523414

# 1 - Craft a custom web server image

Check that no container is already running with `docker ps`

What will the following command do ? `docker build -t docker-workshop-web:1.0 .`

* Create a new container named `docker-workshop-web:1.0` with the current directory as main directory
* Download python 3 base image and create a new image based on our application requirements.txt
* An error, our application source code is missing
* Docker will ask a bunch of question to determine what type of image should be built  

# 2 - Run the web server as a container

You should see the image with `docker images` When building a custom image, the simplest way is to provide docker with a Dockerfile. A Dockerfile is basically a provisioning script, but you may also build your custom image using `docker commit` on a running container (more on that later).

Now that our image is carefully crafted with our web server dependencies inside (python3 and some custom pip packages), let's create a new instance of our web server but running inside a container.

What will the following command do ? `docker run --rm --name=docker-workshop-web-1 docker-workshop-web:1.0 python server.py`

* An error, the `--rm` option does not exists
* Create a new container named `docker-workshop-web-1` running our python server
* Create a background container and echo the container ID, I will be able to fetch the container logs with `docker logs docker-workshop-web-1`
* An error, the server.py file does not exists

# 3 - Run the web server as a container (for real this time)

Using this command, you asked docker to create a new container named `docker-workshop-web-1` based on the image `docker-workshop-web:1.0`. `--rm` means that you want the container removed once the main process is stopped. And `python server.py` is the "entry point", it tells docker to run this command inside the container to keep it running.

The previous command failed to find our server.py because the Dockerfile didn't crafted our application code inside the container image. We can fix it at runtime with a volume mount:

`docker run --rm -it --name=docker-workshop-web-1 -v "$PWD"/server.py:/home/server.py -p 8080:8080 -e POSTGRES_PORT_5432_TCP_ADDR=192.168.33.10 docker-workshop-web:1.0 python /home/server.py`

Ouch, that's a lot of of options but it's all about explicitly specifying every dependencies
* The server.py file got mounted on the container with the `-v` options
* We told the server where he should find PostgreSQL running using a custom environment variable
* `-p` is a simple port mapping option, in this case, the container outside `8080` maps to the `8080` port
* `-it` binds the container in a way that simulates a TTY, I won't go into details here (because I can't :p)

To check that the container is properly running, open another terminal and do `docker ps`.


At this point, you should experiment with the various `docker run` options.


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

* Stop the local PostgreSQL instance, just to make sure (`sudo service postgresql stop`)
* Create a new network named `docker-workshop`
* Guess what this command will do: `docker run -d --name docker-workshop-db-1 --net=docker-workshop postgres:latest`
* Check your available images. What do you see ? Why ?
* Check your running containers.
* Start the application server and link it to the database container
      `docker run -it --rm --name docker-workshop-web -v "$PWD"/server.py:/home/server.py -w /home -p 80:80 b8a7a6b4ceee python server.py`

Answers: `git checkout exercise-1-answer`

# 2 - Run the database as a container

Exercise: git checkout exercise-1
Answer: git checkout exercise-1-answer

# X - Get rid of Vagrant

* Install docker on your system a
