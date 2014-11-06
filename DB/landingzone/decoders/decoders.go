package decoders

import (
	"errors"
	"fmt"
	"log"
	"math"
	"regexp"
	"strconv"

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
var InvalidTime = errors.New("Invalid time.")

func init() {
	var err error
	headerRegex, err = regexp.Compile(constants.HEADER_REGEX)
	if err != nil {
		log.Panic("Regex compile error:", err)
	}
}

func DecodeHeader(packet []byte) (serial int, err error) {
	serialStrings := headerRegex.FindSubmatch(packet)

	if serialStrings == nil {
		err = InvalidHeader
		return
	}
	log.Printf("Found %d serials.\n", len(serialStrings))
	if len(serialStrings) != 1 {
		err = InvalidHeader
		return
	}
	log.Printf("Header serial string: %s\n", string(serialStrings[0]))

	serial, err = strconv.Atoi(string(serialStrings[0]))
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

func asciiTimeToDouble(ascii_time []byte) (time float64, err error) {
	// Check time string format
	if len(ascii_time) != 16 {
		err = InvalidTime
	}
	_, err = strconv.Atoi(string(ascii_time))
	if err != nil {
		return
	}

	// Do the conversion now that we know it should work
	var ptr int = 0
	days, err := strconv.Atoi(string(ascii_time[ptr : ptr+3]))
	if err != nil {
		return
	}
	ptr += 3
	time += float64(60 * 60 * 24 * days)
	hours, err := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	if err != nil {
		return
	}
	ptr += 2
	time += float64(60 * 60 * hours)
	minutes, err := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	if err != nil {
		return
	}
	ptr += 2
	time += float64(60 * minutes)
	seconds, err := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	if err != nil {
		return
	}
	ptr += 2
	time += float64(seconds)
	milliseconds, err := strconv.Atoi(string(ascii_time[ptr : ptr+3]))
	if err != nil {
		return
	}
	ptr += 3
	time += float64(milliseconds) / 1000.0
	clock, err := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	if err != nil {
		return
	}
	ptr += 2
	time += float64(clock) / 12000.0
	return
}

func every(data []byte, check func(byte) bool) bool {
	for _, element := range data {
		if !check(element) {
			return false
		}
	}
	return true
}
