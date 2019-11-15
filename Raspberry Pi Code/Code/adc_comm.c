#include <stdio.h>
#include <stdlib.h>
#include <linux/spi/spidev.h>
#include <unistd.h>
#include <wiringPiSPI.h>
#include <wiringPi.h>
//designates the speed and channel for the SPI transfer
	int init_spi() {
		int value;
		int speed = 500000;

		value = wiringPiSPISetup(0, speed);
		return(value);	
	}
//does a 3-byte transfer and calculates a datum from the response
	int transfer(void) {
		unsigned char data_temp[3];
		data_temp[0]=0x01;
		data_temp[1]=0x80;
		data_temp[2]=0x00;
		wiringPiSPIDataRW(0, data_temp, 3);
		//printf("%x,%x,%x\n",data_temp[0], data_temp[1], data_temp[2]);
		int response = ((data_temp[1]&3)*256) + data_temp[2];
		return(response);
	}
	int main(void) {
		int response;
		int value;
		value = init_spi();
		if (value == -1) {
			printf("SPI initialization unsuccesful");
			return(0);
		}
		int i = 1;
		while (i == 1) {
			response = transfer();
			usleep(250000);
			printf("%d\n", response);
		}
	}
