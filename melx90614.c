//fordit:  gcc mlx90614_query.c -o mlx90614_query -l bcm2835
#include <stdio.h>
#include "bcm2835.h"
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>
#define AVG 1   //averaging samples
#define LOGTIME 10  //loging period

int main(int argc, char **argv)
{
    unsigned char buf[6];
    unsigned char i,reg;
    double temp=0,calc=0, skytemp,atemp;
    FILE *flog;
    flog=fopen("mlxlog.csv", "a");
    bcm2835_init();
    bcm2835_i2c_begin();
    bcm2835_i2c_set_baudrate(25000);
    // set address
    bcm2835_i2c_setSlaveAddress(0x5a);

    printf("\nOk, your device is working!!\n");

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    calc=0;
    reg=7;

    for(i=0;i<AVG;i++){
        bcm2835_i2c_begin();
        bcm2835_i2c_write (&reg, 1);
        bcm2835_i2c_read_register_rs(&reg,&buf[0],3);
        temp = (double) (((buf[1]) << 8) + buf[0]);
        temp = (temp * 0.02)-0.01;
        temp = temp - 273.15;
        calc+=temp;
        sleep(1);
    }

    skytemp=calc/AVG;
    calc=0;
    reg=6;

    for(i=0;i<AVG;i++){
        bcm2835_i2c_begin();
        bcm2835_i2c_write (&reg, 1);
        bcm2835_i2c_read_register_rs(&reg,&buf[0],3);
        temp = (double) (((buf[1]) << 8) + buf[0]);
        temp = (temp * 0.02)-0.01;
        temp = temp - 273.15;
        calc+=temp;
        sleep(1);
    }

    atemp=calc/AVG;

    printf("|{\"time\":{\"month\":\"%02d\",\"day\":\"%02d\",\"hour\":\"%02d\",\"min\":\"%02d\",\"sec\":\"%02d\"},\"data\":{\"t_ambi\":\"%04.2f\",\"t_obj\":\"%04.2f\"}}|\n", tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec,atemp,skytemp);

    fprintf(flog,"%04d-%02d-%02d %02d:%02d:%02d,%04.2f,%04.02f\n",tm.tm_year+1900, tm.tm_mon +1, tm.tm_mday,tm.tm_hour, tm.tm_min, tm.tm_sec,atemp,skytemp);

    fflush(flog);
    sleep(LOGTIME-(2*AVG));

    printf("[done]\n");

    return 0;
}

