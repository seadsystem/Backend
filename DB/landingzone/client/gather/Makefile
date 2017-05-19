S = hex/shader_256.hex \
    hex/shader_512.hex \
    hex/shader_1k.hex \
    hex/shader_2k.hex \
    hex/shader_4k.hex \
    hex/shader_8k.hex \
    hex/shader_16k.hex \
    hex/shader_32k.hex \
    hex/shader_64k.hex \
    hex/shader_128k.hex \
    hex/shader_256k.hex \
    hex/shader_512k.hex \
    hex/shader_1024k.hex \
    hex/shader_2048k.hex \
    hex/shader_4096k.hex

C = main.c fft_analysis.c mailbox.c gpu_fft.c gpu_fft_base.c gpu_fft_twiddles.c gpu_fft_shaders.c spi.c csvparser.c

H = fft_analysis.h gpu_fft.h mailbox.h spi.h csvparser.h

F = -lrt -lm -ldl -lgsl -lgslcblas -lbcm2835

all:fft_sampling	

fft_sampling:	$(S) $(C) $(H)
	gcc -g -std=c11 -o fft_sampling $(H) $(C) $(F) 
clean:
	rm -f *.bin
