import requests
import argparse
from bs4 import BeautifulSoup
from requests.utils import requote_uri
import csv
import os
from datetime import datetime
import urllib.parse

proxies = {}

sep = ","

class UneAuPair:
    "Notes"
    prenom = ''
    age = ''
    nationalite = ''
    status = ''
    quandStatus = ''
    pong = ''
    quandPong = ''
    commentaire = ''
    url = ''
    def __init__(self):
        self.prenom = ''
    def __eq__(self, other):
        """Comparaison de deux notes"""
        return self.prenom == other.prenom \
           and self.url == other.url
    def toString(self, sep):
        """Format du dump fichier"""
        return self.prenom \
               + sep + self.nationalite \
               + sep + self.age \
               + sep + self.status \
               + sep + self.quandStatus \
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

def extractDetail(maSession, uneAuPair, spamTodo):
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
        if ( formPersonal ):
            memberIdPersonal = formPersonal.find('input', {'name': 'memberId'}).get('value')

        memberIdStuff = soup.find('input', {'name': 'memberId'})
        if ( memberIdStuff ):
            memberId = memberIdStuff.get('value')
        print(str(spamTodo) + " > spam[" + uneAuPair.prenom + "][" + uneAuPair.age + "][" + memberIdPersonal + "] for [" + uneAuPair.url + "]")

        now = datetime.now() # current date and time
        if ( spamTodo ):
            sendMessage(maSession,memberId,memberIdPersonal)
            uneAuPair.status = 'oui'
            uneAuPair.quandStatus = now.strftime("%Y-%m-%d")

def sendMessage(maSession,memberId,memberIdPersonal):
    memberId = False
    if (memberId):
        payload = "memberId=" + requote_uri(memberId) + "&visaAllowed=1&message=Hello%2C%0Awe%20would%20love%20to%20hear%20about%20you%20to%20see%20if%20you%20could%20be%20interested%20in%20living%20with%20us%20%21%0AWe%20have%20two%20kids%20at%20home%20during%20the%20day%2C%20Elise%20who%20is%20nearly%204%20and%20Raphael%20nearly%2010%20%28the%20others%20are%2011%2C%2014%20and%2016%20and%20take%20care%20of%20themselves%29.%0AThey%20were%20in%20a%20Montessori%20school%20last%20year%20but%20the%20teachers%20were%20not%20like%20we%20hoped%20so%20we%20are%20homeschooling%20them%20both%20this%20year.%0A%0AWe%20live%20in%20a%20beautiful%20place%20in%20east%20France%20and%20would%20love%20to%20show%20you%20our%20country%20and%20around.%0APlease%20let%20us%20know%20if%20you%20could%20be%20interested.%0AKind%20regards%0AMagali&freeRequest=Envoyer"
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        r = maSession.post("https://www.aupair.com/personal-message-db.php", data=payload, headers=headers, proxies=proxies, verify=False)
        #  if r.status_code != 200:
        print("message-db",r.status_code, r.reason)

    if (memberIdPersonal):
        payload = "memberId=" + requote_uri(memberIdPersonal) + "&message=Hello%2C%0Awe%20would%20love%20to%20hear%20about%20you%20to%20see%20if%20you%20could%20be%20interested%20in%20living%20with%20us%20%21%0AWe%20have%20two%20kids%20at%20home%20during%20the%20day%2C%20Elise%20who%20is%20nearly%204%20and%20Raphael%20nearly%2010%20%28the%20others%20are%2011%2C%2014%20and%2016%20and%20take%20care%20of%20themselves%29.%0AThey%20were%20in%20a%20Montessori%20school%20last%20year%20but%20the%20teachers%20were%20not%20like%20we%20hoped%20so%20we%20are%20homeschooling%20them%20both%20this%20year.%0A%0AWe%20live%20in%20a%20beautiful%20place%20in%20east%20France%20and%20would%20love%20to%20show%20you%20our%20country%20and%20around.%0APlease%20let%20us%20know%20if%20you%20could%20be%20interested.%0AKind%20regards%0AMagali&Submit=Envoyer"
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        r = maSession.post("https://www.aupair.com/send-user-personal-mail-db.php", data=payload, headers=headers, proxies=proxies, verify=False)
        #if r.status_code != 200:
        print("send-user",r.status_code, r.reason)

    #<form method="post" action="/personal-message-db.php">
    #https://www.aupair.com/send-user-personal-mail-db.php
    #memberId=1430596&message=Hello%2C%0D%0Awe+would+love+to+hear+about+you+to+see+if+you+could+be+interested+in+living+with+us+%21%0D%0AWe+have+two+kids+at+home+during+the+day%2C+Elise+who+is+nearly+4+and+Raphael+nearly+10+%28the+others+are+11%2C+14+and+16+and+take+care+of+themselves%29.%0D%0AThey+were+in+a+Montessori+school+last+year+but+the+teachers+were+not+like+we+hoped+so+we+are+homeschooling+them+both+this+year.%0D%0A%0D%0AWe+live+in+a+beautiful+place+in+east+France+and+would+love+to+show+you+our+country+and+around.%0D%0APlease+let+us+know+if+you+could+be+interested.%0D%0AKind+regards%0D%0AMagali&Submit=Envoyer

