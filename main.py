import digitron_with_tca9548a as digitron
import bh1750,BMP085,dht,ds1302
from machine import I2C,Pin,freq,SoftI2C,RTC
import time
import random
import network,ntptime

key1 = Pin(32,Pin.IN,pull=Pin.PULL_UP)
key2 = Pin(16,Pin.IN,pull=Pin.PULL_UP)
key3 = Pin(17,Pin.IN,pull=Pin.PULL_UP)

lcd = I2C(1,scl=Pin(25), sda=Pin(26), freq=400000)
lux = SoftI2C(scl=Pin(22), sda=Pin(23), freq=100000)
press = SoftI2C(scl=Pin(18), sda=Pin(19), freq=100000)
rtc = RTC()

lcdC = digitron.digitron1(lcd)
try:
    dht11 = dht.DHT11(Pin(4,Pin.IN,pull=Pin.PULL_UP))
    dht11.measure()
except:
    dht11=False
for i in range(5):
    if bh1750.sample(lux):
        luxC = True
        break
    time.sleep(0.2)
else:
    luxC=False
try:
    pressC = BMP085.BMP085(press)
    pressC.oversample = 2
    pressC.sealevel = 101325
except OSError:
    pressC = False
ds = ds1302.DS1302(Pin(27),Pin(13),Pin(5))

#功能——浏览器配网
def do_network():
    global init, counter
    if not init:
        lcd.writeto(0x70, b'\xff')
        lcdC.display.fill(0)
        lcdC.display.text('Connect to wifi?',0,8)
        lcdC.display.text('Press KEY2!',0,16)
        if wlan.isconnected():
            lcdC.display.text('WIFI Connected.',0,0)
        else:
            lcdC.display.text('WIFI NOT Connected.',0,0)
        lcdC.display.show()
        init=True
    else:
        time.sleep(0.2)
        if not key2.value():
            while not key2.value():
                pass
                
            import connect_wifi_by_web

            lcdC.display.fill(0)
            lcdC.display.text('Conect to:.',0,0)
            lcdC.display.text('ESP32_AP:',0,8)
            lcdC.display.text('Open webpage:',0,16)
            lcdC.display.text('192.168.4.1',0,24)
            lcdC.display.show()

            ap=connect_wifi_by_web.connet_by_webserver(wlan)
            ap.active(False)

            lcdC.display.fill(0)
            if wlan.isconnected():
                lcdC.display.text('DONE!',0,24)
            else:
                lcdC.display.text('FAIL!',0,24)
            lcdC.display.show()
    if counter==50:
        counter=0
        lcdC.move()
    else:
        counter+=1
