/*
 * Package seadPlugDecoders contains functions to decode raw packets.
 */
package seadPlugDecoders

import (
	"errors"
	"fmt"
	"log"
	"regexp"
	"strconv"
	"time"

	"github.com/seadsystem/Backend/DB/landingzone/decoders"
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

// Header regex. Stored globally so it only needs to be compiled once in init.
var (
	headerRegex       *regexp.Regexp
	headerRegexString = "^(?:THS)(\\d+)(?:t)(\\d+)(?:X)$"
)

// Errors
var (
	InvalidHeader = errors.New("Invalid header.")
	InvalidPacket = errors.New("Invalid packet.")
)

// init sets up stuff we need with proper error handling. If it isn't complicated or doesn't need error handling, it can probably just be assigned directly.
func init() {
	compileRegex()
}

// compileRegex compiles all regexs needed for decoding SeadPackets.
// Panics on regex compile error.
func compileRegex() {
	var err error
	headerRegex, err = regexp.Compile(headerRegexString)
	if err != nil {
		log.Panic("regex compile error: ", err)
	}
}

// DecodeHeader verifies that the header is in the correct format and extracts the serial number
func DecodeHeader(packet []byte) (serial int, offset time.Time, err error) {
	headerStrings := headerRegex.FindSubmatch(packet)

	// Header has two parts, serial number and offset. The headerStrings should contain the entire header string in position 0, the serial number in position 1, and the offset in position 2.
	if headerStrings == nil || len(headerStrings) != 3 {
		err = InvalidHeader
		return
	}

	log.Printf("Header serial string: %s\n", string(headerStrings[1]))

	var duration time.Duration
	duration, err = AsciiTimeToDuration(headerStrings[2])
	log.Printf("Duration: %v\n", duration)
	if err != nil {
		return
	}

	offset = time.Now().Add(-1 * duration)

	serial, err = strconv.Atoi(string(headerStrings[1])) // Serial number should be 5 digit integer
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
			// if count isn't set, return error. Count is required to tell us how much data we have.
			if packet.Count == 0 {
				err = InvalidPacket
			} else {
				count := int(packet.Count)
				bytes := count * 2
				data := buffer[i : i+bytes]
				packet.Data = make([]int16, count)
				for i := 0; i < bytes; i += 2 {
					// Data is an array of 16 bit (2 byte) integers.
					packet.Data[i/2] = int16(Binary2uint(data[i : i+2]))
				}
				i += bytes
			}
		case datatype == 'S':
			// Serial
			packet.Serial, err = strconv.Atoi(string(buffer[i : i+6]))
			i += 6
		case datatype == 'X':
			// End of packet
			return
		default:
			err = InvalidPacket
		}

		// Return any error generated during loop iteration
		if err != nil {
			return
		}
	}

	// Breaking out of loop constitutes an error.
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

// AsciiTimeToDuration converts plug time string to an integral duration type
func AsciiTimeToDuration(ascii_time []byte) (time.Duration, error) {
	// Check time string format
	if len(ascii_time) != 14 {
		return 0, fmt.Errorf("invalid ascii time: %s", string(ascii_time))
	}

	// Check that all characters are integers.
	for _, digit := range ascii_time {
		if digit < '0' || digit > '9' {
			return 0, fmt.Errorf("invalid ascii time: %s", string(ascii_time))
		}
	}

	// Do the conversion now that we know it should work
	var ptr int
	var duration time.Duration

	days, _ := strconv.Atoi(string(ascii_time[ptr : ptr+3]))
	ptr += 3
	duration += time.Hour * time.Duration(24*days)
	hours, _ := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	ptr += 2
	duration += time.Hour * time.Duration(hours)
	minutes, _ := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	ptr += 2
	duration += time.Minute * time.Duration(minutes)
	seconds, _ := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	ptr += 2
	duration += time.Second * time.Duration(seconds)
	milliseconds, _ := strconv.Atoi(string(ascii_time[ptr : ptr+3]))
	ptr += 3
	duration += time.Millisecond * time.Duration(milliseconds)
	clock, _ := strconv.Atoi(string(ascii_time[ptr : ptr+2]))
	ptr += 2
	duration += time.Millisecond * time.Duration(clock) / 12
	return duration, nil
}

// NewIterator creates a closure over a SeadPacket.
// Each time the returned function is called, it returns data and no error, no data and an error, or no data and no error to indicate that no more data is available.
func NewIterator(packet SeadPacket) decoders.Iterator {
	interpTime := packet.Timestamp // Set timestamp for first data point to time in packet
	i := 0
	return func() (*decoders.DataPoint, error) {
		if i >= len(packet.Data) {
			// No more data
			return nil, nil
		}

		row := &decoders.DataPoint{
			Serial: int64(packet.Serial),
			Type:   packet.Type,
			Data:   int64(packet.Data[i]),
			Time:   interpTime,
		}

		i++
		interpTime = interpTime.Add(packet.Period) // Add data point time spacing for next data point
		return row, nil
	}
}
