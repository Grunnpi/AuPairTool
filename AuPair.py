import requests
import argparse
from bs4 import BeautifulSoup
from requests.utils import requote_uri
import csv
import os
from datetime import datetime
import urllib.parse
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import telegram

import gspread
from oauth2client.service_account import ServiceAccountCredentials

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

proxies = {}
sep = ","

auPairToolVersion = 'v3'

class UneAuPair:
    "Notes"
    prenom = ''
    age = ''
    nationalite = ''
    ping = ''
    quandPing = ''
    pong = ''
    quandPong = ''
    status = ''
    commentaire = ''
    url = ''
    googleLine = -1
    googleStatus = 'new'
    def __init__(self):
        self.prenom = ''
    def __eq__(self, other):
        """Comparaison de deux au pair"""
        return self.url == other.url
    def updated(self):
        if ( self.googleStatus != 'new' ):
            self.googleStatus = 'update'
    def isToSync(self):
        return ( self.googleStatus == 'new' or self.googleStatus == 'update' )
    def toString(self, sep):
        """Format du dump fichier"""
        return self.prenom \
               + sep + self.nationalite \
               + sep + self.age \
               + sep + self.ping \
               + sep + self.quandPing \
               + sep + self.pong \
               + sep + self.quandPong \
               + sep + self.commentaire \
               + sep + self.url

def dump( champ, bulletProof ):
    returnMe = ""
    if ( bulletProof ):
        returnMe = repr(str(champ.encode('utf8')))[2:-1]
    else:
        returnMe = "'" + str(champ) + "'"
    returnMe = returnMe.replace("'", "\"")
    return returnMe

def readField( champ, bulletProof ):
    returnMe = ""
    if ( bulletProof ):
        returnMe = repr(str(champ.encode('utf8')))[2:-1]
    else:
        returnMe = str(champ)
    returnMe = returnMe.replace("'", "")
    return returnMe

def extractDetail(maSession, uneAuPair, spamTodo,messageType):
    extractOk = True
    try:
        r = maSession.get(uneAuPair.url, headers=headers, proxies=proxies, verify=False)
        if r.status_code != 200:
            print(r.status_code, r.reason)
    except:
        print("Erreur lors du fetch spam[" + uneAuPair.prenom + "] for [" + uneAuPair.url + "]")
        uneAuPair.status = 'erreurExtractDetail'
        extractOk = False

    if (extractOk):
        soup = BeautifulSoup(r.content, "html.parser")

        formPersonal = soup.find('form', action='/send-user-personal-mail-db.php')
        memberIdPersonal = ""
        if ( formPersonal ):
            memberIdPersonal = formPersonal.find('input', {'name': 'memberId'}).get('value')

        memberIdStuff = soup.find('input', {'name': 'memberId'})
        memberId = ""
        if ( memberIdStuff ):
            memberId = memberIdStuff.get('value')
        print(str(spamTodo) + " > spam[" + uneAuPair.prenom + "][" + uneAuPair.age + "][" + memberIdPersonal + "] for [" + uneAuPair.url + "]")


        if ( spamTodo ):
            sendMessage(maSession,uneAuPair, memberId,memberIdPersonal,messageType)


def sendMessage(maSession,uneAuPair,memberId,memberIdPersonal,messageType):

    spamDone = False
    memberId = False
    if (memberId):
        spamDone = True
        payload = "memberId=" + requote_uri(memberId) + "&visaAllowed=1&message=" + messageType + "&freeRequest=Envoyer"
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        r = maSession.post("https://www.aupair.com/personal-message-db.php", data=payload, headers=headers, proxies=proxies, verify=False)
        #  if r.status_code != 200:
        print("message-db",r.status_code, r.reason)

    if (memberIdPersonal):
        spamDone = True
        payload = "memberId=" + requote_uri(memberIdPersonal) + "&message=" + messageType + "&Submit=Envoyer"
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        r = maSession.post("https://www.aupair.com/send-user-personal-mail-db.php", data=payload, headers=headers, proxies=proxies, verify=False)
        #if r.status_code != 200:
        print("send-user",r.status_code, r.reason)

    now = datetime.now() # current date and time
    if ( spamDone ):
        uneAuPair.ping = 'oui'
    else:
        uneAuPair.ping = 'spamFail'
    uneAuPair.quandPing = now.strftime("%Y-%m-%d")
    uneAuPair.updated()

