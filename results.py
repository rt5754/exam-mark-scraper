import requests, json
from lxml import html
from lxml import etree as et

session_requests = requests.session()

login_url = "https://sso-legacy.sun.ac.za/cas/login?service=https://web-apps.sun.ac.za/AcademicResults/shiro-cas"
result = session_requests.get(login_url)

tree = html.fromstring(result.text)
authenticity_token = list(set(tree.xpath("//input[@name='lt']/@value")))[0]

f = open('credentials.json')
credentials = json.load(f)
username = credentials.get('Username')
password = credentials.get('Password')

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
modules = []
marks = []
tree = html.fromstring(result.text)
root = et.HTML(result.text)
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
	print(f"{modules[i]:<25}{marks[i]:>5}")
	i = i+1

