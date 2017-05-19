#define _BSD_SOURCE
#include <bcm2835.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <math.h>
#include "csvparser.h"
#include <time.h>
#include "fft_analysis.h"

gsl_matrix_complex *compute_fft(int *points, int length) { //length should be specified as length = log2(FFT_length)
    unsigned t[2];
    struct GPU_FFT_COMPLEX *dataIn,*dataOut;
    struct GPU_FFT *fftinfo;

    int mb = mbox_open();
    gpu_fft_prepare(mb,length,GPU_FFT_FWD,1,&fftinfo);

    dataIn = fftinfo->in;
    dataOut = fftinfo->out;

    // Fill the fft data input array with signal
    int i;
    int FFT_length = 1 << length;
    for (i = 0; i < FFT_length; i++) {
	dataIn[i].re = points[i];
	dataIn[i].im = 0;
    } 

    usleep(1); // Yield to OS
    clock_t t1 = clock();
    gpu_fft_execute(fftinfo);
    clock_t t2 = clock();
    float diff = (1000000*(float)(t2 - t1) / CLOCKS_PER_SEC ); 
    //syslog(LOG_INFO,"Computed FFT of length %d in %f microseconds\n",FFT_length,diff);

    gsl_matrix_complex *matrix = gsl_matrix_complex_alloc(FFT_length,1); //Initialize complex fft vector 
    // Fill it with complex values
    for (i = 0; i < FFT_length; i++) {
       gsl_complex complex = gsl_complex_rect(dataOut[i].re,dataOut[i].im); 
       gsl_matrix_complex_set(matrix, i, 0,complex); //Fill matrix rows
    }
    gpu_fft_release(fftinfo);
    mbox_close(mb);
    return matrix;
}


void apply_flattop_window(int *points, int length)
{
	double a0 = 0.21557895;
	double a1 = 0.41663158;
	double a2 = 0.277263158;
	double a3 = 0.083578947;
	double a4 = 0.006947368;
	double pi = 3.1415926536;

	for (int i = 0; i < length; i++) 
	{
		double fw = (pi*i)/(length-1);
		double coefficient = a0 - a1*cos(2*fw)+a2*cos(4*fw)-a3*cos(6*fw)+a4*cos(8*fw); 
		points[i] = (int)(points[i] * coefficient);
	}
}

/*
scale_matrix function

matrix - comlex fft matrix to scale

This function scales matrix by it's size.

I use it to normalize fft vector.
*/
void scale_matrix(gsl_matrix_complex *matrix) {
     size_t size = matrix->size1;
     double scale = 1.0/size;
     gsl_complex complex_scale = gsl_complex_rect(scale,0); // This is just a scale represented by a complex number
     gsl_matrix_complex_scale(matrix,complex_scale); //Scale matrix by the length of the signal
}

/*
abs_matrix function

matrix - comlex fft matrix

This function takes an absolute valus of the complex matrix and returns a real matrix as a result.

*/
gsl_matrix *abs_matrix(gsl_matrix_complex *matrix) {
     size_t size = matrix->size1;
     gsl_matrix *absolute = gsl_matrix_alloc(size,1);
     for (int i = 0; i < size; i++) {
         gsl_complex complex = gsl_matrix_complex_get(matrix,i,0);
	 double abs = gsl_complex_abs(complex);
	 gsl_matrix_set(absolute,i,0,abs);
     }
     return absolute;
}

/*
half_matrix function

matrix - real values matrix

This function "chops" matrix in half to get the positive frequency spectrum.
*/
gsl_matrix *half_matrix(gsl_matrix *matrix) {
     size_t size = matrix->size1;
     size_t half_size = (size / 2)+1;
     gsl_matrix *half = gsl_matrix_alloc(half_size,1); //Take only half of the absolute of ff
     for (int i = 0; i < half_size; i++) {
         double value = gsl_matrix_get(matrix,i,0);
	 gsl_matrix_set(half,i,0,value);
     }
     return half;
}

/*
save_waveform_to_file function

data - signal
length - signal length
filename - name of the file to be saved to

Saves the signal to the file.
*/
void save_waveform_to_file(int *data, int length, char *filename) {
    FILE *f = fopen(filename,"a");
    //syslog(LOG_INFO,"Length: %d\n",length);
    for (int i = 0; i < length; i++) {
	fprintf(f,"%d,\n",data[i]);
    }
    fclose(f);
}

/*
print_result_to_file function

result - vector
filename - name of the file to be saved to

Saves the vector to the file.
*/
void print_result_to_file(gsl_matrix *result, char *filename) {
        FILE *f = fopen(filename,"w");
	int size = result->size1;
	for (int i = 0; i < size; i++) {
            double value = gsl_matrix_get(result,i,0);
	    fprintf(f,"%d,\n",value);
	}
	fclose(f);
}

/*
print_fft_to_file function

result - complex fft vector

Saves the vector to the file.
*/
void print_fft_to_file(gsl_matrix_complex *result) {
        FILE *real = fopen("real.csv","w");
        FILE *imag = fopen("imag.csv","w");

	int size = result->size1;
	for (int i = 0; i < size; i++) {
            gsl_complex value = gsl_matrix_complex_get(result,i,0);
	    fprintf(real,"%f,\n",value.dat[0]);
	    fprintf(imag,"%f,\n",value.dat[1]);
	}
	fclose(real);
	fclose(imag);
}

void display_harmonics(gsl_matrix *fft_vector) {
	double value_60 = gsl_matrix_get(fft_vector,60,0);
	double amplitude = value_60 * (3.72/4096);
	//syslog(LOG_INFO,"Amplitude of 60Hz is: %f\n",amplitude);
}

