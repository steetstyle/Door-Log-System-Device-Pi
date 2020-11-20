/*
 * wiegand.c
 *
 * Wiegand 26 RFID Reader for Orange/Raspberry Pi, get the RFID readings key code, into a Domoticz variable (string)
 *
 *
 * Updated by ILoveIOT 03-04-2019
 *
 *
 * By Kyle Mallory All rights reserved.
 * 12/01/2013
 *
 *
 * Based on previous code by Daniel Smith (www.pagemac.com) and Ben Kent (www.pidoorman.com)
 * Depends on the wiringPi library by Gordon Henterson: https://projects.drogon.net/raspberry-pi/wiringpi/
 *
 *
 * The Wiegand interface has two data lines, DATA0 and DATA1.  These lines are normall held
 * high at 5V.  When a 0 is sent, DATA0 drops to 0V for a few µs.  When a 1 is sent, DATA1 drops
 * to 0V for a few µs. There are a few ms between the pulses.
 *
 *                                      *************
 *                                      * IMPORTANT *
 *                                      *************
 *
 * The Raspberry Pi GPIO pins are 3.3V, NOT 5V. Please take appropriate precautions to bring the
 * 5V Data 0 and Data 1 voltages down. I used a 330 ohm resistor and 3V3 Zenner diode for each
 * connection, or use level shifters like me. FAILURE TO DO THIS WILL PROBABLY BLOW UP THE RASPBERRY PI!
 *
 *
 * For compiling use   : cd /root/scripts/gpio/ ; gcc -o wiegand -lpthread -lwiringPi -lrt wiegand.c
 * For console use     : /root/scripts/gpio/wiegand
 * For background use  : /root/scripts/gpio/wiegand &
 *
 *
 * 1. Create a variable in Domoticz to store the value, type variable is a string, mine looks like "KE934802"
 * 2. Change the IP address (192.168.8.189) + the name of the variable (RFIDDeur)
 * 3. Change the used PINS, I use GPIO 11 and GPIO 21 (#define D0_PIN 11 and #define D1_PIN 21)
 * 4. Optional : change the console outputs below
 * 5. Optional : You can use Domoticz blocky to trigger a event with the key code
 *
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <wiringPi.h>
#include <time.h>
#include <unistd.h>
#include <memory.h>
#include <string.h>
#include <assert.h>



// gpio readall | 26 	   | 1 | ALT2 | GPIO.11  | 11  | 21  |
//				| Physical | V | Mode | Name     | wPi | BCM |

#define D0_PIN 11


// gpio readall |   7 |  21 |  GPIO.21 | ALT2 | 1 | 29 |
//				| BCM | wPi |   Name   | Mode | V | Physical |

#define D1_PIN 21





#define WIEGANDMAXDATA 32
#define WIEGANDTIMEOUT 3000000

static unsigned char __wiegandData[WIEGANDMAXDATA];    // can capture upto 32 bytes of data -- FIXME: Make this dynamically allocated in init?
static unsigned long __wiegandBitCount;                // number of bits currently captured
static struct timespec __wiegandBitTime;               // timestamp of the last bit received (used for timeouts)

void data0Pulse(void) {
    if (__wiegandBitCount / 8 < WIEGANDMAXDATA) {
        __wiegandData[__wiegandBitCount / 8] <<= 1;
        __wiegandBitCount++;
    }
    clock_gettime(CLOCK_MONOTONIC, &__wiegandBitTime);
}

void data1Pulse(void) {
    if (__wiegandBitCount / 8 < WIEGANDMAXDATA) {
        __wiegandData[__wiegandBitCount / 8] <<= 1;
        __wiegandData[__wiegandBitCount / 8] |= 1;
        __wiegandBitCount++;
    }
    clock_gettime(CLOCK_MONOTONIC, &__wiegandBitTime);
}

int wiegandInit(int d0pin, int d1pin) {
    // Setup wiringPi
    wiringPiSetup() ;
    pinMode(d0pin, INPUT);
    pinMode(d1pin, INPUT);

    wiringPiISR(d0pin, INT_EDGE_FALLING, data0Pulse);
    wiringPiISR(d1pin, INT_EDGE_FALLING, data1Pulse);
}

void wiegandReset() {
    memset((void *)__wiegandData, 0, WIEGANDMAXDATA);
    __wiegandBitCount = 0;
}

int wiegandGetPendingBitCount() {
    struct timespec now, delta;
    clock_gettime(CLOCK_MONOTONIC, &now);
    delta.tv_sec = now.tv_sec - __wiegandBitTime.tv_sec;
    delta.tv_nsec = now.tv_nsec - __wiegandBitTime.tv_nsec;

    if ((delta.tv_sec > 1) || (delta.tv_nsec > WIEGANDTIMEOUT))
        return __wiegandBitCount;

    return 0;
}

/*
 * wiegandReadData is a simple, non-blocking method to retrieve the last code
 * processed by the API.
 * data : is a pointer to a block of memory where the decoded data will be stored.
 * dataMaxLen : is the maximum number of -bytes- that can be read and stored in data.
 * Result : returns the number of -bits- in the current message, 0 if there is no
 * data available to be read, or -1 if there was an error.
 * Notes : this function clears the read data when called. On subsequent calls,
 * without subsequent data, this will return 0.
 */
 
int wiegandReadData(void* data, int dataMaxLen) {
    if (wiegandGetPendingBitCount() > 0) {
        int bitCount = __wiegandBitCount;
        int byteCount = (__wiegandBitCount / 8) + 1;
        memcpy(data, (void *)__wiegandData, ((byteCount > dataMaxLen) ? dataMaxLen : byteCount));

        wiegandReset();
        return bitCount;
    }
    return 0;
}

void main(void) {
    int i;

    wiegandInit(D0_PIN, D1_PIN);

    while(1) {
        
		int bitLen = wiegandGetPendingBitCount();
        if (bitLen == 0) {
            usleep(5000);
        
		} else {
            
			char data[100];
            bitLen = wiegandReadData((void *)data, 100);
            int bytes = bitLen / 8 + 1;

			// because we get the data from a loop I had to make a virtual file and store the value's from the loop into file and into char "buf"
			char *buf;
			size_t size;
			FILE *fp = open_memstream(&buf, &size);
			assert(fp);
			
			// Doing the loop, we get 2 value's at the same time, 4 times, print them in a file, in 1 code.
			for (i = 0; i < bytes; i++) {
			fprintf(fp, "%02X", (int)data[i]);
			}
			
			// Close the virtual file
			fclose(fp);
			
			// Making the string with the RFID data for Domoticz
			char str1[] = "/bin/bash -c 'curl -i -s \"http://192.168.8.189:8080/json.htm?type=command&param=updateuservariable&vname=RFIDDeur&vtype=2&vvalue=";
			
			// Get the value from "buf" the keycard code, and put it in a string
			char str2[25]; //size of the number
			sprintf(str2, "%s", buf);

			
			// Uncomment one off the lines if you wanna see output or not from domoticz
			char str3[] = "\"' > /dev/null 2>&1";	
			//char str3[] = "\"'";			

			
			// Put the strings together
			strcat(str2,str3);
			strcat(str1,str2);

			// Sending data to Domoticz, in the already prepared string
			system(str1);
			
			
			// Uncomment if you wanna see the line sending to Domoticz
			//puts(str1);  	
		
			
			// Uncomment if you wanna see the output of "buf" on the console
			//puts(buf);
			free(buf);		
			
        }
    }
}