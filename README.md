# bananaLights
## RPi Controlled Lighting
This project automates the control of an LED strip. The goal is an unobtrusive and simple approach to ambient lighting. 

In this state the project has four modes:

1. Late night- lights off, unless the PIR senses your movement.
2. Daytime - lights off
3. Evening - lights low, unless the PIR senses your movement.
4. Override - lights up

It has two inputs, a button and PIR sensor, and controls two outputs, an indicator LED and the 12V LED light strip.

###Setup
1. Create the map database, and a device table.

		create database map;
		create table map.device (
		id INT NOT NULL AUTO_INCREMENT,
	    name varchar(250),
	    location varchar(250),
	     PRIMARY KEY (id)
	    );
		ALTER TABLE map.device ADD CONSTRAINT unique_device UNIQUE (name, location);


2. `python settings.py` initilizes the devices hourly settings. You can adjust hours by changing the 	`base` list. `base[0]` is the 0 index setting for PWM when the PIR is low `base[0][0]` and high `base[0][1]`.
3. Run `fade.py`. This starts the lighting. 
4. Start at boot
`@reboot /usr/bin/pigpiod`
`@reboot /home/pi/Documents/bananaLights/lighting/fade.py & >> /home/pi/Documents/bananaLights/log.txt`

#Supplies

1. Raspberry Pi (or equivalent) - I use Raspberry Pi Zero
2. DC/DC Buck Converter - Brings down the presumed 12V wall-power to a usable 5V to power the Pi.
3. MOSFET PWM Driver Circuit
4. PIR Sensor
5. Momentary Button


#Pinout
	                            J8
	                           .___.              
	                  +3V3---1-|O O|--2--+5V
	    			 GPIO2---3-|O O|--4--+5V
	    			 GPIO3---5-|O O|--6--_
	    			 GPIO4---7-|O O|--8-----GPIO14 
	                      _--9-|O.O|-10-----GPIO15 
	    			GPIO17--11-|O O|-12-----GPIO18  - PIR Sensor Input
	    			GPIO27--13-|O O|-14--_
	    			GPIO22--15-|O O|-16-----GPIO23	- MOSFET PWM Output  
	                  +3V3--17-|O O|-18-----GPIO24 
	    			GPIO10--19-|O.O|-20--_
	    			GPIO9 --21-|O O|-22-----GPIO25 
	    			GPIO11--23-|O O|-24-----GPIO8  
	                      _-25-|O O|-26-----GPIO7  
	       			ID_SD---27-|O O|-28-----ID_SC 
	 Red LED Anode  GPIO5---29-|O.O|-30--_
	Blue LED Anode  GPIO6---31-|O O|-32-----GPIO12	- Mode Switch Input
	                GPIO13--33-|O O|-34--_
	                GPIO19--35-|O O|-36-----GPIO16
	                GPIO26--37-|O O|-38-----GPIO20
	                      _-39-|O O|-40-----GPIO21
	                           '---'
