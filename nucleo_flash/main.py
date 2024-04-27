# main.py -- put your code here!
# pyb module already imported
import micropython
import asyncio
from machine import Pin, SPI
import max7219
import dcf77

# buffer for interrupt
micropython.alloc_emergency_exception_buf(100)

# asynchronous interrupt from RTC
ITRtcTSF = asyncio.ThreadSafeFlag()
# asynchronous interrupt from DCF
ITDcfTSF = asyncio.ThreadSafeFlag()

class Rtc(object):
    ''' RTC based on interrupts
    '''
    def __init__(self, rtc=None, timeout=10):
        self.rtc = rtc
        self.rtc.wakeup(timeout, self.cb)

    def cb(self, t):
        ''' RTC callback
            Datetime structure [4] : H.; [5] : min.; [6] : sec.
        '''
        global ITRtcTSF
        ITRtcTSF.set()

    def get_time(self):
        ''' Return RTC time
        '''
        return self.rtc.datetime()[4:7]

    def set_datetime(self, datetime):
        ''' Set RTC time
        '''
        return self.rtc.datetime(datetime)


class Dcf(object):
    ''' Dcf based on interrupts
    '''
    def __init__(self, dcf=None):
        self.dcf = dcf
        self.start()
        self.dcf.irq([dcf.IRQ_MINUTE], self.cb)

    def cb(self):
        ''' DCF callback
        '''
        global ITDcfTSF
        ITDcfTSF.set()

    def GETInfos(self):
        return self.dcf.get_Infos()

    def GETLastSignal(self):
        return self.dcf.get_LastSignal()

    def GETDateTime(self):
        return self.dcf.get_DateTime()

    def GETLastPulseLength(self):
        return self.dcf.last_pulse

    def start(self):
        ''' Start DCF
        '''
        self.dcf.start()

    def stop(self):
        ''' Stop DCF
        '''
        self.dcf.stop()


class MatrixDisp(object):
    ''' Display using MAX7219
    '''
    def __init__(self, spi=None, CSpin=None, Xdim=64, Ydim=8):
        self.screen = max7219.Max7219(Xdim, Ydim, spi, CSpin)
        self.clear()
        self.brightness(0)

    def clear(self):
        ''' Clearing display
        '''
        self.screen.fill(0)
        self.screen.show()

    def write(self, txt='', PosX=0, PosY=0):
        ''' Display string on screen
        '''
        self.screen.fill(0)
        self.screen.text(txt, PosX, PosY, 1)
        self.screen.show()

    def brightness(self, level):
        ''' Control screen brightness
            0: min; 15: MAX
        '''
        self.screen.brightness(level)


################
# Led Init
################
# led definition usefull for debug
led = pyb.LED(1)

################
# Matrix Display
################
# Using SPI 2 for easy PIN wiring on Nucleo 64
# and chip select PIN D7
screen = MatrixDisp(SPI(2, baudrate=10000000), Pin('D7'))

################
# RTC Init
################
rtc = Rtc(pyb.RTC())

################
# DCF77
################
dcf = Dcf(dcf77.dcf77(Pin('D4')))

prev_sec = -1
updating_display = False

async def DispUpdate():
    global prev_sec
    global updating_display
    updating_display = True
    h_, min_, sec_ = rtc.get_time()
    if sec_ != prev_sec:
        h_txt = '{0:0=2d}:{1:0=2d}:{2:0=2d}'.format(h_, min_, sec_)
        screen.write(h_txt)
        if sec_ in (50, 55, 56, 57, 58, 59):
            led.on()
            await asyncio.sleep_ms(200)
            led.off()
        elif sec_ == 0:
            led.on()
            await asyncio.sleep_ms(500)
            led.off()
        prev_sec = sec_
    updating_display = False

async def RTCResync():
    while True:
        await ITDcfTSF.wait()
        DCFdatetime = dcf.GETDateTime()
        rtc.set_datetime(DCFdatetime)
        print('Resync done', DCFdatetime)

async def main():
    asyncio.create_task(RTCResync())
    while True:
        await ITRtcTSF.wait()
        if updating_display == False:
            asyncio.create_task(DispUpdate())

asyncio.run(main())
