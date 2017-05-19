#ifndef _SPI_H_   /* Include guard */
#define _SPI_H_

#ifdef WINDOW_SIZE 
#undef WINDOW_SIZE 
#endif
#define WINDOW_SIZE 13

#ifdef SIZE_LIMIT 
#undef SIZE_LIMIT 
#endif
#define SIZE_LIMIT 20 

#include <bcm2835.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

typedef struct {
   int * channel_data[8];
   int frequency;
} sample;

int init();
sample *sample_data(int *channels,int frequency);
void sample_deallocate(sample *s);
int sample_channel(uint8_t channel); 
void setup();
void end();
#endif // _SPI_H_
