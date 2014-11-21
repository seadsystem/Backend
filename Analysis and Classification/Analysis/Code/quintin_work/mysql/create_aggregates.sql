/*
 * Create By: Quintin Leong
 * Create Date: November 5th, 2014
 * File Name: createAggregates.sql
 * File Desciption: Creates aggregate tables for raw data metrics for device categories
 * 		so that differentiating by device, sensor type, packets, etc.  becomes trivial.
 *		Runs on data produced by import.sql.
 *
 * 	***NOTES***
 * 	- SAFE UPDATE MODE MUST BE TURNED OFF TO EXECUTE UPDATES STATEMENTS IN THIS SCRIPT
 *	- The following sampling frequencies were updated to the following specs:
 * 		- current(4): 2.4 kHz
 * 		- voltage(2): 2.4kHz
 * 		- wattage(5)- 1 Hz
 * 		- temperature(6): 0.2 Hz
 *
 * Output Table(s): scratch.computer 
 * 					scratch.lamp 
 * 					scratch.microwave 
 * 					scratch.television.
 *
 * Drops Table(s):	scratch.computer_raw, 
 *					scratch.television_raw, 
 *					scratch.lamp_raw,
 *					scratch.microwave_raw
 */
 




-- Create computer aggregate table
CREATE TABLE scratch.computer(
	line_id INT(10) PRIMARY KEY auto_increment,
	device_id INT(10) NOT NULL,
	sensor_id INT(10) NOT NULL,
	packet_id INT(10) NOT NULL,
	sensor_type_id INT(10) NOT NULL,
	sensor_type VARCHAR(50) NOT NULL,
	`data` DOUBLE NOT NULL,
	period INT(10) NOT NULL,
	microstamp BIGINT(20) NOT NULL
);

INSERT INTO scratch.computer(device_id, sensor_id, packet_id, sensor_type_id, sensor_type, `data`, period, microstamp)
SELECT 
	s.device_id,
	cr.sensor_id,
	cr.packet_id,
	st.sensor_type_id,
	st.sensor_type,
	cr.`data`,
	s.period,
	cr.microstamp

FROM scratch.computer_raw cr
JOIN shempserver.sensors s
	ON cr.sensor_id = s.sensor_id
JOIN shempserver.sensor_types st
	ON s.sensor_type_id = st.sensor_type_id
ORDER BY 2,4,7 ASC
;

ALTER TABLE scratch.computer 
CHANGE period frequency DOUBLE NOT NULL;

/*
 * 
 */
-- You must make sure safe update mode is not on to execute these update statements
UPDATE scratch.computer
SET frequency = 2400
WHERE sensor_type_id = 2
;
UPDATE scratch.computer
SET frequency = 2400
WHERE sensor_type_id = 4
;
UPDATE scratch.computer
SET frequency = 1
WHERE sensor_type_id = 5
;
UPDATE scratch.computer
SET frequency = 0.2
WHERE sensor_type_id = 6
;

CREATE INDEX i ON scratch.computer(packet_id);

DROP TABLE scratch.computer_raw;



-- Create lamp aggregate table.
CREATE TABLE scratch.lamp(
	line_id INT(10) PRIMARY KEY auto_increment,
	device_id INT(10) NOT NULL,
	sensor_id INT(10) NOT NULL,
	packet_id INT(10) NOT NULL,
	sensor_type_id INT(10) NOT NULL,
	sensor_type VARCHAR(50) NOT NULL,
	`data` DOUBLE NOT NULL,
	period INT(10) NOT NULL,
	microstamp BIGINT(20) NOT NULL
);

INSERT INTO scratch.lamp(device_id, sensor_id, packet_id, sensor_type_id, sensor_type, `data`, period, microstamp)
SELECT 
	s.device_id,
	cr.sensor_id,
	cr.packet_id,
	st.sensor_type_id,
	st.sensor_type,
	cr.`data`,
	s.period,
	cr.microstamp

FROM scratch.lamp_raw cr
JOIN shempserver.sensors s
	ON cr.sensor_id = s.sensor_id
JOIN shempserver.sensor_types st
	ON s.sensor_type_id = st.sensor_type_id
ORDER BY 2,4,7 ASC
;

ALTER TABLE scratch.lamp
CHANGE period frequency DOUBLE NOT NULL;

/*
 * 4(current)- 2.4 kHz
 * 2(voltage- 2.4kHz
 * 5(wattage)- 1 Hz
 * 6(temperature)- 0.2 Hz
 */
