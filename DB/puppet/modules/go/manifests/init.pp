# Install golang and libpq for the landingzone user
class go {
  # Install go package
  package {'golang':
    ensure => installed,
  }

  # Ensure go directory exists for landingzone user
  file {'gopath-dir':
    ensure  => directory,
    path    => '/home/landingzone/go',
    owner   => 'landingzone',
    group   => 'db',
    recurse => true,
    require => User['landingzone'],
  }

  # Install go pq bulk library
  exec {'go-pq':
      command => 'env GOPATH=/home/landingzone/go go get github.com/olt/libpq',
      require => Package['golang']
  }

  # Set permissions on go module directories
  file {['/home/landingzone/go/src',
  '/home/landingzone/go/pkg']:
    ensure  => directory,
    owner   => 'landingzone',
    group   => 'db',
    require => Exec['go-pq'],
    recurse => true,
  }
}
