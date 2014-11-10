# Unix user type for creating additional users
define db_user (
  $username = $title,
  $password = false,
) {

  $db_sql = "CREATE DATABASE ${title};"
  $privs_sql = "GRANT ALL PRIVILEGES ON TABLE data_raw TO ${username};"

  exec {"${username}-user":
    command => "sudo -u postgres psql -c \"CREATE USER ${username};\"",
    unless  => "sudo -u ${username} psql -l",
  }
  exec {"${username}-privs":
    command => "sudo -u postgres psql -d seads -c '${privs_sql}'",
    require => Exec["${username}-user"],
  }
}
