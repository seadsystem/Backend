# Configuration for the database server
class config {
  import 'unix_user'
  import './credentials.pp'

  # Configure groups and users
  group {'db':
    ensure => present;
  'postgres':
    ensure => present;
  }

  # Administrators
  unix_user {['raymond', 'ian']:
    groups  => ['db', 'sudo'],
    require => Group['db'],
  }

  # Create application users
  unix_user {'landingzone':
    groups   => ['db', 'postgres'],
    #password => $config::landingzone_pw,
    require  => Group['db'],
  }
  unix_user {'seadapi':
    groups  => ['db', 'postgres'],
    #password => $config::seadapi_pw,
    require => Group['db'],
  }

  # Set up application directories
  file {'/home/seadapi/api':
    ensure  => directory,
    owner   => 'seadapi',
    group   => 'seadapi',
    require => User['seadapi'],
  }
  # landingzone directory set up in the go manifest.

  # Set up init scripts
  file {'/etc/init.d/seadapi':
    source  => 'puppet:///modules/config/init.seadapi',
    mode    => '0774',
    owner   => 'root',
    group   => 'root',
    require => User['seadapi'],
  }
  service {'seadapi':
    ensure  => running,
    enable  => true,
    require => File['/etc/init.d/seadapi'],
  }
  file {'/etc/init.d/landingzone':
    source  => 'puppet:///modules/config/init.landingzone',
    mode    => '0774',
    owner   => 'root',
    group   => 'root',
    require => User['landingzone'],
  }
  service {'landingzone':
    ensure  => running,
    enable  => true,
    require => File['/etc/init.d/landingzone'],
  }

  package {['python3-pip', 'libpq-dev', 'python3-scipy']:
    ensure => present,
    before => [ Exec['psycopg2'], Exec['sklearn'] ],
  }

  package {['python3-numpy', 'python3-matplotlib']:
    ensure => present,
  }

  exec {'psycopg2':
    command => 'pip3 install psycopg2',
  }

  exec {'sklearn':
    command => 'pip3 install sklearn',
  }
}