# extract search page summary info
def extractionPage(maSession, page_number,auPairDuSite):
    headersNotes = { \
        'content-type': 'text/html; charset=utf-8' , \
         'Sec-Fetch-Mode': 'navigate' \
        , 'Sec-Fetch-Site': 'same-origin' \
        , 'Sec-Fetch-User': '?1' \
    }

    r = maSession.get("https://www.aupair.com/find_aupair.php?quick_search=search&language=fr&page=" + str(page_number), headers=headersNotes, proxies=proxies, verify=False)
    if r.status_code != 200:
        print(r.status_code, r.reason)
    # else:
    #     print(r.content)

    print("*** Extraction page " + str(page_number))

    soup = BeautifulSoup(r.content, "html.parser")
    mydivs = soup.findAll("div", {"class": "search_result_box aupairList boxNew"})

    compteAuPair = 0
    now = datetime.now() # current date and time
    #    #<div class="search_result_box aupairList">
    for auPair in mydivs:
        uneAuPair = UneAuPair()
        uneAuPair.ping = 'todo'
        uneAuPair.quandPing = now.strftime("%Y-%m-%d")
        compteAuPair = compteAuPair + 1
        # if ( auPair.find("h4").find("b") ):
        #     print(auPair.find("h4").find("b"))
        # else:
        #     print(auPair.find("h4").find("a"))
        fullText = auPair.find("h4").text
        prenomEtAge = fullText.split(' ans,')[0]
        age = prenomEtAge[-2:]
        prenom = prenomEtAge[:-4]
        uneAuPair.age = age
        uneAuPair.prenom = prenom
        print(prenom + "/" + age)
        uneAuPair.url = requote_uri("https://www.aupair.com" + auPair.find("h4").find("a")['href'])
        # mySummary = auPair.findAll("div", {"class": "summary_box"})
        # for unSummary in mySummary:
        #     print(unSummary)

        myLabels = auPair.findAll("label")
        for unLabel in myLabels:
            if ( unLabel.text == "Départ" ):
                nope = False
                #print(unLabel.next_element.next_element.next_element.text.strip())
        #print(auPair)
        # n.write(uneAuPair.toString(sep) + '\n')
        auPairDuSite.append(uneAuPair)
        #break # break pour 1 par page
    return compteAuPair

