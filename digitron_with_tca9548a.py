from time import sleep
import ssd1306
class digitron1(object):
    def __init__(self,lcd):
        self.px = 0
        self.pp = 1
        self.log = [0,0,0,0,0,0,0,0]
        self.lcd = lcd

        lcd.writeto(0x70, b'\xff')
        self.display = ssd1306.SSD1306_I2C(128, 32, lcd)
        self.map=(b'\x01',b'\x02',b'\x04',b'\x08',b'\x10',b'\x20',b'\x40',b'\x80')
        self.nab= a={' ':[],'-':[4],'0':[1,2,3,5,6,7],'1':[8,9],'2':[7,6,4,2,1],'3':[7,6,4,3,1],'4':[4,5,6,3],'5':[7,5,4,3,1],'6':[1,2,3,4,5,7],'7':[7,6,3],'8':[1,2,3,4,5,6,7],'9':[1,6,3,4,5,7],'a':[2,5,7,4,6,3],'b':[5,4,2,1,3],'c':[7,5,2,1],'d':[6,3,1,4,2],'e':[7,5,4,2,1],'f':[7,5,4,2],'g':[7,5,2,1,3],'h':[3,2,4,5,6],'i':[7,6,3,1],'j':[6,3,1],'k':[7,5,4,2,3],'l':[5,2,1],'m':[2,5,7,6,3],'n':[2,4,3],'o':[1,2,4,3],'p':[7,6,4,5,2],'q':[7,5,6,4,3],'r':[7,5,2],'s':[7,4,1],'t':[5,4,2,1],'u':[5,4,1,3,6],'v':[2,1,3],'w':[5,4,6,3,1,2],'x':[5,4,3],'y':[5,4,6,3,1],'z':[6,4,2,1]}

#自检动画
    def start(self):
        for i in range(8):
            self.lcd.writeto(0x70, self.map[i])
            self.display.fill(0)
            self.display.text('Screen %i' % i, 30, 15)
            sleep(1)
        
        self.lcd.writeto(0x70, b'\xff')
        for i in (1,2,5,7,6,3,1,2,5,7,6,3):
            self.display.fill(0)
            self.segment([i],0)
            self.display.show()
            sleep(0.2)

    def rect(self,x0,y0,x1,y1):
        for x in range(x0-1,x1):
            for y in range (y0-1,y1):
                self.display.pixel(x,y,1)
##防烧屏,每调用一次偏移值self.px会改变
    def move(self):
        if self.px==14:
            self.pp=-1
        elif self.px==-14:
            self.pp=1
        self.px+=self.pp
##数码管模拟
    def segment(self,lis,px):
        for item in lis:
            if item==1:
                self.rect(16+px, 1, 22+px, 32)
            elif item==2:
                self.rect(16+px, 1, 64+px, 6)
            elif item==3:
                self.rect(16+px, 26, 64+px, 32)
            elif item==4:
                self.rect(61+px, 1, 67+px, 32)
            elif item==5:
                self.rect(64+px, 1, 112+px, 6)
            elif item==6:
                self.rect(64+px, 26, 112+px, 64)
            elif item==7:
                self.rect(106+px, 1, 112+px, 64)
            elif item==8:
                self.rect(16+px, 13, 64+px, 19)
            elif item==9:
                self.rect(64+px, 13, 112+px, 19)
    #数字字母
    def show(self,channel_code,num_ab):
        self.lcd.writeto(0x70,channel_code)
        self.display.fill(0)
        self.segment(self.nab[str(num_ab).lower()],self.px)
        self.display.show()
    #由当前数字一个个数增加到目标数字的动画
    def effNum(self,channel_number_dict):
        done=True
        while not done:
            done=True
            for c,n in channel_number_dict.items():
                if self.log[c]!=n:
                    if self.log[c]==9:
                        self.log[c]=0
                    else:
                        self.log[c]+=1
                    self.show(self.map[c],self.log[c])
                    done=False


##4x4像素模拟
    def pixel(self,lis,px):
        for item in lis:
            y=item//4
            x=item%4
            self.rect(24*x+16+px,8*y,24*x+40+px,8*y+8)
    def pixelEff(self):
        for i in range(16):
            self.display.fill(0)
            self.pixel([i],0)
            self.display.show()
            sleep(0.2)
    #符号
    def symbol(self,channel_code,sym):
        self.lcd.writeto(0x70,channel_code)
        self.display.fill(0)
        a={':':[8,4],';':[11,7],'%':[15,10,5,0,3,12],'!':[7,11,6,10,4,5],"(":[3,7,11,15,2,1,0,4,8,12],')':[3,7,11,15,14,13,12,8,4,0],'.':[12]}
        self.pixel(a[sym],self.px)
        self.display.show()
    
    def showlong(self,content):
        for i in range(8):
            try:
                self.show(self.map[i],content[i])
            except:pass
            try:
                self.symbol(self.map[i],content[i])
            except:pass