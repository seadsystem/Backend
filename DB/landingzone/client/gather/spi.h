// +build arm
#ifndef _SPI_H_   /* Include guard */
#define _SPI_H_

typedef struct {
   int first;
   int second;
   int third;
} sample;

sample sample_data(int frequency);

#endif // _SPI_H_
