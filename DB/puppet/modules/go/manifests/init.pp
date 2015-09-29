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
    command => 'env GOPATH=/home/landingzone/go go get -u github.com/lib/pq',
    require => Package['golang'],
  }

  # Install go sqlmock library
  exec {'go-sqlmock':
    command => 'env GOPATH=/home/landingzone/go go get -u github.com/DATA-DOG/go-sqlmock',
    require => Package['golang'],
  }
}
