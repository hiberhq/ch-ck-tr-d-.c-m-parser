#!/usr/bin/env python3

import os
import shutil
import requests
from requests.utils import requote_uri
from bs4 import BeautifulSoup
import json
import re
import argparse


BASE_URL = 'https://www.che' + 'ck' + 'atr' + 'ad' + 'e.com'
PATH = 'temp'
URLS_PATH = PATH + '/urls.txt'
STATE_PATH = PATH + '/state.json'
CAT_PATH = 'categories.conf'
POST_PATH = 'postcodes.conf'
CAT_ALL_PATH = 'categories_all.conf'
POST_ALL_PATH = 'postcodes_all.conf'
RESULT = 'data.json'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}


def log(text, color = ''):
	colors = {
		'black': '\x1b[30m',
		'red': '\x1b[31m',
		'green': '\x1b[32m',
		'yellow': '\x1b[33m',
		'blue': '\x1b[34m',
		'magenta': '\x1b[35m',
		'cyan': '\x1b[36m',
		'white': '\x1b[37m'
	}
	print(colors.get(color, '\x1b[0m'), text, '\x1b[0m')

	
##
# Let's get it started
##

os.system('clear')
count = 0

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='f', action='store_const', const=True, help='Will start to parse from the ground erasing the previous parser state.')
args = parser.parse_args()

if args.f:
	if os.path.exists(RESULT):
		try:
			os.remove(RESULT)
		except OSError as e:
			log('Cannot remove file %s %s' % (RESULT, e), 'red')
	if os.path.exists(PATH):
		try:
			shutil.rmtree(PATH)
		except OSError as e:
			log('Cannot remove file %s %s' % (RESULT, e), 'red')


def nrmlz(HTMLString):
	return HTMLString.text.replace('\n', ' ').strip()


def nrmlzMoney(s):
	# Not sure about removing commas as soon as I saw value 5000000.0
	return re.sub('[£ ]+', '', s.text)


def decryptEmail(encodedString):
	r = int(encodedString[:2],16)
	email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
	return email


def writeState(state):
	if os.path.exists(STATE_PATH):
		writeFile(state)
	else:
		if os.path.exists(PATH):
			writeFile(state)
		else:
			# Create it initially
			try:
				os.mkdir(PATH)
				os.chmod(PATH, 0o777)
				writeFile(state)
			except OSError as e:
				log("Cannot create the directory '%s'. %s" % (PATH, e), 'red')
				exit(-1)

				
def writeFile(state):
	try:
		with open(STATE_PATH, 'w') as file:
			file.write(json.dumps(state))
	except OSError as e:
		log("Cannot write in file '%s'. %s" % (STATE_PATH, e), 'red')
		exit(-1)
		
##
# Handle input or kinda
##
if os.path.exists(CAT_PATH):
	with open(CAT_PATH, 'r') as file:
		categories = file.readline().split(',')
else:
	if os.path.exists(CAT_ALL_PATH):
		with open(CAT_ALL_PATH, 'r') as file:
			categories = file.readline().split(',')
	else:
		log('Cannot find %s / %s file' % (CAT_PATH, CAT_ALL_PATH), 'red')
		exit(-1)

if os.path.exists(POST_PATH):
	with open(POST_PATH, 'r') as file:
		postcodes = file.readline().split(',')
else:
	if os.path.exists(POST_ALL_PATH):
		with open(POST_ALL_PATH, 'r') as file:
			postcodes = file.readline().split(',')
	else:
		log('Cannot find %s / %s file' % (POST_PATH, POST_ALL_PATH), 'red')
		exit(-1)


# Use previous values to resume the work
if os.path.exists(STATE_PATH):
	print('%s does exist' % STATE_PATH)
	with open(STATE_PATH, 'r') as file:
		state = json.loads(file.read())
		
		if state['cat'] == len(categories) - 1 and state['postcode'] == len(postcodes) - 1:
			log('Seems like the previous task was completed. To run parser again add -f parameter to run.', 'yellow')
			log('In this case ALL PARSED DATA WILL BE ERASED. So make sure you save/use data.', 'red')
			exit()
else:
	# Begin from the start with default values
	state = {'page': 1, 'cat': 0, 'catName': '', 'postcode': 0}
	writeState(state)

		
