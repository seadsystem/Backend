class deploy {
  import 'db_user'

  # Postgres table data_raw
  $table_schema =  '
CREATE TABLE data_raw (
  serial BIGINT NOT NULL,
  type CHAR(1) NOT NULL,
  data BIGINT NOT NULL,
  time TIMESTAMP NOT NULL,
  device TEXT NULL
);

CREATE INDEX data_raw_serial_time_type_device_idx ON data_raw(serial, time, type, device);
CLUSTER data_raw USING data_raw_serial_time_type_device_idx;

CREATE TABLE data_label (
  serial BIGINT NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  label TEXT NOT NULL
);

CREATE TABLE classifier_model (
  id UUID NOT NULL,
  created_at TIMESTAMP NOT NULL,
  model_type TEXT NOT NULL,
  model TEXT NOT NULL
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
    cwd       => '/vagrant',
    logoutput => true,
    require   => [
      Exec['create-table'],
      Db_user['landingzone'],
      Db_user['seadapi']
    ],
  }
}

