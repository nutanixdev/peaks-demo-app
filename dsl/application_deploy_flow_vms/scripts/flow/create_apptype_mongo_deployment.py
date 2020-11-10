user = "@@{Prism Central User.username}@@"
password = "@@{Prism Central User.secret}@@"

def process_request(url, method, user, password, headers, payload=None):
    r = urlreq(url, verb=method, auth="BASIC", user=user, passwd=password, params=payload, verify=False, headers=headers)
    return r

url = "https://@@{pc_instance_ip}@@:9440/api/nutanix/v3/categories/AppType/Mongo_Deployment"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
url_method = "PUT"
payload = {"value": "Mongo_Deployment","description":"Mongo_Deployment deployment"}
r = process_request(url, url_method, user, password, headers, json.dumps(payload))
print "Response Status: " + str(r.status_code)
print "Response: ", r.json()

url = "https://@@{pc_instance_ip}@@:9440/api/nutanix/v3/categories/AppType/Node.js_Deployment"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
url_method = "PUT"
payload = {"value": "Node.js_Deployment","description":"Node.js_Deployment deployment"}
r = process_request(url, url_method, user, password, headers, json.dumps(payload))
print "Response Status: " + str(r.status_code)
print "Response: ", r.json()