def checkNextSearch():
	if not os.path.exists(URLS_PATH):
		log('no urls file, so try to page += 1', 'magenta')
		state['page'] = state['page'] + 1
		writeState(state)
		getSearchResults()

	goTo(getURL())

def query():
	return BASE_URL + '/Search/?postcode=%s&location=%s&page=%s&facet_Category=%s' % (postcodes[state['postcode']], postcodes[state['postcode']], state['page'], categories[state['cat']])


def getContent(url):
	try:
		response = requests.get(url, headers=HEADERS).text # url, timeout=(10, 0.00001)
	except requests.RequestException as e:
		if e.response is not None:
			log(e.response + ' %s' % url, 'red')
		else:
			log(str(e) + ' %s' % url, 'red')
		response = False
		
	return response


def getSearchResults():
#	print('getSearchResults')
	content = getContent(query())
	
	if not content:
		log('No response from server/ No search results', 'red')
		# Try to get it again?
		getSearchResults()
		return
	
	html = BeautifulSoup(content, 'html.parser')
	searchRes = html.find(class_="results")
	
	if None == searchRes or 1 == len(list(searchRes.children)): # 1 is element itself with no childrens oO
		# Next query
		log('No results for query %s' % query(), 'blue')
		nextQuery()
		return
		
	links = searchRes.select('.results__title a')
	state['catName'] = html.find('h1').text.split(' in ')[0]
	
	with open(URLS_PATH, 'w') as file:
#		log('write in file %s' % URLS_PATH)
		urls = ''
		for i, link in enumerate(links):
			urls += ('' if i == 0 else '\n') + BASE_URL + link.get('href')
		file.write(urls)
	


def nextQuery():
	state['page'] = 1
	
	if len(postcodes) > state['postcode'] + 1:
		state['postcode'] = state['postcode'] + 1
		log('Next query. postcode: %s page: %s cat: %s' % (state['postcode'], state['page'], state['cat']), 'green')
		writeState(state)
		getSearchResults()
	else:
		if len(categories) > state['cat'] + 1:
			state['cat'] = state['cat'] + 1
			log('Next query. postcode: %s page: %s cat: %s' % (state['postcode'], state['page'], state['cat']), 'green')
			writeState(state)
			getSearchResults()
		else:
			with open(RESULT, 'a') as file:
				file.write(']')
			log('...DONE!...', 'yellow')
			exit()

			
def getURL():
	with open(URLS_PATH, 'r') as file:
		urls = ''
		for i, line in enumerate(file):
			if i == 0:
				url = line
			else:
				urls += line
				
	if not urls:
		# urls var is empty, so
		os.remove(URLS_PATH)
	else:
		with open(URLS_PATH, 'w') as file:
			file.write(urls)
	
	return requote_uri(url).rstrip('%0A')


# Multithread it
def goTo(url):
	content = getContent(url)

	if not content:
		# maybe try to refresh the same URL?
		log('No response from server. Trying to get response again', 'red')
		goTo(url)
		return

	saveData(content, url)
	checkNextSearch()


