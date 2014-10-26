Exec { path => ['/usr/local/sbin', '/usr/local/bin', '/usr/sbin', '/usr/bin', '/sbin', '/bin'] }

include "config"
include "postgres"
include "go"

Class['config']
  -> Class['postgres']
  -> Class['go']
