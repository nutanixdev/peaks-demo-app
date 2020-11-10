url = "https://@@{f5_ip}@@/mgmt/tm/ltm/virtual/primary-@@{cicd_app_name}@@-virtual-vs"
url_method = "PATCH"
user = "@@{F5.username}@@"
password = "@@{F5.secret}@@"

def process_request(url, method, user, password, headers, payload=None):
    r = urlreq(url, verb=method, auth="BASIC", user=user, passwd=password, params=payload, verify=False, headers=headers)
    return r

headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

payload_obj = {}
payload_obj['pool'] = "@@{service_name}@@-@@{MongoDBF5.app_name}@@-@@{project_name}@@@@{build_number}@@-pool";

payload = json.dumps(payload_obj)
print "Payload: " + payload

r = process_request(url, url_method, user, password, headers, payload)
print "Response Status: " + str(r.status_code)
print "Response: " + str(r.json())
