package decoders

import (
	"errors"
	"log"
	"regexp"
	"strconv"
	"time"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
)

type SeadPacket struct {
	Type      byte
	Location  byte
	Timestamp time.Time
	Period    time.Duration
	Count     uint
	Data      []int16
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
func DecodeHeader(packet []byte) (serial int, offset time.Time, err error) {
	headerStrings := headerRegex.FindSubmatch(packet)

	if headerStrings == nil || len(headerStrings) != 3 {
		err = InvalidHeader
		return
	}

	log.Printf("Header serial string: %s\n", string(headerStrings[1]))

	var duration time.Duration
	duration, err = AsciiTimeToDuration(headerStrings[2])
	if err != nil {
		return
	}

	offset = time.Now().Add(-1 * duration)

	serial, err = strconv.Atoi(string(headerStrings[1]))
	return
}

// DecodePacket extracts the data sent from sensor
func DecodePacket(buffer []byte, offset time.Time) (packet SeadPacket, err error) {
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
			var on_time time.Duration
			on_time, err = AsciiTimeToDuration(buffer[i : i+14])
			packet.Timestamp = offset.Add(on_time)
			i += 14
		case datatype == 'P':
			// Period separator
			packet.Period, err = AsciiTimeToDuration(buffer[i : i+14])
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
				packet.Data = make([]int16, count)
				for i := 0; i < bytes; i += 2 {
					packet.Data[i/2] = int16(Binary2uint(data[i : i+2]))
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

// Binary2uint converts a byte array containing binary data into an int
func Binary2uint(data []byte) (total uint) {
	for index, element := range data {
		total += uint(element) << uint(index*8)
	}
	return
}

func AsciiTimeToDuration(ascii_time []byte) (duration time.Duration, err error) {
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
	duration += time.Hour * time.Duration(24*days)
	hours, err := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	if err != nil {
		return
	}
	ptr += 2
	duration += time.Hour * time.Duration(hours)
	minutes, err := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	if err != nil {
		return
	}
	ptr += 2
	duration += time.Minute * time.Duration(minutes)
	seconds, err := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	if err != nil {
		return
	}
	ptr += 2
	duration += time.Second * time.Duration(seconds)
	milliseconds, err := strconv.Atoi(string(ascii_time[ptr : ptr+3]))
	if err != nil {
		return
	}
	ptr += 3
	duration += time.Millisecond * time.Duration(milliseconds)
	clock, err := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	if err != nil {
		return
	}
	ptr += 2
	duration += time.Millisecond * time.Duration(clock) / 12
	return
}
