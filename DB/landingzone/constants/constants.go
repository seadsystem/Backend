/*
 * Package contains constants and config for the program. Easier than a true config file.
 */
package constants

const (
	HOST           = "0.0.0.0" // All host names
	SEAD_PLUG_PORT = "9000"
	EGAUGE_PORT    = "9002"

	LENGTH_HEADER_SIZE = 3 // Measured in bytes

	// Packet constants for plug communication
	HEAD   = "@H\n"
	ACK    = "\x06\n"
	OKAY   = "@K\n"
	CONFIG = "@SLITIsEP00000000500000C00001\n@SLITVsEP00000000500000C00001\n@SLITWsEP00000000500000C00001\n@SLITTsEP00000000500000C00001\n" // Sample config pulled from the old database for plug serial #00001

	READ_TIME_LIMIT  = 10 // Measured in seconds
	WRITE_TIME_LIMIT = 5  // Measured in seconds

	// Database
	DB_SOCKET    = "/var/run/postgresql" // Use localhost or appropriate hostname for IP connection.
	DB_PORT      = 5432
	DB_USER      = "landingzone"
	DB_NAME      = "seads"
	DB_PASSWORD  = "" // Password unneeded for Postgres peer authentication.
	DB_MAX_CONNS = 90 // Should be slightly smaller than the max number in PostgreSQL's postgresql.conf file.
)

var Verbose bool = false
