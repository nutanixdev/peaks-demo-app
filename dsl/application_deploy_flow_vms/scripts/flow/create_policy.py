user = "@@{Prism Central User.username}@@"
password = "@@{Prism Central User.secret}@@"

def process_request(url, method, user, password, headers, payload=None):
    r = urlreq(url, verb=method, auth="BASIC", user=user, passwd=password, params=payload, verify=False, headers=headers)
    return r

url = "https://@@{pc_instance_ip}@@:9440/api/nutanix/v3/network_security_rules"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
url_method = "POST"

payload = {
    "metadata": {
        "categories": {},
        "kind": "network_security_rule",
        "spec_version": 0
    },
    "spec": {
        "description": "Secure mongo @@{calm_application_name}@@ deployment",
        "name": "@@{calm_application_name}@@_Policy",
        "resources": {
            "app_rule": {
                "action": "APPLY",
                "inbound_allow_list": [
                    {
                        "filter": {
                            "kind_list": [
                                "vm"
                            ],
                            "params": {
                                "AppType": [
                                    "Node.js_Deployment"
                                ],
                                "Deployment": [
                                    "@@{calm_application_name}@@"
                                ]
                            },
                            "type": "CATEGORIES_MATCH_ALL"
                        },
                        "peer_specification_type": "FILTER",
                        "protocol": "TCP",
                        "tcp_port_range_list": [
                            {
                                "end_port": 27017,
                                "start_port": 27017
                            }
                        ]
                    },
                    {
                        "ip_subnet": {
                            "ip": "10.59.98.214",
                            "prefix_length": 32
                        },
                        "peer_specification_type": "IP_SUBNET",
                        "protocol": "TCP",
                        "tcp_port_range_list": [
                            {
                                "end_port": 22,
                                "start_port": 22
                            },
                            {
                                "end_port": 23,
                                "start_port": 23
                            }
                        ]
                    },
                    {
                        "icmp_type_code_list": [
                            {
                                "code": 0,
                                "type": 8
                            }
                        ],
                        "ip_subnet": {
                            "ip": "10.59.98.214",
                            "prefix_length": 32
                        },
                        "peer_specification_type": "IP_SUBNET",
                        "protocol": "ICMP"
                    }
                ],
                "outbound_allow_list": [
                    {
                        "peer_specification_type": "ALL"
                    }
                ],
                "target_group": {
                    "filter": {
                        "kind_list": [
                            "vm"
                        ],
                        "params": {
                            "AppType": [
                                "Mongo_Deployment"
                            ],
                            "Deployment": [
                                "@@{calm_application_name}@@"
                            ]
                        },
                        "type": "CATEGORIES_MATCH_ALL"
                    },
                    "peer_specification_type": "FILTER"
                }
            }
        }
    }
}

print "Payload: " + json.dumps(payload)

r = process_request(url, url_method, user, password, headers, json.dumps(payload))
print "Response Status: " + str(r.status_code)
print "Response: ", r.json()

print "policy_uuid=", r.json()['metadata']['uuid']

