# Install golang and libpq for the landingzone user
class go {
  # Install godeb and go
  $bin_url = 'https://godeb.s3.amazonaws.com/godeb-amd64.tar.gz'
  exec {'install-godeb':
    command => "curl ${bin_url} | tar zxf - > godeb",
    cwd     => '/usr/local/sbin',
    creates => '/usr/local/sbin/godeb',
  }

  exec {'godeb install':
    require => Exec['install-godeb'],
    cwd     => '/tmp',
    timeout => 600,
    unless  => 'which go',
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
    require => Exec['godeb install'],
  }

  # Install go sqlmock library
  exec {'go-sqlmock':
    command => 'env GOPATH=/home/landingzone/go go get -u github.com/DATA-DOG/go-sqlmock',
    require => Exec['godeb install'],
  }
}
