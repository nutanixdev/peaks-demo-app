user = "@@{Prism Central User.username}@@"
password = "@@{Prism Central User.secret}@@"

def process_request(url, method, user, password, headers, payload=None):
    r = urlreq(url, verb=method, auth="BASIC", user=user, passwd=password, params=payload, verify=False, headers=headers)
    return r

url = "https://@@{pc_instance_ip}@@:9440/api/nutanix/v3/categories/Deployment/@@{calm_application_name}@@"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
url_method = "DELETE"
r = process_request(url, url_method, user, password, headers)
print "Response Status: " + str(r.status_code)

