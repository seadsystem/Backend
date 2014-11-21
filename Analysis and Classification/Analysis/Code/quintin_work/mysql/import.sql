/*
 * Created By: Quintin Leong
 * File Name: import.sql
 * File Description: imports all csv data from local machine to raw tables in scratch database.
 *					 this is all the data that we collected in sprint #1.
 *
 * Output Table(s): scratch.computer_raw
 *					scratch.television_raw 
 *					scratch.lamp_raw
 *					scratch.microwave_raw.
 */

-- Drop and create the computer_raw table
DROP TABLE scratch.computer_raw;
CREATE TABLE scratch.computer_raw(
	sensor_id INT(10) NOT NULL,
	packet_id INT(10) NOT NULL,
	`data` DOUBLE,
	microstamp BIGINT(20),
	device_microstamp BIGINT(20)
);


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/computer_1.csv'
INTO TABLE scratch.computer_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/computer_2.csv'
INTO TABLE scratch.computer_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/computer_3.csv'
INTO TABLE scratch.computer_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/computer_4.csv'
INTO TABLE scratch.computer_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/computer_5.csv'
INTO TABLE scratch.computer_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/computer_6.csv'
INTO TABLE scratch.computer_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


-- Drop and create the television_raw table
DROP TABLE scratch.television_raw;
CREATE TABLE scratch.television_raw(
	sensor_id INT(10) NOT NULL,
	packet_id INT(10) NOT NULL,
	`data` DOUBLE,
	microstamp BIGINT(20),
	device_microstamp BIGINT(20)
);


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/tv_1.csv'
INTO TABLE scratch.television_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/tv_2.csv'
INTO TABLE scratch.television_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/tv_3.csv'
INTO TABLE scratch.television_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


-- Drop and create the lamp_raw table
DROP TABLE scratch.lamp_raw;
CREATE TABLE scratch.lamp_raw(
	sensor_id INT(10) NOT NULL,
	packet_id INT(10) NOT NULL,
	`data` DOUBLE,
	microstamp BIGINT(20),
	device_microstamp BIGINT(20)
);


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/lamp_1.csv'
INTO TABLE scratch.lamp_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/lamp_2.csv'
INTO TABLE scratch.lamp_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/lamp_3.csv'
INTO TABLE scratch.lamp_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/lamp_4.csv'
INTO TABLE scratch.lamp_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/lamp_5.csv'
INTO TABLE scratch.lamp_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


-- Drop and create the microwave_raw table
DROP TABLE scratch.microwave_raw;
CREATE TABLE scratch.microwave_raw(
	sensor_id INT(10) NOT NULL,
	packet_id INT(10) NOT NULL,
	`data` DOUBLE,
	microstamp BIGINT(20),
	device_microstamp BIGINT(20)
);


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/microwave_1.csv'
INTO TABLE scratch.microwave_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/microwave_2.csv'
INTO TABLE scratch.microwave_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


-- Drop and create the speaker_raw table
DROP TABLE scratch.speaker_raw;
CREATE TABLE scratch.speaker_raw(
	sensor_id INT(10) NOT NULL,
	packet_id INT(10) NOT NULL,
	`data` DOUBLE,
	microstamp BIGINT(20),
	device_microstamp BIGINT(20)
);


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/speakers_1.csv'
INTO TABLE scratch.speaker_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/speakers_2.csv'
INTO TABLE scratch.speaker_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;


LOAD DATA LOCAL INFILE '/Users/Quintin/Desktop/School/CMPS115/analysis/analysis/speakers_3.csv'
INTO TABLE scratch.speaker_raw
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES;
