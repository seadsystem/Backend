#ifndef _FFT_ANALYSYS_H_ /*Include guard */
#define _FFT_ANALYSYS_H_

#include <string.h>
#include <syslog.h>
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_complex_math.h>
#include "mailbox.h"
#include "gpu_fft.h"
#include "spi.h"

typedef struct harmonics_sample {
	int harmonics[400];
} harmonics_sample;
gsl_matrix_complex *compute_fft(int *points, int length); 
int *perform_fft_analysis(int *points, int frequency);
harmonics_sample *sample_harmonics(int *channels);
sample *sample_waveform(int *channels);
void deallocate(harmonics_sample *sample);
#endif // _FFT_ANALYSYS_H_