/*
extract_50_harmonics function

fft_vector - complex fft vector

Exracts 50 fundamental hormonics
60,120,180, etc

Returns the harmonics array of size 50.
*/
int *extract_50_harmonics(gsl_matrix *fft_vector, int frequency, int length) {
	int *harmonics = (int *)malloc(sizeof(int)*60);;
	int factor = (int)(60.0 *  (float)length / (float)frequency);

	for (int i = 1; i < 51; i++) {
		double max = 0;
		for (int j = -5; j < 5; j++)
		{
			double value = gsl_matrix_get(fft_vector,i*factor+j,0);
			if (value > max)
			{
				max = value;
			}
		}
		harmonics[i-1] = (int)max;
	}
	return harmonics;
}

/*
perform_fft_analysis function

points - signal

performs fft analysis
*/
int *perform_fft_analysis(int *points, int frequency) {
    clock_t t1 = clock();
    int length = 1 << WINDOW_SIZE; // Sampling frequency
    apply_flattop_window(points,length);
    gsl_matrix_complex *fft_matrix = compute_fft(points,WINDOW_SIZE); // performs fft transformation of the signal
    scale_matrix(fft_matrix); // normalizes the resulting fft vector
    gsl_matrix *absolute = abs_matrix(fft_matrix); // takes an absolute value of the fft vector
    gsl_matrix *half = half_matrix(absolute); // and chops of the negative part.
    gsl_matrix_scale(half,2); // Scales by two
    clock_t t2 = clock();
    float diff = ((float)(t2 - t1) / CLOCKS_PER_SEC ); 
    //syslog(LOG_INFO,"FFT analysis took: %f seconds\n",diff);

    int *harmonics = extract_50_harmonics(half, frequency, length); // extracts harmonics
    //save_waveform_to_file(harmonics,1,"harmonics.csv");
    for (int i = 0; i < 50; i++)
    {
	    printf("peak at %dHz is %d\n",(i+1)*60,harmonics[i]);
    }

    // frees the resources.
    gsl_matrix_free(half);
    gsl_matrix_free(absolute);
    gsl_matrix_complex_free(fft_matrix);
    return harmonics;
}

/*
rms function

signal - signal
frequency - signal frequency

Computes rms value of the given signal.
*/
int rms(int *signal, int frequency) {
    clock_t t1 = clock();
    int sum = 0; 
    for (int i = 0; i < frequency; i++) {
       int data = signal[i];
	sum += data*data; 
    }
    sum /= frequency;
    double root = sqrt((double)sum); 
    clock_t t2 = clock();
    float diff = ((float)(t2 - t1) / CLOCKS_PER_SEC ); 
    //syslog(LOG_INFO,"RMS analysis took: %f seconds\n",diff);
    //syslog(LOG_INFO,"RMS value: %f\n",root);
    return (int)root;
}

sample *sample_waveform(int *channels)
{
    if (init()) {
        //syslog(LOG_INFO,"Init failed.\n");
    } else {
	   //syslog(LOG_INFO,"Succesfull init of bcm2835.\n");
    }
    //syslog(LOG_INFO,"Starting bcm2835 setup...\n");
    setup();
    //syslog(LOG_INFO,"bcm2835 setup finished.\n");

    int frequency = 1 << WINDOW_SIZE;

    int channelss[] = {0,1,1,1,1,1,0,1};

    for (int i = 0; i < 60; i++)
    {
     sample *s = sample_data(&channelss,frequency);
	perform_fft_analysis(s->channel_data[2], s->frequency);

    //save_waveform_to_file(s->channel_data[1], 1*8192, "ch1_waveform.csv");
    }


    /*
	int i = 0;
    CsvParser *csvparser = CsvParser_new("ch1_waveform_lamp_20secs.csv", ",", 0);
    CsvRow *row;
    int rowCount = 0;
    int data[300000];
    while (row = CsvParser_getRow(csvparser) ) {
	     if (rowCount > 30000) { break;}
	     char **rowFields = CsvParser_getFields(row);
		data[rowCount] = atoi(rowFields[0]);
		CsvParser_destroy_row(row);
		rowCount++;
	}

    int newData[8192];

    for (int i = 0; i < 8192; i++)
    {
	    newData[i] = data[i+8192*1];
    }
    perform_fft_analysis(&newData);
    */
    return NULL;

}

harmonics_sample *sample_harmonics(int *channels) {
    openlog("goclient", LOG_PID|LOG_NDELAY, LOG_DAEMON);
    if (init()) {
        //syslog(LOG_INFO,"Init failed.\n");
    } else {
	   //syslog(LOG_INFO,"Succesfull init of bcm2835.\n");
    }
    //syslog(LOG_INFO,"Starting bcm2835 setup...\n");
    setup();
    //syslog(LOG_INFO,"bcm2835 setup finished.\n");

    int frequency = 1 << WINDOW_SIZE;
    sample *s = sample_data(channels,frequency);
    //syslog(LOG_INFO,"Ending spi connection ...\n");
    end();

    harmonics_sample *hs = malloc(sizeof(harmonics_sample));
    for (int i = 0; i < 8; i++)
    {
	    if (channels[i]) 
	    {
	         int *fft = perform_fft_analysis(s->channel_data[i], s->frequency);
		    for (int j = i*50; j < i*50 + 50; j++)
		    {
		        hs->harmonics[j] = fft[j - i*50];
	         }
		    free(fft);
	    }
    } 

    sample_deallocate(s);
    closelog();


    return hs;
}

void deallocate(harmonics_sample *sample)
{
	free(sample);
}
