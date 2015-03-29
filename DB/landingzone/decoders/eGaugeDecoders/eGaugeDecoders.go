package eGaugeDecoders

import (
	"encoding/xml"
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
	Delta     int64   `xml:"time_delta,attr"`
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
