package eGaugeDecoders

import (
	"encoding/xml"
)

type Cname struct {
	Type string `xml:"t,attr"`
	Name string `xml:",chardata"`
}

type Row struct {
	Columns []string `xml:"c"`
}

type Data struct {
	Columns   int     `xml:"columns,attr"`
	Timestamp int64   `xml:"time_stamp,attr"`
	Delta     int     `xml:"time_delta,attr"`
	Rows      []Row   `xml:"r"`
	Cnames    []Cname `xml:"cname"`
}

type Packet struct {
	Serial int64  `xml:"serial,attr"`
	Data   []Data `xml:"data"`
}

func DecodePacket(raw []byte) (packet Packet, err error) {
	err = xml.Unmarshal(raw, &packet)
	return
}
