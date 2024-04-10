# main.py -- put your code here!
# pyb and machine module already imported
import dcf77

led = pyb.LED(1)
dcf = dcf77.dcf77(machine.Pin('D4'))
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
dcf.start()

# Wait for valid signal
while not dcf.get_Infos()['Valid']:
    pass

# Initializing loop
prev_sec = 0

# Loop forever !
while (True):
    sec = rtc.datetime()[6]
    if (sec != prev_sec):
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

