# Install golang and libraries for the landingzone user
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

  # Install go grpc library
  exec {'go-grpc':
    command => 'env GOPATH=/home/landingzone/go go get -u google.golang.org/grpc',
    require => Exec['godeb install'],
  }

  # Install go protobuf library
  exec {'go-protobuf':
    command => 'env GOPATH=/home/landingzone/go go get -u github.com/golang/protobuf/proto',
    require => Exec['godeb install'],
  }

  # Install go context library
  exec {'go-context':
    command => 'env GOPATH=/home/landingzone/go go get -u golang.org/x/net/context',
    require => Exec['godeb install'],
  }
}
