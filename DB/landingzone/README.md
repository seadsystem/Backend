#Go Landing Zone
The Go Landing Zone is a high speed, concurrent TCP server which listens for connections from SEAD plugs on port 9000. The plug requests its configuration from the server before beginning to send the buffered data it collects. This stream of packets is decoded, and the data is bulk inserted into the Postgres database in the background to be later queried by the API.

The service can be started using the init script installed via Puppet:
```sh
$ sudo service landingzone start
```

The landing zone is not intended to directly interacted with by a user. The data collected by the landing zone is accessible via the API. The correct way to test if the landing zone is functioning properly is to connect a SEAD plug and check if new data becomes available through the API.

Once we have the groundwork necessary to organize the protocol coordination between the SEAD panel and the landing zone, we will be able receive data from the SEAD panel and perform a classification of the raw data to determine the appliance type. This will complete our final user story:
>As a SEAD panel developer, I want to send raw appliance data to the server and a classification result to be rendered in the GUI.

##Installation

Installation of the Go Landing Zone and the Python API can be automated by using the Puppet modules included in the repository. The puppet modules are written for and assume to be executed on an Ubuntu 14.04 x64 Linux server. First you must install the prerequisites for running Puppet. From the terminal, execute:
```sh
$ sudo apt-get install puppet git
```
It is recommended that you also install fail2ban with the following command:
```sh
$ sudo apt-get install fail2ban
```

Copy the Puppet files onto the server (for example, by cloning the repository) and change to the DB directory.
```sh
$ cd DB/
```
If desired, configure the UNIX application user’s password in puppet/modules/config. First add the user credentials to manifests/credentials.pp, then uncomment the password definitions in config/manifests/init.pp.
```sh
$ cd puppet/config
$ nano manifests/credentials.pp
$ nano manifests/init.pp
$ cd ../..
```

Copy the files to the /etc/puppet directory, and execute Puppet:
```sh
$ sudo rsync -avc puppet/ /etc/puppet/
$ sudo puppet apply puppet/manifests/site.pp
```
After Puppet has executed the modules correctly, the server should be listening on ports 8080 and 9000. Verify with netstat:
```sh
$ netstat -tln | egrep ':(8080|9000)'
```
