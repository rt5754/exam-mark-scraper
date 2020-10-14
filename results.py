import requests, json, time
from lxml import html
from lxml import etree as et
from twilio.rest import Client

session_requests = requests.session()

login_url = "https://sso-legacy.sun.ac.za/cas/login?service=https://web-apps.sun.ac.za/AcademicResults/shiro-cas"
result = session_requests.get(login_url)

tree = html.fromstring(result.text)
authenticity_token = list(set(tree.xpath("//input[@name='lt']/@value")))[0]

f = open('credentials.json')
credentials = json.load(f)

#MYSUN credentials setup
username = credentials.get('Username')
password = credentials.get('Password')

#Twilio credentials setup
account_sid = credentials.get('account_sid')
twilio_auth_token = credentials.get('auth_token')
client = Client(account_sid, twilio_auth_token)

old_marks = []
initial_run = 1
iterations = 1
#Infinite loop
while 1:
	payload = {
		"username": username, 
		"password": password, 
		"lt": authenticity_token,
		"execution": "e1s1",
		"_eventId": 'submit'
	}

	result = session_requests.post(
		"https://sso-legacy.sun.ac.za/cas/login;jsessionid=7F52F16889C9AF59596895DFC27C8E90?service=https://web-apps.sun.ac.za/AcademicResults/shiro-cas", 
		data = payload, 
		headers = dict(referer=login_url)
	)

	home_url = "https://web-apps.sun.ac.za/AcademicResults/Exam.jsp?pLang=1"
	result = session_requests.get(
		home_url, 
		headers = dict(referer = home_url)
	)

	root = et.HTML(result.text)
	## FOR TESTING
	# f = open('marks.txt')
	# result = f.read()
	# root = et.HTML(result)
	##
	modules = []
	marks = []
	
	body = root[1]
	table = body[1]
	i = 3
	while i < 13:
		tr = table[i]
		modules.append(" ".join((tr[1][0].text).split()))
		if (tr[4][0].text != None):
			marks.append(tr[4][0].text)
		else:
			marks.append("TBA")
		i = i + 1
	i = 0

	while i<len(modules):
		if ((initial_run == 0) and (marks[i] != old_marks[i])):					#If a mark has changed
			module = str(modules[i])
			notification = module.upper() + ": YOU ACHIEVED A MARK OF " + marks[i]
			#Send SMS using Twilio
			message = client.messages \
		    .create(
		         body= notification,
		         from_='+12055731812',
		         status_callback='http://postb.in/1234abcd',
		         to='+27713313052'
		     )

		#print(f"{modules[i]:<25}{marks[i]:>5}")
		i = i+1
	print('Iterations: ' + str(iterations))
	old_marks = marks
	initial_run = 0
	iterations += 1
	time.sleep(60)   				#Wait time in seconds, default is 1 min