# partie principale
if __name__ == "__main__":

    parser=argparse.ArgumentParser()

    parser.add_argument('--user', help='User', type=str)
    parser.add_argument('--pwd', help='Password', type=str)
    parser.add_argument('--proxy', help='https://uzer:pwd@name:port', type=str, default="")
    parser.add_argument('--spam', help='true', type=str, default="")
    parser.add_argument('--cred', help='true', type=str, default="")
    parser.add_argument('--token', help='true', type=str, default="")
    parser.add_argument('--chatid', help='true', type=str, default="")
    args=parser.parse_args()

    if args.proxy:
        print("Proxy provided")
        proxies = {
            "https": str(args.proxy)
        }

    #print(str(args.path))

    payload = "userNameF=" + urllib.parse.quote(str(args.user)) + "&passwordF=" + str(args.pwd) + "&login=Login+%C2%BB"
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    maSession = requests.session()

    r = maSession.post("https://www.aupair.com/login-submit.php", data=payload, headers=headers, proxies=proxies, verify=False)
    if r.status_code != 200:
        print(r.status_code, r.reason)

    r = maSession.get("https://www.aupair.com/my-account.php", headers=headers, proxies=proxies, verify=False)
    if r.status_code != 200:
        print(r.status_code, r.reason)

    r = maSession.get("https://www.aupair.com/matching_aupairs.php", headers=headers, proxies=proxies, verify=False)
    if r.status_code != 200:
        print(r.status_code, r.reason)

    print("Auth ok to auPair.com")

    encoreAuPair = True
    pageAuPair = 0

    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(args.cred), scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    auPairSheet = client.open("AuPair").worksheet("AuPair.com")
    messageSheet = client.open("AuPair").worksheet("Message")

    messageType = messageSheet.cell(1,1).value
    messageType = urllib.parse.quote(messageType)

    # Extract and print all of the values
    auPairFromGoogle = []
    list_of_hashes = auPairSheet.get_all_records()

    currentGoogleLine = 2 # header++
    for rec in list_of_hashes:
        uneAuPair = UneAuPair()
        for item in rec.items():
            # print(item[0], " -- ", item[1], "<", item, ">",)
            if ( item[0] == 'Who'):
                uneAuPair.prenom = readField(item[1], False)
            if ( item[0] == 'Where'):
                uneAuPair.nationalite = readField(item[1], False)
            if ( item[0] == 'Age'):
                uneAuPair.age = readField(item[1], False)
            if ( item[0] == 'Ping'):
                uneAuPair.ping = readField(item[1], False)
            if ( item[0] == 'WhenPing'):
                uneAuPair.quandPing = readField(item[1], False)
            if ( item[0] == 'Pong'):
                uneAuPair.pong = readField(item[1], False)
            if ( item[0] == 'WhenPong'):
                uneAuPair.quandPong = readField(item[1], False)
            if ( item[0] == 'Status'):
                uneAuPair.status = readField(item[1], False)
            if ( item[0] == 'Comment'):
                uneAuPair.commentaire = readField(item[1], False)
            if ( item[0] == 'URL'):
                uneAuPair.url = readField(item[1], False)
        uneAuPair.googleLine = currentGoogleLine
        currentGoogleLine = currentGoogleLine + 1
        uneAuPair.googleStatus = 'nope'
        auPairFromGoogle.append(uneAuPair)

    print("Nb AuPair from Google %s" % len(auPairFromGoogle))
    googleNextRow = len(auPairFromGoogle) + 2 # header + new row
    auPairDuSite = []

    while( encoreAuPair ):
        compte = extractionPage(maSession, pageAuPair,auPairDuSite)
        encoreAuPair = (compte > 0)
        pageAuPair = pageAuPair + 1

    # pour utilisation sans fetch du site, seulement les status du fichie existant
    auPairNouvelleDuSite = []

    compteTotal = 0
    compteNouvelle = 0
    for uneAuPairSite in auPairDuSite:
        compteTotal = compteTotal + 1
        existeDeja = False
        for uneAuPairHistorique in auPairFromGoogle:
            if ( uneAuPairHistorique == uneAuPairSite):
                existeDeja = True
                break
        if ( not existeDeja ):
            auPairNouvelleDuSite.append(uneAuPairSite)
            compteNouvelle = compteNouvelle + 1
        else:
            if ( uneAuPairHistorique.age != uneAuPairSite.age ):
                uneAuPairHistorique.age = uneAuPairSite.age
                uneAuPairHistorique.updated()

    auPairFromGoogle.extend(auPairNouvelleDuSite)
    print("Fin extraction : " + str(compteNouvelle) + " nouveaux profiles pour " + str(compteTotal) + " recupérés du site\n Total inventaire " + str(len(auPairFromGoogle)))

    #spam
    spamTodo = True
    for uneAuPair in auPairFromGoogle:
        if ( uneAuPair.ping == 'todo'):
            extractDetail(maSession,uneAuPair,spamTodo,messageType)

    rowSync = 1
    nbUpdate = 0
    nbCreate = 0
    for uneAuPair in auPairFromGoogle:
        if ( uneAuPair.isToSync()):
            #print("Sync to google " + uneAuPair.prenom + " ." + str(rowSync))
            if ( uneAuPair.googleStatus == 'update'):
                print("Update %s" % uneAuPair.prenom, " on line %d" % uneAuPair.googleLine)
                auPairSheet.update_cell(uneAuPair.googleLine,2,uneAuPair.nationalite)
                auPairSheet.update_cell(uneAuPair.googleLine,3,uneAuPair.age)
                auPairSheet.update_cell(uneAuPair.googleLine, 4, uneAuPair.ping)
                auPairSheet.update_cell(uneAuPair.googleLine, 5, uneAuPair.quandPing)
                nbUpdate = nbUpdate + 1
            else:
                print("Create %s" % uneAuPair.prenom, " at line %d" % googleNextRow)
                row = [uneAuPair.prenom, uneAuPair.nationalite, uneAuPair.age, uneAuPair.ping, uneAuPair.quandPing, uneAuPair.pong, uneAuPair.quandPong, uneAuPair.status,  uneAuPair.commentaire, uneAuPair.url]
                print(auPairSheet.insert_row(row,googleNextRow))
                googleNextRow = googleNextRow + 1
                nbCreate = nbCreate + 1
        rowSync = rowSync + 1


    bot = telegram.Bot(token=str(args.token))
    bot.send_message(chat_id=str(args.chatid), text="*AuPair(" + auPairToolVersion + ")* _create_ `" + str(nbCreate) + "` / _update_ `" + str(nbUpdate) + "` / _total_ `" + str(len(auPairFromGoogle)) + "`", parse_mode=telegram.ParseMode.MARKDOWN)
    #bot.send_document(chat_id=str(args.chatid), document=open('tests/test.zip', 'rb'))

    print("End of process")