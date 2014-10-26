# Unix user type for creating additional users
define unix_user (
  $groups,
  $username = $title,
) {
  #  include "user"
  user {$username:
    ensure     => 'present',
    groups     => $groups,
    require    => Group['db'],
    home       => "/home/${username}",
    shell      => '/bin/bash',
    managehome => true,
  }

  file {"${username}-bashrc":
    ensure => 'present',
    path   => "/home/${username}/.bashrc",
    source => 'puppet:///modules/unix_user/bashrc',
    mode   => '0644',
    owner  => $username,
    group  => $username,
  }
}
