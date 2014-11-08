package decoders

import (
	"errors"
	"fmt"
	"log"
	"math"
	"regexp"
	"strconv"
	"time"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
)

type SeadPacket struct {
	Type      byte
	Location  byte
	Timestamp time.Time
	Period    float64
	Count     uint
	Data      []uint16
	Serial    int
}

var headerRegex *regexp.Regexp
var InvalidHeader = errors.New("Invalid header.")
var InvalidPacket = errors.New("Invalid packet.")
var InvalidTime = errors.New("Invalid time.")

// init sets up stuff we need with proper error handling. If it isn't complicated or doesn't need error handling, it can probably just be assigned directly.
func init() {
	var err error
	headerRegex, err = regexp.Compile(constants.HEADER_REGEX)
	if err != nil {
		log.Panic("Regex compile error:", err)
	}
}

// DecodeHeader verifies that the header is in the correct format and extracts the serial number
func DecodeHeader(packet []byte) (serial int, offset float64, err error) {
	headerStrings := headerRegex.FindSubmatch(packet)

	if headerStrings == nil || len(headerStrings) != 3 {
		err = InvalidHeader
		return
	}

	log.Printf("Header serial string: %s\n", string(headerStrings[1]))

	var double_time float64
	double_time, err = asciiTimeToDouble(headerStrings[2])
	if err != nil {
		return
	}

	offset = float64(time.Now().Unix()) - double_time

	serial, err = strconv.Atoi(string(headerStrings[1]))
	return
}

// DecodePacket extracts the data sent from sensor
func DecodePacket(buffer []byte, offset float64) (packet SeadPacket, err error) {
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
			var double_time float64
			double_time, err = asciiTimeToDouble(buffer[i : i+14])
			double_time += offset
			micro := math.Pow10(6)
			packet.Timestamp = time.Unix(int64(double_time), int64(double_time*micro)%int64(micro))
			//packet.Timestamp, err = asciiTimeToDouble(buffer[i : i+14])
			i += 14
		case datatype == 'P':
			// Period separator
			packet.Period, err = asciiTimeToDouble(buffer[i : i+14])
			i += 14
		case datatype == 'C':
			// Count
			packet.Count = Binary2uint(buffer[i : i+2])
			i += 2
		case datatype == 'D':
			// Data
			// if count isn't set, return error
			if packet.Count == 0 {
				err = InvalidPacket
			} else {
				count := int(packet.Count)
				bytes := count * 2
				data := buffer[i : i+bytes]
				packet.Data = make([]uint16, count)
				for i := 0; i < bytes; i += 2 {
					packet.Data[i/2] = Binary2uint16(data[i : i+2])
				}
				i += bytes
			}
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

func doubleToasciiTime(double_time float64) string {
	int_time := int(double_time)
	var days = int(math.Floor(double_time / (60 * 60 * 24)))
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

// Every checks if every byte in a slice meets some criteria
func Every(data []byte, check func(byte) bool) bool {
	for _, element := range data {
		if !check(element) {
			return false
		}
	}
	return true
}

// Binary2uint converts a byte array containing binary data into an int
func Binary2uint(data []byte) (total uint) {
	for index, element := range data {
		total += uint(element) << uint(index*8)
	}
	return
}

// Binary2uint16 converts a 2 byte array containing binary data into an uint16
func Binary2uint16(data []byte) (total uint16) {
	return uint16(data[0]) + uint16(data[1]<<8)
}
