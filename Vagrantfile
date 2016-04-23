# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

$install_docker = <<SCRIPT
    apt-get install apt-transport-https ca-certificates --yes
    apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
    echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" > /etc/apt/sources.list.d/docker.list
    apt-get update
    apt-get install linux-image-extra-$(uname -r) --yes
    apt-get install docker-engine --yes
    service docker start
    docker run hello-world
SCRIPT

$allow_vagrant_user_to_use_docker_without_sudo = <<SCRIPT
    usermod -aG docker vagrant
SCRIPT

$install_postgres = <<SCRIPT
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
    echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" > /etc/apt/sources.list.d/pgdg.list
    apt-get update
    apt-get install postgresql-9.5 --yes
    echo "listen_addresses = '*'" >> /etc/postgresql/9.5/main/postgresql.conf
    echo "host all all 0.0.0.0/0 trust" > /etc/postgresql/9.5/main/pg_hba.conf
    echo "local all all   trust" >> /etc/postgresql/9.5/main/pg_hba.conf
    pg_ctlcluster 9.5 main restart
SCRIPT

$install_project_requirements = <<SCRIPT
    echo "localhost:5432:dockerworkshop:dockerworkshop:dockerworkshop" > /home/vagrant/.pgpass
    su postgres -c "psql -p 5432 -h localhost template1 -f /home/vagrant/docker-workshop/create_db.sql"
    su postgres -c "psql -p 5432 -h localhost -U dockerworkshop dockerworkshop -f /home/vagrant/docker-workshop/create_schema_and_fixtures.sql"
    apt-get install python3-setuptools --yes
    easy_install3 pip
    pip install -r requirements.txt
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

 config.vm.define "docker-workshop"

 config.vm.box = "ubuntu/trusty64"
 config.vm.box_url = "https://atlas.hashicorp.com/ubuntu/boxes/trusty64/versions/20150516.0.0/providers/virtualbox.box"

 config.vm.network "private_network", ip: "192.168.33.10"
 config.vm.network :forwarded_port, guest: 80, host: 8080
 config.vm.hostname = "docker-workshop.dev"

 config.vm.synced_folder ".", "/vagrant", disabled: true
 config.vm.synced_folder ".", "/home/vagrant/docker-workshop", id: "vagrant-root", nfs: true

 config.vm.provider :virtualbox do |vb|
   vb.gui = false
   vb.customize ["modifyvm", :id, "--memory", "2048", "--cpus", "2"]
 end

 # http://foo-o-rama.com/vagrant--stdin-is-not-a-tty--fix.html
 config.vm.provision "fix-no-tty", type: "shell" do |s|
    s.privileged = false
    s.inline = "sudo sed -i '/tty/!s/mesg n/tty -s \\&\\& mesg n/' /root/.profile"
 end

 # automatically cd to project dir on login
 config.vm.provision :shell, inline: "echo 'cd /home/vagrant/docker-workshop' > /home/vagrant/.bashrc"

 # fix locale issue https://github.com/mitchellh/vagrant/issues/1188
 config.vm.provision :shell, :inline => <<-EOT
      echo 'LC_ALL="en_US.UTF-8"'  >  /etc/default/locale
EOT

 # install project
 config.vm.provision :shell, privileged:true, inline: $install_docker
 config.vm.provision :shell, privileged:true, inline: $allow_vagrant_user_to_use_docker_without_sudo
 config.vm.provision :shell, privileged:true, inline: $install_postgres
 config.vm.provision :shell, privileged:true, inline: $install_project_requirements

end
