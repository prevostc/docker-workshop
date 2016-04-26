# Docker workshop

We will learn how to use docker by typing some stuff on a terminal.

This step by step tutorial is designed for anyone that already know a little bit of theory about docker but need more practice to really get a grasp on it.

If you feel that you need a more detailed tutorial to get started, Docker inc. built his own, more in-depth, tutorial for beginners: https://github.com/docker/docker-birthday-3/blob/master/tutorial.md

IMPORTANT NOTES:
* Some steps ends with an EXERCISE. It is important that you try to answer the question before running any command, your first answers will be mostly guesses but you should get better and better with time :)
* Raw docker forces us to type command with a lot of options, please take time to go through each of theses options as it is important that you understand most of them

Author notes:
* I hope you will learn and enjoy going through this tutorial as much as I learned and enjoyed writing it and I also hope the step by step approach will demystify the docker black box.
* If I missed something important or made a mistake, please create an issue or a PR to improve this tutorial.
* Please note that english is not my native language and while I'm confident that this tutorial makes sense, I don't know how it sounds to a native speaker. Any comment or advice is welcome.

# Pre-requisites

- Vagrant (1.7.4 at the time of writing)
- VirtualBox (5.0.16 at the time of writing)

# 0 - The db and the server

The provided vagrant comes with a PostgreSQL DB and a small python server

1. Start the virtual machine with `vagrant up` (this might take some time, continue your reading in the meantime)
2. `vagrant ssh` is used to login to the vm
3. Inside vagrant, start the server with `python3 server.py` to start our simple server
4. On another terminal, still inside vagrant `curl -XGET http://localhost:8080` and `curl -XPOST http://localhost:8080 -d "Hello world"` to play with the included web server

OK, now let's put these inside containers.

# ½ - Why would I do that ?

Our application server works well, but the install procedure is quite long, we need python, PostgreSQL, some build tools, a database, and some scripts (@see Vagrantfile:$install_project_requirements)

Containers will allow us to start our app on any machine without any prior provisioning process.
The final container will be shipped with his dependencies and will be (near) totally isolated from any other program running alongside.

How is that possible ? Docker is no black magic, under the hood a process running "in a container" is just a regular process running on your host machine.

I have to trust linux kernel specialists on this but here are some interesting quotes:

