# Docker workshop

We will learn how to use docker by typing some stuff on a terminal

# Pre-requisites

- Vagrant (1.7.4 at the time of writing)
- VirtualBox (5.0.16 at the time of writing)

# 0 - The db and the server

The vagrant comes with a PostgreSQL DB and a small python server

- vagrant ssh on 2 consoles
- Start the server with `python3 server.py`
- Test the server with `curl -XGET http://localhost:8080` and `curl -XPOST http://localhost:8080 -d "Hello world"`

OK, now let's put these inside containers.

# ½ - Why would I do that ?

Our application server works well, but the install procedure is quite long, you need python, PostgreSQL, some build tools, a database, and some scripts (@see Vagrantfile:$install_project_requirements)

Containers will allow us to start our app on any machine without any provisioning process.
The final container will be shipped with his dependencies and will be (near) totally isolated from any other program running alongside.

How is that possible ? https://www.docker.com/what-docker

IMPORTANT: A quick reminder if you don't remember what is an image and what is a container: http://stackoverflow.com/a/21499102/2523414

# 1 - Craft a custom web server image

Check that no container is already running with `docker ps`

EXERCISE: What will the following command do ? `docker build -t docker-workshop-web:1.0 .`

* Create a new container named `docker-workshop-web:1.0` with the current directory as main directory
* Download python 3 base image and create a new image based on our application requirements.txt
* An error, our application source code is missing
* Docker will ask a bunch of question to determine what type of image should be built  

# 2 - Run the web server as a container

You should see the image with `docker images` When building a custom image, the simplest way is to provide docker with a Dockerfile. A Dockerfile is basically a provisioning script, but you may also build your custom image using `docker commit` on a running container (more on that later).

Now that our image is carefully crafted with our web server dependencies inside (python3 and some custom pip packages), let's create a new instance of our web server but running inside a container.

EXERCISE: What will the following command do ? `docker run --rm --name=docker-workshop-web-1 docker-workshop-web:1.0 python server.py`

* An error, the `--rm` option does not exists
* Create a new container named `docker-workshop-web-1` running our python server
* Create a background container and echo the container ID, I will be able to fetch the container logs with `docker logs docker-workshop-web-1`
* An error, the server.py file does not exists

# 3 - Run the web server as a container (for real this time)

Using this command, you asked docker to create a new container named `docker-workshop-web-1` based on the image `docker-workshop-web:1.0`. `--rm` means that you want the container removed once the main process is stopped. And `python server.py` is the "entry point", it tells docker to run this command inside the container to keep it running.

The previous command failed to find our server.py because the Dockerfile didn't crafted our application code inside the container image. We can fix it at runtime with a volume mount:

`docker run --rm -it --name=docker-workshop-web-1 -v "$PWD"/server.py:/home/server.py -p 8080:8080 -e POSTGRES_PORT_5432_TCP_ADDR=192.168.33.10 docker-workshop-web:1.0 python /home/server.py`

Ouch, that's a lot of of options but it's all about explicitly specifying everything our program needs to execute and his external dependencies.
* The server.py file got mounted on the container with the `-v` options
* We told the server where he should find PostgreSQL running using a custom environment variable
* `-p` is a simple port mapping option, in this case, the container outside `8080` maps to the `8080` port
* `-it` binds the container in a way that simulates a TTY, I won't go into details here (because I can't :p)

Don't worry though, with `docker-compose` you can write down all these options in a .yml file so you don't have to type a command line that long every time you want to start a container (more on that later).

To check that the container is properly running, open another terminal and do `docker ps` or `docker info`. You should be able to `curl -XGET http://localhost:8080`. You may also request the docker engine some more infos about the running container with `docker top docker-workshop-web-1`, `docker stats docker-workshop-web-1`, `docker logs docker-workshop-web-1` or the full package with `docker inspect docker-workshop-web-1`

At this point, you should also experiment with the various `docker run` options.

Further Experiments:
* Start a shell inside the running container with `docker exec -it docker-workshop-web-1 bash` and compare inside and outside basic command outputs like `ps auxf` (tree view) or `htop`
* Uninstall python PostgreSQL package with `sudo pip uninstall py-postgresql` and check your container health
* Don't forget to take a look at the Dockerfile

# 3 - Run the database as a container

Now stop the local PostgreSQL instance just to make sure (`sudo service postgresql stop`) and start a new PostgreSQL instance with `docker run -d --name docker-workshop-db-1 postgres:9.5`

You should see additional PostgreSQL images with `docker images`.

We can see that the new container is running at 172.17.0.2 with `docker inspect --format '{{ .NetworkSettings.IPAddress }}' docker-workshop-db-1`

Setup the database with the following:
* `docker run -it --rm -v "$PWD"/:/home/ postgres:9.5 sh -c 'exec psql -h 172.17.0.2 -p 5432 -U postgres -f /home/create_db.sql postgres'`
* `docker run -it --rm -v "$PWD"/:/home/ postgres:9.5 sh -c 'exec psql -h 172.17.0.2 -p 5432 -U dockerworkshop -f /home/create_schema_and_fixtures.sql dockerworkshop'`

Now restart the web server with `docker run --rm -it --name=docker-workshop-web-1 -v "$PWD"/server.py:/home/server.py -p 8080:8080 -e POSTGRES_PORT_5432_TCP_ADDR=172.17.0.2 docker-workshop-web:1.0 python /home/server.py`

Everything should be as before with both `curl -XGET http://localhost:8080` and `curl -XPOST http://localhost:8080 -d "Hello world"`

EXERCISE: What would happen we `docker restart docker-workshop-db-1` ?

* Nothing bad, the database will restart and no data will be lost
* The database won't stop as the web server is holding an active connexion to it
* The container will restart and my data will be lost
* The database will restart with another ip and the web server will display an error

EXERCISE: What if we `docker stop docker-workshop-db-1`, `docker rm docker-workshop-db-1` and restart the database container ?

* Nothing bad, the database will restart and no data will be lost
* The database won't stop as the web server is holding an active connexion to it
* The container will restart and my data and schema will be lost
* The database will restart with another ip and the web server will display an error

# 4 - Commit



# 4 - Playing with networks

* Create a new network named `docker-workshop`
* Guess what this command will do: `docker run -d --name docker-workshop-db-1 --net=docker-workshop postgres:9.5`

# 2 - Run the database as a container

Exercise: git checkout exercise-1
Answer: git checkout exercise-1-answer

# X - Get rid of Vagrant

* Install docker on your system a