# fonction pour lister toutes les notes d'un eleve sur base de son ID
def extractionPage(maSession, n, page_number,auPairDuSite):
    headersNotes = { 'content-type': 'text/html; charset=utf-8' \
        , 'Sec-Fetch-Mode': 'navigate' \
        , 'Sec-Fetch-Site': 'same-origin' \
        , 'Sec-Fetch-User': '?1' \
    }

    r = maSession.get("https://www.aupair.com/find_aupair.php?quick_search=search&language=fr&page=" + str(page_number), headers=headersNotes, proxies=proxies, verify=False)
    if r.status_code != 200:
        print(r.status_code, r.reason)

    print("*** Extraction page " + str(page_number))

    soup = BeautifulSoup(r.content, "html.parser")
    mydivs = soup.findAll("div", {"class": "search_result_box aupairList"})

    compteAuPair = 0
    #<div class="search_result_box aupairList">
    for auPair in mydivs:
        uneAuPair = UneAuPair()
        uneAuPair.status = 'todo'
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
        n.write(uneAuPair.toString(sep) + '\n')
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
    args=parser.parse_args()

    if args.proxy:
        print("Proxy provided")
        proxies = {
            "https": str(args.proxy)
        }

    #print(str(args.user) + "//" + urllib.parse.quote(str(args.user)) )

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

    print("Generation des fichiers ici : [" + os.getcwd() + "]")

    encoreAuPair = True
    pageAuPair = 0

    nouveauFichier = True

    nomFichierHistorique = "d:/Documents/[Mes Documents]/Gestion/AuPair/aupair.com.csv"
    nomFichierNouveau = "d:/Documents/[Mes Documents]/Gestion/AuPair/aupair.new.csv"
    nomFichierNouveauTotal = "d:/Documents/[Mes Documents]/Gestion/AuPair/aupair.new.total.csv"
    nomFichierHistoriqueBackup = "d:/Documents/[Mes Documents]/Gestion/AuPair/aupair.com.backup.csv"

    auPairDuFichier = []

    if ( os.path.isfile(nomFichierHistorique) ):
        nouveauFichier = False
        # lire les notes déjà presente si existe
        line_count = 0
        with open(nomFichierHistorique) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=sep)
            for row in csv_reader:
                uneAuPair = UneAuPair()
                if line_count == 0:
                    #print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    #print(f'\t{row[0]}  sur ligne {line_count}.')
                    uneAuPair.prenom = readField(row[0], False)
                    uneAuPair.nationalite = readField(row[1], False)
                    uneAuPair.age = readField(row[2], False)
                    uneAuPair.status = readField(row[3], False)
                    uneAuPair.quandStatus = readField(row[4], False)
                    uneAuPair.pong = readField(row[5], False)
                    uneAuPair.quandPong = readField(row[6], False)
                    uneAuPair.commentaire = readField(row[7], False)
                    uneAuPair.url = readField(row[8], False)

                    auPairDuFichier.append(uneAuPair)
                    line_count += 1


    auPairDuSite = []
    with open(nomFichierNouveau, "w") as n:
        if (nouveauFichier):
            n.write(
                'Qui'
                + sep + 'Ou'
                + sep + 'Age'
                + sep + 'Contacté'
                + sep + 'Quand'
                + sep + 'Pong'
                + sep + 'Quand'
                + sep + 'Commentaire'
                + sep + 'URL'
                + "\n"
            )

        while( encoreAuPair ):
            compte = extractionPage(maSession, n, pageAuPair,auPairDuSite)
            encoreAuPair = (compte > 0)
            pageAuPair = pageAuPair + 1

        n.close()

    # pour utilisation sans fetch du site, seulement les status du fichie existant
    #auPairDuSite = []

    auPairNouvelleDuSite = []

    compteTotal = 0
    compteNouvelle = 0
    for uneAuPairSite in auPairDuSite:
        compteTotal = compteTotal + 1
        existeDeja = False
        for uneAuPairHistorique in auPairDuFichier:
            if ( uneAuPairHistorique == uneAuPairSite):
                existeDeja = True
                break
        if ( not existeDeja ):
            auPairNouvelleDuSite.append(uneAuPairSite)
            compteNouvelle = compteNouvelle + 1
        else:
            uneAuPairHistorique.age = uneAuPairSite.age

    auPairDuFichier.extend(auPairNouvelleDuSite)
    print("Fin extraction : " + str(compteNouvelle) + " nouveaux profiles pour " + str(compteTotal) + " recupérés du site\n Total inventaire " + str(len(auPairDuFichier)))

    #spam
    spamTodo = True
    for uneAuPair in auPairDuFichier:
        if ( uneAuPair.status == 'todo'):
            extractDetail(maSession,uneAuPair,spamTodo)

    with open(nomFichierNouveauTotal, "w") as n:
        n.write(
            'Qui'
            + sep + 'Ou'
            + sep + 'Age'
            + sep + 'Contacté'
            + sep + 'Quand'
            + sep + 'Pong'
            + sep + 'Quand'
            + sep + 'Commentaire'
            + sep + 'URL'
            + "\n"
        )
        for uneAuPair in auPairDuFichier:
            n.write(uneAuPair.toString(sep) + '\n')
        n.close()

    print("Renommage des fichiers pour garder [" + nomFichierHistorique + "] comme totale")
    if ( os.path.isfile(nomFichierHistoriqueBackup) ):
        os.remove(nomFichierHistoriqueBackup)
    os.rename(nomFichierHistorique, nomFichierHistoriqueBackup)
    os.rename(nomFichierNouveauTotal, nomFichierHistorique)