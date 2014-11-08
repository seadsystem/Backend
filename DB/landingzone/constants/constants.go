package constants

const (
	HOST = "0.0.0.0" // All host names
	PORT = "9000"

	LENGTH_HEADER_SIZE = 3 // Measured in bytes

	// Packet constants for plug communication
	HEAD   = "@H\n"
	ACK    = "\x06\n"
	OKAY   = "@K\n"
	CONFIG = "@SLITIsEP00000000500000C00001\n" // Config value is no longer used by plug. We must still send it a valid config anyway.
	// Full config includes these lines too:
	//"@SLITVsEP00000000500000C00001\n"
	//"@SLITWsEP00000000500000C00001\n"
	//"@SLITTsEP00000000500000C00001\n"

	READ_TIME_LIMIT = 5 * 60 // Measured in seconds
	DB_TIME_LIMIT   = 10     // Measured in seconds

	HEADER_REGEX = "^(?:THS)(\\d+)(?:t)(\\d+)(?:X)$"

	// Database
	DB_SOCKET   = "/var/run/postgresql"
	DB_PORT     = 5432
	DB_USER     = "landingzone"
	DB_NAME     = "seads"
	DB_PASSWORD = ""
)