> There are six namespaces in Linux (mnt, ipc, net, usr etc.). Using these namespaces a container can have its own network interfaces, ip address etc. Each container will have its own namespace and the processes running inside that namespace will not have any privileges outside its namespace. [devopscube.com](http://devopscube.com/what-is-docker/)

> Linux Containers and LXC, a user-space control package for Linux Containers, constitute the core of Docker. LXC uses kernel-level namespaces to isolate the container from the host. The user namespace separates the container's and the host's user database, thus ensuring that the container's root user does not have root privileges on the host. The process namespace is responsible for displaying and managing only processes running in the container, not the host. And, the network namespace provides the container with its own network device and virtual IP address. [linuxjournal.com](http://www.linuxjournal.com/content/docker-lightweight-linux-containers-consistent-development-and-deployment)

> Another component of Docker provided by LXC are Control Groups (cgroups). While namespaces are responsible for isolation between host and container, control groups implement resource accounting and limiting. While allowing Docker to limit the resources being consumed by a container, such as memory, disk space and I/O, cgroups also output lots of metrics about these resources. These metrics allow Docker to monitor the resource consumption of the various processes within the containers and make sure that each gets only its fair share of the available resources. [linuxjournal.com](http://www.linuxjournal.com/content/docker-lightweight-linux-containers-consistent-development-and-deployment)

> In addition to the above components, Docker has been using AuFS (Advanced Multi-Layered Unification Filesystem) as a filesystem for containers. AuFS is a layered filesystem that can transparently overlay one or more existing filesystems. When a process needs to modify a file, AuFS creates a copy of that file. AuFS is capable of merging multiple layers into a single representation of a filesystem. This process is called copy-on-write. [linuxjournal.com](http://www.linuxjournal.com/content/docker-lightweight-linux-containers-consistent-development-and-deployment)

In short: just regular linux processes with a lot of resource namespaces, but no magic involved.

Now that we know we're in know linux land, let's see how docker leverage these technologies.

Note, that the previous quotes are from docker 0.7, since then docker started the open container project and uses [RunC](https://runc.io/) and [ContainerD](https://containerd.tools/) internally.

> RunC is a lightweight, portable container runtime. It includes all of the plumbing code used by Docker to interact with system features related to containers [blog.docker.com](https://blog.docker.com/2015/06/runc/)

# 1 - Craft a custom web server image

As the first step, we are going to put our web server in a container. The first step is to build a custom container image. This image will contain everything we need to run server.py (python3 and the dependencies listed in requirements.txt).

Please check that your docker install is ok with `docker run hello-world`

Check that no container is already running with `docker ps` and check the available images with `docker images`.

Based on what you know, you should already be able to solve the first exercise :)

EXERCISE: What will the following command do ? `docker build -t docker-workshop-web:1.0 .`

1. Create a new container named `docker-workshop-web:1.0` with the current directory as main directory
2. Download python 3 base image and create a new image based on our application requirements.txt
3. An error, our application source code is missing
4. Docker will ask a bunch of question to determine what type of image should be built  

# 2 - Run the web server as a container

We should see the image with `docker images` When building a custom image, the simplest way is to provide docker with a Dockerfile. A Dockerfile is a build script, but we may also build our custom image using `docker commit` on a running container (more on that later).

Now that our image is carefully crafted with our web server dependencies inside (python3 and some custom pip packages), let's create a new instance of our web server but running inside a container.

EXERCISE: What will the following command do ? `docker run --rm --name=docker-workshop-web-1 docker-workshop-web:1.0 python server.py`

1. An error, the `--rm` option does not exists
2. Create a new container named `docker-workshop-web-1` running our python server
3. Create a background container and echo the container ID, but the database is unreachable
4. An error, the server.py file does not exists

# 3 - Run the web server as a container (for real this time)

Using this command, we asked docker to create a new container named `docker-workshop-web-1` based on the image `docker-workshop-web:1.0`. `--rm` means that we want the container removed once the main process is stopped. And `python server.py` is the "entry point", it tells docker to run this command inside the container to keep it running.

The previous command failed to find our server.py because the Dockerfile didn't crafted our application code inside the container image. We can fix it at runtime with a volume mount:

`docker run --rm -it --name=docker-workshop-web-1 -v "$PWD"/server.py:/home/server.py -p 8080:8080 -e POSTGRES_PORT_5432_TCP_ADDR=192.168.33.10 docker-workshop-web:1.0 python /home/server.py`

Ouch, that's a lot of of options but it's all about being explicit about everything our program needs to execute:
* The server.py file got mounted on the container with the `-v` options
* We told the server where he should find PostgreSQL running with a custom environment variable
* `-p` is used to publish ports, in this case, the container `8080` is published as the `8080` port
* `-it` binds the container in a way that simulates a TTY, I won't go into details here (because I can't :p)

Don't worry though, with `docker-compose` we can write down all these options in a .yml file so we don't have to type a command line that long every time we want to start a container (more on that later).

To check that the container is properly running, open another terminal and do `docker ps` or `docker info`. We should be able to `curl -XGET http://localhost:8080`. We may also request the docker engine some more infos about the running container with `docker top docker-workshop-web-1`, `docker stats docker-workshop-web-1`, `docker logs docker-workshop-web-1` or the full package with `docker inspect docker-workshop-web-1`

At this point, you should also experiment with the various `docker run` options.

Further Experiments:
* Start a shell inside the running container with `docker exec -it docker-workshop-web-1 bash` and compare inside and outside basic command outputs like `ps auxf` (tree view) or `htop`
* Uninstall python PostgreSQL package with `sudo pip uninstall py-postgresql` and check your container health
* Don't forget to take a look at the Dockerfile

# 3 - Run the database as a container

Now stop the local PostgreSQL instance just to make sure (`sudo service postgresql stop`) and start a new PostgreSQL instance with `docker run -d -e PGDATA=/pg_data --name docker-workshop-db-1 postgres:9.5`

We should see additional PostgreSQL images with `docker images`.

We can see that the new container is running at 172.17.0.2 with `docker inspect --format '{{ .NetworkSettings.IPAddress }}' docker-workshop-db-1`

Setup the database with the following:
1. Create the database with `docker run -it --rm -v "$PWD"/:/home/ postgres:9.5 sh -c 'exec psql -h 172.17.0.2 -p 5432 -U postgres -f /home/create_db.sql postgres'`
2. Create the schema with `docker run -it --rm -v "$PWD"/:/home/ postgres:9.5 sh -c 'exec psql -h 172.17.0.2 -p 5432 -U dockerworkshop -f /home/create_schema_and_fixtures.sql dockerworkshop'`

Now restart the web server with `docker run --rm -it --name=docker-workshop-web-1 -v "$PWD"/server.py:/home/server.py -p 8080:8080 -e POSTGRES_PORT_5432_TCP_ADDR=172.17.0.2 docker-workshop-web:1.0 python /home/server.py`

Everything should be as before with both `curl -XGET http://localhost:8080` and `curl -XPOST http://localhost:8080 -d "Hello world"`

EXERCISE: What would happen we `docker restart docker-workshop-db-1` ?

1. Nothing bad, the database will restart and no data will be lost
2. The database won't stop as the web server is holding an active connexion to it
3. The container will restart and my data will be lost
4. The database will restart with another ip and the web server will display an error

EXERCISE: What if we `docker stop docker-workshop-db-1`, `docker rm docker-workshop-db-1` and restart the database container ?

1. Nothing bad, the database will restart and no data will be lost
2. The database won't stop as the web server is holding an active connexion to it
3. The container will restart and my data and schema will be lost
4. The database will restart with another ip and the web server will display an error

EXERCISE: Can you come up with a way to start the database container that avoid this behavior ?

# 4 - Commit & Data management

To avoid loosing our data every time the container gets stopped and removed, we can play with the `-v` option to map the PostgreSQL data directory on our host system (be careful not to mount a directory from ~/docker-workshop as VirtualBox will forbid PostgreSQL to change the directory ownership): `run -d --name docker-workshop-db-1 -e PGDATA=/pg_data -v /pg_data:/pg_data postgres:9.5`

Please note that while this works well on a development environment, this is not the recommended way to manage data volumes. Docker support volume plugins that abstract the data management away. You should check out the [List of built in plugins](https://github.com/docker/docker/blob/master/docs/extend/plugins.md), especially the well-known Flocker and Convoy plugins.

At any time, we can also create a new image based on the state of a container.
Make sure the database is stopped and run the following commands:
1. Start the database container with `docker run -d -e PGDATA=/pg_data --name docker-workshop-db-1 postgres:9.5` (this is important because of [this](http://stackoverflow.com/a/27378619/2523414)).
2. Re-create the database with `docker run -it --rm -v "$PWD"/:/home/ postgres:9.5 sh -c 'exec psql -h 172.17.0.2 -p 5432 -U postgres -f /home/create_db.sql postgres'`
3. Re-create the schema with `docker run -it --rm -v "$PWD"/:/home/ postgres:9.5 sh -c 'exec psql -h 172.17.0.2 -p 5432 -U dockerworkshop -f /home/create_schema_and_fixtures.sql dockerworkshop'`
4. Insert some custom data with the web server `curl -XPOST http://localhost:8080 -d 'Such payload, much content!'`

Now that everything is in good shape, we can commit the container state with `docker commit docker-workshop-db-1 docker-workshop-db:1.0`. Now checkout the image list `docker images` and stop the database container `docker stop docker-workshop-db-1 && docker rm docker-workshop-db-1`.

We should be able to restart the database from our previous state with `docker run -d --name docker-workshop-db-1 docker-workshop-db:1.0`

# 5 - Container management systems

Tired of typing long commands ? I prepared docker-compose file. Now all you have to do to start everything is `docker-compose up`.
Now that you know the docker basics, you can dig into the [docker-compose documentation](https://docs.docker.com/compose/compose-file/) on your own without too much trouble.

# 6 - Conclusion

We went from a raw python web app and a PostgreSQL database and some simple provisioning scripts to a fully packaged application with ultra-standard boundaries in term of volumes, network and metrics inspection. In the process we learned a little bit more about the various docker commands and internals. In the end, we are now better aware of the docker capabilities and limitations and we can thoughtfully add it to our toolbox.

But the docker journey doesn't end yet! Standard application boundaries means we can automate a LOT of things. Here are some further Experiments:
* Get rid of Vagrant: Install docker on your system and transfer the database image to your new docker instance
* Learn more about `docker network`
* Learn more about docker volumes and volume plugins
* Put a load balancer in front of the web app and start many web containers using docker-compose scale
* Play with docker swarm
* Explore docker hub and create a Wordpress or a Prestashop container with one command only! :)
* Check out ultra-specialized micro-containers from iron.io