#功能——时钟
def clock():
    global counter,clock_dot
    if key2.value()==0:
        while not key2.value():#阻塞
            pass
        counter=170
    if counter<170:
        try:
            lcdC.symbol(b'\x24', clock_dot[counter%2])
        except:pass
        try:
            hour=rtc.datetime()[4]
            lcdC.show(b'\x01', str(hour//10))
            lcdC.show(b'\x02', str(hour%10))
        except:pass
        try:
            minute=rtc.datetime()[5]
            lcdC.show(b'\x08', str(minute//10))
            lcdC.show(b'\x10', str(minute%10))
        except:pass
        try:
            second=rtc.datetime()[6]
            lcdC.show(b'\x40', str(second//10))
            lcdC.show(b'\x80', str(second%10))
            print(lcdC.pp,lcdC.px)
            time.sleep(0.1)
        except:pass
    elif counter<174 and (pressC or dht11):
        lcd.writeto(0x70, b'\xff')
        try:
            s = str(pressC.temperature)+'c'
        except not KeyboardInterrupt:
            try:
                s = dht11.measure()
            except not KeyboardInterrupt:
                s = 0
        print(s)
        while len(s)<8:
            s+=' '
        lcdC.showlong(s)
        time.sleep(1)

    elif counter<178 and pressC:
        lcd.writeto(0x70, b'\xff')
        try:
            s = str(pressC.pressure)+'hpa'
        except not KeyboardInterrupt:
            s = 0
        print(s)
        while len(s)<8:
            s+=' '
        lcdC.showlong(s)
        time.sleep(1)

    elif counter<182 and luxC:
        lcd.writeto(0x70, b'\xff')
        try:
            s = str(bh1750.sample(lux))+'lux'
        except not KeyboardInterrupt:
            s = 0
        print(s)
        while len(s)<8:
            s+=' '
        lcdC.showlong(s)
        time.sleep(1)
    
    elif counter<185 and dht11:
        try:
            dht11.measure()
        except:
            counter=185
        lcd.writeto(0x70, b'\xff')
        try:
            s = str(dht11.humidity())+'%'
        except not KeyboardInterrupt:
            s = 0
        print(s)
        while len(s)<8:
            s+=' '
        lcdC.showlong(s)
        time.sleep(1)
    else:
        counter=185
    print(counter)
    if counter>=185:
        counter=0
        lcdC.move()
    else:
        counter+=1
#功能——世界函数
def world_function():
    global counter,world_change_rate
    key3 = Pin(17,Pin.OUT,pull=Pin.PULL_UP,value=1)
    if counter%5==0:
        key3.value(0)
        time.sleep(0.05)
        en = random.randint(0,10)
        if en >8:
            world_change_rate+=random.randint(0,1000)/100000000
            for i in range(random.randrange(6)):
                lcdC.showlong(str(world_change_rate+random.randint(-100000000,100000000)/100000000))
            lcdC.showlong(str(world_change_rate))
        key3.value(1)
        
    time.sleep(1)

    if counter==20:
        counter=0
        lcdC.move()
    else:
        counter+=1
#功能——计时器
timer_power, timer_pause = False, False
time0, time1= None, None

def time_length(time_old):
    second=rtc.datetime()[6]-time_old[6]
    minute = rtc.datetime()[5]-time_old[5]
    hour=rtc.datetime()[4]-time_old[4]
    if second<0:
        second = 60+second
        minute -= 1
    if minute<0:
        minute = 60+minute
        hour -=1
    if hour<0:
        hour+=24
    elif hour>23:
        hour=0
    return hour, minute, second

def timer():
    global counter, timer_power, timer_pause, time0, time1
    
    print(counter, timer_power, timer_pause, time0)

    if not key3.value():
        while not key3.value():#阻塞
            pass
        timer_power = not timer_power
        if timer_power:#开始计时
            time0 = list(rtc.datetime())
        else:#结束计时
            time0 = None

    if not key2.value() and timer_power:
        while not key2.value():#阻塞
            pass
        timer_pause = not timer_pause
        if timer_pause:#暂停开始
            time1 = rtc.datetime()
        else:#暂停结束
            hour1, minute1, second1 = time_length(time1)
            time0[6]+=second1
            while time0[6]>=60:
                time0[6]-=60
                minute1+=1
            time0[5]+=minute1
            while time0[5]>=60:
                time0[5]-=60
                hour1+=1
            time0[4]+=hour1
            while time0[4]>=24:
                time0[4]-=24
                time0[2]+=1
        
    if not timer_power:#关闭状态
        lcdC.show(b'\xff',0)
    else:
        if timer_pause:#开启并暂停状态
            pass
        else:#只开启状态
            hour, minute, second = time_length(time0)
        
            try:
                lcdC.symbol(b'\x24', clock_dot[counter%2])
            except:pass
            try:
                lcdC.show(b'\x01', str(hour//10))
                lcdC.show(b'\x02', str(hour%10))
            except:pass
            try:
                lcdC.show(b'\x08', str(minute//10))
                lcdC.show(b'\x10', str(minute%10))
            except:pass
            try:
                lcdC.show(b'\x40', str(second//10))
                lcdC.show(b'\x80', str(second%10))
            except:pass
    time.sleep(0.1)
    if counter==40:
        counter=0
        lcdC.move()
    else:
        counter+=1
#变量
world_change_rate=random.randint(0,1000000)/100000000
counter=0
module = {}
mode=[timer, world_function, do_network, clock,]
lcdC.start()
mode_num=0
clock_dot=(';',':',)

lcd.writeto(0x70, b'\xff')
lcdC.display.fill(0)

key3 = Pin(17,Pin.OUT,value=1)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
#连wifi
if not wlan.isconnected():
    lcdC.display.text('wifi...',0,0)
    lcdC.display.show()
    try:
        with open('db.txt', 'r', encoding='utf-8',) as f:
            eval(f.read())
        #wlan.connect('openwrt', 'open1234')
        for i in range(25):
            if not wlan.isconnected():
                key3.value(0)
                time.sleep(0.2)
                key3.value(1)
            else:
                lcdC.display.text('done!',0,8)
                lcdC.display.show()
                module['wifi']=True
    except:pass

if not wlan.isconnected():
    module['wifi']=False
    print('timeout')
    lcdC.display.text('timeout',0,8)
    lcdC.display.show()

key3 = Pin(17,Pin.IN,pull=Pin.PULL_UP)
#对时
lcd.writeto(0x70, b'\xff')
if wlan.isconnected():  
    ntptime.NTP_DELTA = 3155644800
    ntptime.host = 'time.apple.com'
    for i in range(3):
        try:
            ntptime.settime()
            module['ntp']=True
            lcdC.display.text('ntp done!',0,16)
            lcdC.display.show()
            break
        except:
            continue
    else:
        lcdC.display.text('ntp fail...',0,16)
        lcdC.display.show()
        module['ntp']=False

module['ds1302']=True
if wlan.isconnected() and module['ntp']:
    try:
        ds.date_time((time.localtime()[0],time.localtime()[1],time.localtime()[2],time.localtime()[6],time.localtime()[3],time.localtime()[4],time.localtime()[5]))
        lcdC.display.text('rtc to ds1302 done!',0,24)
        lcdC.display.show()
    except:
        module['ds1302']=False
   
else:
    try:
        rtc.datetime((ds.year(), ds.month(), ds.day(), None, ds.hour(), ds.minute(), ds.second(), 0))
        lcdC.display.text('ds1302 to rtc done!',0,24)
        lcdC.display.show()
    except:
        module['ds1302']=False

if not module['ds1302']:
    if not wlan.isconnected():
        lcdC.display.text('WARNING: WRONG TIME',0,16)
    lcdC.display.text('ds1302 disconnected!',0,24)
    lcdC.display.show()
#模式切换
while True:
    if key1.value()==0:
        while not key1.value():#阻塞
            pass
        mode_num+=1
        init=False
        counter=0
        key3 = Pin(17,Pin.IN,pull=Pin.PULL_UP)

    if mode_num==len(mode):
        mode_num=0
    mode[mode_num]()