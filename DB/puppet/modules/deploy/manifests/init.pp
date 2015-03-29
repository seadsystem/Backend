class deploy {
  import 'db_user'

  # Postgres table data_raw
  $table_schema =  '
CREATE TABLE data_raw (
  serial BIGINT NOT NULL,
  type CHAR(1) NOT NULL,
  device TEXT NULL,
  data BIGINT NOT NULL,
  time TIMESTAMP NOT NULL
);

CREATE TABLE classifications (
  Serial BIGINT NOT NULL,
  StartTime TIMESTAMP NOT NULL,
  EndTime TIMESTAMP NOT NULL,
  Classification TEXT NOT NULL
);
  '

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

  exec {'create-table':
    command => "sudo -u postgres psql -d seads -c '${table_schema}'",
    unless  => "sudo -u postgres psql -d seads -c '\\d data_raw;'",
    require => Exec['seads-db'],
  }

  exec {'enable-tablefunc':
    command => 'sudo -u postgres psql -d seads -c "CREATE EXTENSION IF NOT EXISTS tablefunc;"',
    require => Exec['seads-db'],
  }

  exec {'deploy.sh':
    command   => '/etc/puppet/modules/deploy/files/deploy.sh',
    #cwd       => '/vagrant',
    require   => Exec['create-table'],
  }
}

