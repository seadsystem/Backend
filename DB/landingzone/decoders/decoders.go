package decoders
package math

import (
    "math"
)

// Extract data sent from sensor from request
func decodePacket(buffer []byte) {
    // TODO set the types in this struct
    type SeadPacket struct {
        type
        location 
        timestamp
        period
        count
        data
        serial
    }
    var packet SeadPacket
    for i := 0; i < len(buffer); {
        var datatype := buffer[i]
        i++

        // Switch on the type of data sent in the packet
        switch {
        case datatype == 'T':
            // Type
            packet.type := buffer[i]
            i++
        case datatype == 'l':
            // Location
            packet.location := buffer[i]
            i++
        case datatype == 't':
            // Timestamp
            packet.timestamp := asciiTimeToDouble(buffer[i:i+14])
            i += 14
        case datatype == 'P':
            // Period separator
            packet.period := asciiTimeToDouble(buffer[i:i+14])
            i += 14
        case datatype == 'C':
            // Count
            packet.count := buffer[i:i+2]
            i += 2
        case datatype == 'D':
            // Data
            // if count isn't set, return error
            // TODO finish parsing data
        case datatype == 'S':
            // Serial
            packet.serial := buffer[i:i+6]
            i += 6
        case datatype == 'X':
            return packet
        default:
            // error: unknown field
        }
    }
    // return error
}

func double_to_ascii_time(double_time float64) (string) {
   var days = Floor(double_time / (60*60*24))
   var hours = Floor((double_time % (60*60*24)) / (60*60))
   var minutes = Floor((double_time % (60*60))   / (60))
   var seconds = Floor((double_time % (60)) / (1))
   var milliseconds = Floor(((double_time * 1000) %1000))
   var clock_time = Floor(((double_time * 12000) %12))

   return fmt.Sprintf("%03d%02d%02d%02d%03d%02d", days, hours, minutes, seconds, milliseconds, clock_time)
}