def saveData(content, url):
#	os.system('clear')
	html = BeautifulSoup(content, 'html.parser')
	r = {}
	
	name = nrmlz(html.find('h1'))
	contact = html.find(class_='contact-card__contact-name')
	phones = html.select('a[href^="tel"]')
	phonesStr = ''
	for i, phone in enumerate(phones):
		phonesStr += phone.get('href')[4:]
		if (i + 1 < len(phones)):
			phonesStr += ', '
	email = html.select('#ctl00_ctl00_content_ctlEmail span')
	email = email[0].get('data-cfemail') if email else ''
	email2 = html.select('#ctl00_ctl00_content_managedEmail span')
	email2 = email2[0].get('data-cfemail') if email2 else ''
	website = html.find(id='ctl00_ctl00_content_ctlWeb1')
	score = html.find(class_='scores__overall-value')
	reliability = html.select('.scores__row:nth-child(2) .scores__value')
	reliability = reliability[0] if reliability else ''
	tidiness = html.select('.scores__row:nth-child(3) .scores__value')
	tidiness = tidiness[0] if tidiness else ''
	courtesy = html.select('.scores__row:nth-child(4) .scores__value')
	courtesy = courtesy[0] if courtesy else ''
	workmanship = html.select('.scores__row:nth-child(5) .scores__value')
	workmanship = workmanship[0] if workmanship else ''
	reviews = html.find(class_='page-nav__review-count')
	basedIn = html.find(class_='address', recursive=True)
	worksIn = html.select('#ctl00_ctl00_content_content_pnlWorksIn p')
	worksIn = worksIn[0] if worksIn else ''
	
	r['name'] = name
	r['pageURL'] = url
	r['contact'] = nrmlz(contact) if contact else ''
	r['phones'] = phonesStr
	r['email'] = decryptEmail(email) if email else decryptEmail(email2)
	r['website'] = website.get('href') if website else ''
	r['score'] = nrmlz(score) if score else ''
	r['reliability'] = nrmlz(reliability) if reliability else ''
	r['tidiness'] = nrmlz(tidiness) if tidiness else ''
	r['courtesy'] = nrmlz(courtesy) if courtesy else ''
	r['workmanship'] = nrmlz(workmanship) if workmanship else ''
	r['reviews'] = nrmlz(reviews) if reviews else ''
	r['basedin'] = nrmlz(basedIn) if basedIn else ''
	r['worksin'] = nrmlz(worksIn) if worksIn else ''
	r['postcode'] = postcodes[state['postcode']]
	r['category'] = categories[state['cat']]
	r['categoryName'] = state['catName']
	
	global count
	count += 1
	log('%s. Saving %s post: %s cat: %s page: %s' % (count, name, state['postcode'], state['cat'], state['page']), 'cyan')
	
	##
	# getData2
	##
	content2 = getContent(url + 'Checks.aspx')

	if not content2:
		log('No response from page %s' % url + 'Checks.aspx', 'red')
		
	html2 = BeautifulSoup(content2, 'html.parser')
	
	gasSafeNumber = html2.select('img[alt="Gas Safe Register"]')
	gasSafeNumber = html2.find(class_="background-check__caption").text.replace('verify membership', '').replace('Get the Promise', '').strip() if gasSafeNumber else ''
	companyType = html2.select('#ctl00_ctl00_content_content_trCompanyType td')
	companyType = companyType[0] if companyType else ''
	companyOwner = html2.select('#ctl00_ctl00_content_content_trOwners td')
	companyOwner = companyOwner[0] if companyOwner else ''
	companyLimitedCheked = html2.select('#ctl00_ctl00_content_content_trLimitedChecked td')
	companyLimitedCheked = companyLimitedCheked[0] if companyLimitedCheked else ''
	companyVAT = html2.find(id='ctl00_ctl00_content_content_lblVAT')
	publicLiabilityInsurance = html2.find(id='ctl00_ctl00_content_content_lblInsurance')
	insuredBy = html2.select('#ctl00_ctl00_content_content_pnlInsurance tr:nth-child(2) td')
	insuredBy = insuredBy[0] if insuredBy else ''
	insuranceAmount = html2.select('#ctl00_ctl00_content_content_pnlInsurance tr:nth-child(3) td')
	insuranceAmount = insuranceAmount[0] if insuranceAmount else ''
	
		
	r['gasSafeNumber'] = gasSafeNumber if gasSafeNumber else ''
	r['companyType'] = nrmlz(companyType) if companyType else ''
	r['companyOwner'] = nrmlz(companyOwner) if companyOwner else ''
	r['companyLimitedCheked'] = nrmlz(companyLimitedCheked) if companyLimitedCheked else ''
	r['companyVAT'] = nrmlz(companyVAT) if companyVAT else ''
	r['publicLiabilityInsurance'] = nrmlz(publicLiabilityInsurance) if publicLiabilityInsurance else ''
	r['insuredBy'] = nrmlz(insuredBy) if insuredBy else ''
	r['insuranceAmount'] = nrmlzMoney(insuranceAmount) if insuranceAmount else ''
	
	
	##
	# write the Data
	##	
	if os.path.exists(RESULT):
		result = ',' + json.dumps(r)
	else:
		result = '[' + json.dumps(r)
	
	try:
		with open(RESULT, 'a') as file:
			file.write(result)
	except OSErroror as e:
		log("Cannot write in file '%s'. %s" % (RESULT, e), 'red')
		exit(-1)


if __name__ == '__main__':
	if not os.path.exists(URLS_PATH):
		log('No %s file, so go to search' % URLS_PATH, 'magenta')
		getSearchResults()

	goTo(getURL())