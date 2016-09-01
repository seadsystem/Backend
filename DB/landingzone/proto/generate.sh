#!/bin/bash
protoc packet/packet.proto --go_out=plugins=grpc:.
