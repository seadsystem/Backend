# Install golang and libpq for the landingzone user
class go {
  # Install go package
  package {'golang':
    ensure  => installed,
    require => User['landingzone'],
  }

  # Ensure go directory exists for landingzone user
  file {'gopath-dir':
    ensure  => directory,
    path    => '/home/landingzone/go',
    require => User['landingzone'],
  }

  # Install go pq library
  exec {'go-pq':
    command => 'env GOPATH=/home/landingzone/go go get github.com/lib/pq',
    require => Package['golang'],
  }

  # Install go influxdb library
  exec {'go-influxdb':
    command => 'env GOPATH=/home/landingzone/go go get github.com/influxdb/influxdb',
    require => Package['golang'],
  }
}
