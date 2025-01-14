#!/usr/bin/python3

import requests, json, sys, time, os, html

#call parameters
ChargePoint = str(sys.argv[1]) 
code        = str(sys.argv[2]) 

#Debug       = int(os.environ.get('debug'))
Debug       = 0

moddir = '/var/www/html/openWB/modules/soc_eq/'


def printDebug(message, level):
    htmlmsg = html.escape(message)
    if level <= Debug:
        print("<p>" + htmlmsg + "</p>")


def printHtml(message):
    htmlmsg = html.escape(message)
    print("<p>" + htmlmsg + "</p>")

print("<html>")

client_id = ""
client_secret = ""
callback = ""

#get last Character to identify the Chargepoint
ChargePoint = ChargePoint[-1]

#get SoC module config from openWB cofig
fd = open('/var/www/html/openWB/openwb.conf','r')
for line in fd:
  try: 
    printDebug("owb Conf: " + line,2 )
    (key, val) = line.rstrip().split("=")
    if key == "debug":
        Debug = int(val)
    if key == "soc_eq_client_id_lp" + str(ChargePoint):
      printDebug("Found Client ID: " + val ,1)
      client_id = val
    if key == "soc_eq_client_secret_lp" + str(ChargePoint):
      printDebug("Found Client Secret: " + val ,1)
      client_secret = val
    if key == "soc_eq_cb_lp" + str(ChargePoint):
      printDebug("Found callback URL: " + val ,1)
      callback = val.replace("'","")
  except:
    
    val = ""

fd.close()

tok_url  = "https://id.mercedes-benz.com/as/token.oauth2"

data = {'grant_type': 'authorization_code', 'code': str(code), 'redirect_uri': callback}
#call API to get Access/Refresh tokens
act = requests.post(tok_url, data=data, verify=True, allow_redirects=False, auth=(client_id, client_secret))

printDebug(act.url,1)

if act.status_code == 200:
  #valid Response
  toks = json.loads(act.text)
  access_token = toks['access_token']
  refresh_token = toks['refresh_token']
  expires_in = int(time.time())

	#write tokens to files

  fd = open(moddir + 'soc_eq_acc_lp' + str(ChargePoint),'w')
  json.dump({'expires_in' : expires_in, 'refresh_token' : refresh_token, 'access_token' : access_token}, fd)
  fd.close()

if act.status_code == 200:
    printHtml( "Anmeldung erfolgreich!" )
    print( "<a href=""javascript:window.close()"">Sie k&ouml;nnen das Fenster schlie&szlig;en.</a>" )
else: 
    printHtml("Anmeldung Fehlgeschlagen Code: " + str(act.status_code) + " " + act.text)
print("</html>")
