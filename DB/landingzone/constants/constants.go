package constants

const (
	HOST = "0.0.0.0" // All host names
	PORT = "9000"

	LENGTH_HEADER_SIZE = 3 // Measured in bytes

	// Packet constants for plug communication
	HEAD   = "@H\n"
	ACK    = "\x06\n"
	OKAY   = "@K\n"
	CONFIG = "@SLITIsEP00000000500000C00001\n@SLITVsEP00000000500000C00001\n@SLITWsEP00000000500000C00001\n@SLITTsEP00000000500000C00001\n"

	READ_TIME_LIMIT  = 10 // Measured in seconds
	WRITE_TIME_LIMIT = 5  // Measured in seconds

	HEADER_REGEX = "^(?:THS)(\\d+)(?:t)(\\d+)(?:X)$"

	// Database
	DB_SOCKET   = "/var/run/postgresql"
	DB_PORT     = 5432
	DB_USER     = "landingzone"
	DB_NAME     = "seads"
	DB_PASSWORD = ""
)
