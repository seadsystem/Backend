DB
==

Database Team's repo

## Contents ##
 * Deliverables: Scrum project management documentation
 * api: Python API database interaction
 * puppet: Puppet modules for server configuration
   after server configuration
 * landingzone: Go server to listen for connections to
   store sensor data
 * _Vagrantfile_: Vagrant configuration for development
   environment
 * _deploy.sh_: Deployment shell script to be executed

## Using the Vagrant Environment ##
 * Vagrant uses the VirtualBox provider by default, so
   you will first need to install VirtualBox or find
   a suitable Vagrant extension for your virtualization
   platform
 * Download and install Vagrant from
   https://www.vagrantup.com/downloads.html
 * From this directory, execute `vagrant up` to create
   the virtual machine, which will be provisioned
   after boot
 * See the Vagrant docs for more information on using the
   cli: https://docs.vagrantup.com/v2/cli/index.html
