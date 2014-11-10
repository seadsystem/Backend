class deploy {
  import 'db_user'

  # Postgres table data_raw
  $data_raw_schema =  '
CREATE TABLE data_raw (
  serial INTEGER NOT NULL,
  type CHAR(1) NOT NULL,
  data DECIMAL NOT NULL,
  time TIMESTAMP NOT NULL
);
  '

  # Configure this line as the source directory to deploy from
  $project_src = '/vagrant/'

  exec {'seads-db':
    command => "sudo -u postgres psql -c 'CREATE DATABASE seads;'",
    unless  => 'sudo -u postgres psql -l seads',
    require => Class['postgres'],
  }

  db_user {'landingzone':
    password => '',
    require  => Exec['seads-db'],
  }

  db_user {'seadapi':
    password => '',
    require  => Exec['seads-db'],
  }

  file {'data_raw.sql':
    ensure  => present,
    path    => '/home/landingzone/data_raw.sql',
    mode    => '0440',
    owner   => 'postgres',
    content => 'puppet:///modules/deploy/data_raw.sql',
    require => Exec['seads-db'],
  }

  exec {'create-table':
    command => "sudo -u postgres psql -d seads -c '${data_raw_schema}'",
    unless  => "sudo -u postgres psql -d seads -c '\\d data_raw;'",
    require => File['data_raw.sql'],
  }

  exec {'enable-tablefunc':
    command => 'sudo -u postgres psql -d seads -c "CREATE EXTENSION tablefunc;"',
    require => Exec['seads-db'],
  }

  exec {'deploy.sh':
    command => "/etc/puppet/modules/deploy/files/deploy.sh ${project_src}",
    require => Exec['create-table'],
  }
}

