# main.py -- put your code here!
# pyb module already imported
from machine import Pin, SPI
import max7219
import dcf77

# Using SPI 2 for easy PIN wiring
# clk : SCK PB13
# din : MOSI PB15
spi = SPI(2, baudrate=10000000)

# Use a single 4x 8x8 matrix (32x8) pixels
screen = max7219.Max7219(32, 8, spi, Pin('D7'))

# Adjust screen brightness
#  0: min
# 15: MAX
screen.brightness(0)

# Clear screen
screen.fill(0)
screen.show()

led = pyb.LED(1)
dcf = dcf77.dcf77(Pin('D4'))
rtc = pyb.RTC()

# Cutstom irq handler
def handler():
    ''' Resync RTC every time a successful DCF frame is decoded
    '''
    dcf_datetime = dcf.get_DateTime()
    rtc.datetime(dcf_datetime)

# Set IRQ every minute for dcf signal
dcf.irq([dcf.IRQ_MINUTE], handler)

# Starting receiving and decoding
#dcf.start()

# Wait for valid signal
#while not dcf.get_Infos()['Valid']:
#    pass

# Datetime structure
# [4] : H
# [5] : min.
# [6] : sec.
# Initializing loop
prev_sec = 0

# Loop forever !
while (True):
    sec = rtc.datetime()[6]
    if (sec != prev_sec):
        sec_txt = '{0:0=2d}'.format(sec)
        screen.fill(0)
        screen.text(sec_txt, 8, 0, 1)
        screen.show()
        if sec in (50, 55, 56, 57, 58, 59):
            led.on()
            pyb.delay(200)
            led.off()
            prev_sec = sec
        elif sec == 0:
            led.on()
            pyb.delay(400)
            led.off()
        else:
            pyb.delay(10)
    else:
        pyb.delay(10)
