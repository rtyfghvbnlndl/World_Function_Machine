from microdot import Microdot
import network, time

try_connect = False

def do_connect(wlan,ssid, passwd):
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        if not wlan or not passwd:
            return False
        wlan.connect(ssid, passwd)
        for i in range(30):
            if wlan.isconnected():
                return True
            else:
                time.sleep(0.5)
        else:
            return False

def connet_by_webserver(wlan):
    ap = network.WLAN(network.AP_IF) 
    ap.config(essid='ESP32_AP')
    ap.active(True)

    app = Microdot()

    @app.route('', methods=['GET', 'POST'])
    def index(req):
        global try_connect
        ssid, passwd = None, None
        if req.method == 'POST':
            ssid = req.form.get('ssid')
            passwd = req.form.get('passwd')
            with open("db.txt", "w+", encoding="utf-8",) as f:
                f.write("wlan.connect('%s', '%s')", (ssid,passwd))
            print('connect to ',ssid,passwd)

            if do_connect(wlan,ssid,passwd):
                req.app.shutdown()
                return 'success'
            else:
                try_connect=True
    
        with open('index.html', mode='r', encoding='utf-8') as html:
            if not try_connect:
                status = ' '
            else:
                status = '<div class="fail">Wifi Connection Failed.</div>'
            return f'%s{status}' % html.read(), 200, {'Content-Type': 'text/html'}
        
    @app.route('close', methods=['GET', 'POST'])
    def close(req):
        req.app.shutdown()
        if wlan.isconnected():
            return 'Close server. Wifi is connected.'
        else:
            return 'Close server. Wifi is not connected.'

    app.run(port=80)
    return ap
