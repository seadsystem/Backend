package decoders

import (
	"errors"
	"math"
	"regexp"
	"strconv"
	"log"
	"fmt"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
)

type SeadPacket struct {
	Type      byte
	Location  byte
	Timestamp float64
	Period    float64
	Count     int
	Data      float64
	Serial    int
}

var headerRegex *regexp.Regexp
var InvalidHeader = errors.New("Invalid header.")
var InvalidPacket = errors.New("Invalid packet.")

func init() {
	headerRegex, err := regexp.Compile(constants.HEADER_REGEX)
	if err != nil {
		log.Println("Regex compile error:", err)
	}
}

func DecodeHeader(packet []byte) (serial int, err error) {
	serialString := headerRegex.Find(packet)
	if serialString == nil {
		err = InvalidHeader
		return
	}
	serial, err = strconv.Atoi(string(serialString))
	return
}

// Extract data sent from sensor from request
func DecodePacket(buffer []byte) (packet SeadPacket, err error) {
	for i := 0; i < len(buffer); {
		datatype := buffer[i]
		i++

		// Switch on the type of data sent in the packet
		switch {
		case datatype == 'T':
			// Type
			packet.Type = buffer[i]
			i++
		case datatype == 'l':
			// Location
			packet.Location = buffer[i]
			i++
		case datatype == 't':
			// Timestamp
			packet.Timestamp, err = asciiTimeToDouble(buffer[i : i+14])
			i += 14
		case datatype == 'P':
			// Period separator
			packet.Period, err = asciiTimeToDouble(buffer[i : i+14])
			i += 14
		case datatype == 'C':
			// Count
			packet.Count, err = strconv.Atoi(string(buffer[i : i+2]))
			i += 2
		case datatype == 'D':
			// Data
			// if count isn't set, return error
			// TODO finish parsing data
		case datatype == 'S':
			// Serial
			packet.Serial, err = strconv.Atoi(string(buffer[i : i+6]))
			i += 6
		case datatype == 'X':
			return
		default:
			err = InvalidPacket
		}

		if err != nil {
			return
		}
	}
	err = InvalidPacket
	return
}

func doubleToAsciiTime(double_time float64) string {
	int_time := int(double_time)
	var days = math.Floor(double_time / (60 * 60 * 24))
	var hours = (int_time % (60 * 60 * 24)) / (60 * 60)
	var minutes = (int_time % (60 * 60)) / 60
	var seconds = (int_time % (60)) / 1
	var milliseconds = (int_time * 1000) % 1000
	var clock_time = (int_time * 12000) % 12

	return fmt.Sprintf("%03d%02d%02d%02d%03d%02d", days, hours, minutes, seconds, milliseconds, clock_time)
}

func asciiTimeToDouble(asciiTime []byte) (float64, error) {
	return 0.0, nil
}
