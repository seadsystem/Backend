package eGaugeDecoders

import (
	"encoding/xml"
	"fmt"
	"log"
	"strconv"
	"time"

	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

type Cname struct {
	Type string `xml:"t,attr"`
	Name string `xml:",chardata"`
}

type Row struct {
	Columns []int64 `xml:"c"`
}

type Data struct {
	Columns   int64   `xml:"columns,attr"`
	Timestamp string  `xml:"time_stamp,attr"`
	TimeDelta int64   `xml:"time_delta,attr"`
	DataDelta bool    `xml:"delta,attr"`
	Rows      []Row   `xml:"r"`
	Cnames    []Cname `xml:"cname"`
}

type Packet struct {
	Serial string `xml:"serial,attr"`
	Data   []Data `xml:"data"`
}

func DecodePacket(raw []byte) (packet Packet, err error) {
	err = xml.Unmarshal(raw, &packet)
	return
}

func NewIterator(packet Packet) (decoders.Iterator, error) {
	log.Println("Preliminary data processing...")

	// Process data packet
	log.Println("Reading serial:", packet.Serial)
	serial, err := strconv.ParseInt(packet.Serial, 0, 64)
	if err != nil {
		return decoders.NewEmptyIterator(), fmt.Errorf("reading serial: %v", err)
	}
	if serial <= 0 {
		return decoders.NewEmptyIterator(), fmt.Errorf("invalid serial: %v", serial)

	}

	if len(packet.Data) == 0 {
		log.Println("Error: No data in packet")
		return decoders.NewEmptyIterator(), decoders.NoData
	}

	// Select data set with finest granularity
	data := &packet.Data[0]
	columns := &data.Cnames
	for i := 1; i < len(packet.Data); i++ {
		if packet.Data[i].TimeDelta < data.TimeDelta {
			data = &packet.Data[i]
		}
	}

	// Get data set start time
	log.Println("Reading start time:", data.Timestamp)
	startUnixTime, err := strconv.ParseInt(data.Timestamp, 0, 64)
	if err != nil || startUnixTime <= 0 {
		return decoders.NewEmptyIterator(), fmt.Errorf("invalid start time: %s", data.Timestamp)
	}
	startTime := time.Unix(startUnixTime, 0)

	log.Println("Columns:", *columns)
	columnTypes := make([]byte, len(*columns))
	for i, column := range *columns {
		b := []byte(column.Type)
		if len(b) != 1 {
			return decoders.NewEmptyIterator(), fmt.Errorf("invalid column: %s", column)
		}
		columnTypes[i] = b[0]
	}

	interpTime := startTime // Set timestamp for first data point to time in packet
	var currData = make([]int64, len(*columns))

	log.Println("Creating iterator...")
	rowNum := 0
	colNum := 0
	return func() (*decoders.DataPoint, error) {
		if colNum >= len(*columns) {
			// Done with row
			colNum = 0
			rowNum++
			interpTime = interpTime.Add(time.Duration(data.TimeDelta) * time.Second * -1) // Add data point time spacing for next data point
		}
		if rowNum >= len(data.Rows) {
			// No more data
			return nil, nil
		}

		// Quick sanity check
		if len(data.Rows[rowNum].Columns) != len(*columns) {
			return nil, fmt.Errorf("invalid row: %v", data.Rows[rowNum].Columns)
		}

		if data.DataDelta {
			currData[colNum] += data.Rows[rowNum].Columns[colNum]
		} else {
			currData[colNum] = data.Rows[rowNum].Columns[colNum]
		}

		point := &decoders.DataPoint{
			Serial: serial,
			Type:   columnTypes[colNum],
			Data:   currData[colNum],
			Time:   interpTime,
			Device: &(*columns)[colNum].Name,
		}

		// Done with cell
		colNum++
		return point, nil
	}, nil
}