-- You must make sure safe update mode is not on to execute these update statements
UPDATE scratch.lamp
SET frequency = 2400
WHERE sensor_type_id = 2
;
UPDATE scratch.lamp
SET frequency = 2400
WHERE sensor_type_id = 4
;
UPDATE scratch.lamp
SET frequency = 1
WHERE sensor_type_id = 5
;
UPDATE scratch.lamp
SET frequency = 0.2
WHERE sensor_type_id = 6
;

CREATE INDEX i ON scratch.lamp(packet_id);

DROP TABLE scratch.lamp_raw;


-- Create speaker aggregate table.
CREATE TABLE scratch.speaker(
	line_id INT(10) PRIMARY KEY auto_increment,
	device_id INT(10) NOT NULL,
	sensor_id INT(10) NOT NULL,
	packet_id INT(10) NOT NULL,
	sensor_type_id INT(10) NOT NULL,
	sensor_type VARCHAR(50) NOT NULL,
	`data` DOUBLE NOT NULL,
	period INT(10) NOT NULL,
	microstamp BIGINT(20) NOT NULL
);

INSERT INTO scratch.speaker(device_id, sensor_id, packet_id, sensor_type_id, sensor_type, `data`, period, microstamp)
SELECT 
	s.device_id,
	cr.sensor_id,
	cr.packet_id,
	st.sensor_type_id,
	st.sensor_type,
	cr.`data`,
	s.period,
	cr.microstamp

FROM scratch.speaker_raw cr
JOIN shempserver.sensors s
	ON cr.sensor_id = s.sensor_id
JOIN shempserver.sensor_types st
	ON s.sensor_type_id = st.sensor_type_id
ORDER BY 2,4,7 ASC
;

ALTER TABLE scratch.speaker
CHANGE period frequency DOUBLE NOT NULL;

/*
 * 4(current)- 2.4 kHz
 * 2(voltage- 2.4kHz
 * 5(wattage)- 1 Hz
 * 6(temperature)- 0.2 Hz
 */
-- You must make sure safe update mode is not on to execute these update statements
UPDATE scratch.speaker
SET frequency = 2400
WHERE sensor_type_id = 2
;
UPDATE scratch.speaker
SET frequency = 2400
WHERE sensor_type_id = 4
;
UPDATE scratch.speaker
SET frequency = 1
WHERE sensor_type_id = 5
;
UPDATE scratch.speaker
SET frequency = 0.2
WHERE sensor_type_id = 6
;

CREATE INDEX i ON scratch.speaker(packet_id);

DROP TABLE scratch.speaker_raw;




-- Create television aggregate table
CREATE TABLE scratch.television(
	line_id INT(10) PRIMARY KEY auto_increment,
	device_id INT(10) NOT NULL,
	sensor_id INT(10) NOT NULL,
	packet_id INT(10) NOT NULL,
	sensor_type_id INT(10) NOT NULL,
	sensor_type VARCHAR(50) NOT NULL,
	`data` DOUBLE NOT NULL,
	period INT(10) NOT NULL,
	microstamp BIGINT(20) NOT NULL
);

INSERT INTO scratch.television(device_id, sensor_id, packet_id, sensor_type_id, sensor_type, `data`, period, microstamp)
SELECT 
	s.device_id,
	cr.sensor_id,
	cr.packet_id,
	st.sensor_type_id,
	st.sensor_type,
	cr.`data`,
	s.period,
	cr.microstamp

FROM scratch.television_raw cr
JOIN shempserver.sensors s
	ON cr.sensor_id = s.sensor_id
JOIN shempserver.sensor_types st
	ON s.sensor_type_id = st.sensor_type_id
ORDER BY 2,4,7 ASC
;

ALTER TABLE scratch.television
CHANGE period frequency DOUBLE NOT NULL;

/*
 * 4(current)- 2.4 kHz
 * 2(voltage- 2.4kHz
 * 5(wattage)- 1 Hz
 * 6(temperature)- 0.2 Hz
 */
-- You must make sure safe update mode is not on to execute these update statements
UPDATE scratch.television
SET frequency = 2400
WHERE sensor_type_id = 2
;
UPDATE scratch.television
SET frequency = 2400
WHERE sensor_type_id = 4
;
UPDATE scratch.television
SET frequency = 1
WHERE sensor_type_id = 5
;
UPDATE scratch.television
SET frequency = 0.2
WHERE sensor_type_id = 6
;

CREATE INDEX i ON scratch.television(packet_id);

DROP TABLE scratch.television_raw;
