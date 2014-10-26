# Configuration for the database server
class config {
  import 'unix_user'

  # Configure groups and users
  group {'db':
    ensure => present,
  }

  #  include "user"
  unix_user {['raymond', 'ian']:
    groups  => ['db', 'sudo'],
    require => Group['db'],
  }

  unix_user {['landingzone','seadapi']:
    groups  => 'db',
    require => Group['db'],
  }

  file {'/etc/init.d/seadapi':
    source  => 'puppet:///modules/config/init.seadapi',
    mode    => '0774',
    owner   => 'root',
    group   => 'root',
    require => User['seadapi'],
  }

  file {'/home/seadapi/api':
    ensure  => 'directory',
    owner   => 'seadapi',
    group   => 'seadapi',
    require => User['seadapi'],
  }

  service {'seadapi':
    ensure  => 'running',
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

  file {'/home/landingzone/landingzone':
    ensure  => 'directory',
    owner   => 'landingzone',
    group   => 'landingzone',
    require => User['landingzone'],
  }

  service {'landingzone':
    ensure  => 'running',
    enable  => true,
    require => File['/etc/init.d/landingzone'],
  }
}
