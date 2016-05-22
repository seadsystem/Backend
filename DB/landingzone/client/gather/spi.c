// +build arm
#include "spi.h"

sample sample_data(int frequency) {
    return (sample) { .first = frequency, .second = frequency + 1, .third = frequency + 2 };
}
