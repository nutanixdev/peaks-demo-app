"""
CALM DSL Application Deployment VMs With F5 and Infoblox Integration Blueprint

"""

import os
from calm.dsl.builtins import *
from calm.dsl.config import get_context

ContextObj = get_context()
init_data = ContextObj.get_init_config()

if file_exists(os.path.join(init_data["LOCAL_DIR"]["location"], "f5_ip")):
    F5IP = read_local_file("f5_ip")
else:
    F5IP = ""

if file_exists(os.path.join(init_data["LOCAL_DIR"]["location"], "infoblox_ip")):
    InfobloxIP = read_local_file("infoblox_ip")
else:
    InfobloxIP = ""

if file_exists(os.path.join(init_data["LOCAL_DIR"]["location"], "network")):
    Network = read_local_file("network")
else:
    Network = ""

if file_exists(os.path.join(init_data["LOCAL_DIR"]["location"], "domain_name")):
    DomainName = read_local_file("domain_name")
else:
    DomainName = ""

NutanixPublicKey = read_local_file("nutanix_public_key")
NutanixUser = read_local_file("nutanix_user")
NutanixKey = read_local_file("nutanix_key")
NutanixCred = basic_cred(
                    NutanixUser,
                    name="Nutanix",
                    type="KEY",
                    password=NutanixKey,
                    default=True
                )

ArtifactoryPassword = read_local_file("artifactory_password")
ArtifactoryUser = read_local_file("artifactory_user")
ArtifactoryCred = basic_cred(
                    ArtifactoryUser,
                    name="Artifactory Credential", 
                    type="PASSWORD", 
                    password=ArtifactoryPassword, 
                    default=False
                )

InfobloxPassword = read_local_file("infoblox_password")
InfobloxUser = read_local_file("infoblox_user")
InfobloxCred = basic_cred(
                    InfobloxUser, 
                    name="Infoblox", 
                    type="PASSWORD", 
                    password=ArtifactoryPassword, 
                    default=False
                )

F5Password = read_local_file("f5_password")
F5User = read_local_file("f5_user")
F5Cred = basic_cred(
                    F5User, 
                    name="F5", 
                    type="PASSWORD", 
                    password=ArtifactoryPassword, 
                    default=False
                )

Centos74_Image = vm_disk_package(
                    name="centos7_generic", 
                    config_file="image_configs/centos74_disk.yaml"
                )


class MongoDBF5(Service):
    """Calm DSL Service"""

    service_name = CalmVariable.Simple.string(
        "mongodb",
    )
    service_port = CalmVariable.Simple.string(
        "27017",
    )
    f5_vs_ip = CalmVariable.Simple.string(
        "",
    )
    app_name = CalmVariable.Simple.string(
        "",
    )
    f5_virtual_name = CalmVariable.Simple.string(
        "",
    )

    @action
    def ProvisionF5():
        CalmTask.SetVariable.escript(
            name="Set App Name",
            filename="scripts/common/set_app_name.py",
            variables=["app_name"]
        )
        CalmTask.HTTP.post(
            name="Provision Infoblox Virtual Server Host Record",
            url="https://@@{infoblox_ip}@@/wapi/v2.7/record:host",
            body='{\n\t"name":"@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@.@@{domain_name}@@",\n\t"ipv4addrs":[{"ipv4addr":"func:nextavailableip:@@{network}@@"}]\n}',
            content_type="application/json",
            credential=InfobloxCred,
            status_mapping={200: True, 400: False},
            response_paths={"host_ref":"$"}
        )
        CalmTask.HTTP.get(
            name="Get Virtual Server IP Address",
            url="https://@@{infoblox_ip}@@/wapi/v2.7/@@{host_ref}@@",
            content_type="application/json",
            credential=InfobloxCred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_vs_ip":"$.ipv4addrs[0].ipv4addr", "f5_vs_ip_ref":"$.ipv4addrs[0]._ref"}
        )
        CalmTask.HTTP.post(
            name="Create F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool",
            body='{\n\t"loadBalancingMode": "@@{loadBalancingMode}@@",\n\t"monitor": "@@{monitor}@@",\n\t"name": "@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool",\n\t"description": "@@{service_name}@@ @@{app_name}@@ Pool."\n}',
            content_type="application/json",
            credential=F5Cred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_pool_name":"$.name"}
        )
        CalmTask.HTTP.post(
            name="Create F5 Virtual Server",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/virtual",
            body='{\n\t"destination": "/@@{partition}@@/@@{f5_vs_ip}@@:@@{service_port}@@",\n\t"sourceAddressTranslation": {"type": "automap"},\n\t"name": "@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-vs",\n\t"pool": "/@@{partition}@@/@@{f5_pool_name}@@",\n\t"description": "@@{service_name}@@ @@{app_name}@@ virtual server."\n}',
            content_type="application/json",
            credential=F5Cred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_virtual_name":"$.name"}
        )

    @action
    def DeprovisionF5():
        CalmTask.HTTP.delete(
            name="Delete F5 Virtual Server",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/virtual/~@@{partition}@@~@@{f5_virtual_name}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )
        CalmTask.HTTP.delete(
            name="Delete F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool/~@@{partition}@@~@@{f5_pool_name}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )
        CalmTask.HTTP.delete(
            name="Delete Host Record from Infoblox",
            url="https://@@{infoblox_ip}@@/wapi/v2.7/@@{host_ref}@@",
            content_type="text/html",
            credential=InfobloxCred,
            status_mapping={200: True, 400: True}
        )


class MongoDBF5Package(Package):
    """MongoDB F5 Package"""

    services = [ref(MongoDBF5)]

    @action
    def __install__():
        MongoDBF5.ProvisionF5(name="Provision F5")

    @action
    def __uninstall__():
        MongoDBF5.DeprovisionF5(name="Deprovision F5")


class MongoDBF5VM(Substrate):
    """MongoDB F5 VM"""

    provider_type = "EXISTING_VM"
    provider_spec = provider_spec({"address": "0.0.0.0"})
    readiness_probe = {
        "disabled": True,
        "delay_secs": "0",
        "connection_type": "SSH",
        "connection_port": 22,
        "credential": ref(NutanixCred),
    }


class MongoDBF5Deployment(Deployment):
    """
    MongoDB F5 Deployment 
    """

    packages = [ref(MongoDBF5Package)]
    substrate = ref(MongoDBF5VM)


class MongoDB(Service):
    """MongoDB service"""

    dependencies = [ref(MongoDBF5Deployment)]

    service_name = CalmVariable.Simple.string(
        "mongodb",
    )
    service_port = CalmVariable.Simple.string(
        "27017",
    )
    app_name = CalmVariable.Simple.string(
        "",
    )
    f5_virtual_name = CalmVariable.Simple.string(
        "@@{MongoDBF5.f5_virtual_name}@@",
    )

    @action
    def MongoDBInstallation():
        CalmTask.Exec.ssh(
            name="Intall MongoDB", 
            filename="scripts/mongodb/install_mongodb.sh", 
            cred=NutanixCred
        )

    @action
    def MongoDBLoad():
        CalmTask.Exec.ssh(
            name="Load Data", 
            filename="scripts/mongodb/load_data.sh", 
            cred=NutanixCred
        )
    
    @action
    def MongoDBF5ConfigurationAdd():
        CalmTask.SetVariable.escript(
            name="Set App Name",
            filename="scripts/mongodb/set_app_name.py",
            variables=["app_name","f5_virtual_name"]
        )
        CalmTask.HTTP.post(
            name="Add Member to F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool/~@@{partition}@@~@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool/members",
            body='{\n\t"description": "Node: @@{name}@@ is member of Pool: @@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool.",\n\t"name": "@@{name}@@:@@{service_port}@@",\n\t"address": "@@{address}@@"\n}',
            content_type="application/json",
            credential=F5Cred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_pool_name":"$.name"}
        )

    @action
    def MongoDBF5ConfigurationRemove():
        CalmTask.HTTP.delete(
            name="Remove Member from F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool/~@@{partition}@@~@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool/members/~@@{partition}@@~@@{name}@@:@@{service_port}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )
        CalmTask.HTTP.delete(
            name="Remove Node from F5",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/node/~@@{partition}@@~@@{name}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )

    @action
    def __create__():
        MongoDB.MongoDBF5ConfigurationAdd(name="Add Member to F5 Pool")

    @action
    def __delete__():
        MongoDB.MongoDBF5ConfigurationRemove(name="Remove Member to F5 Pool")


class MongoDBPackage(Package):
    """MongoDB Package"""

    services = [ref(MongoDB)]

    @action
    def __install__():
        MongoDB.MongoDBInstallation(name="MongoDB Installation")
        MongoDB.MongoDBLoad(name="MongoDB Load")


class MongoDBAhvVmResources(AhvVmResources):

    memory = 1
    vCPUs = 1
    cores_per_vCPU = 1
    disks = [
        AhvVmDisk.Disk.Scsi.cloneFromVMDiskPackage(Centos74_Image, bootable=True)
    ]
    nics = [
        AhvVmNic.NormalNic("vLAN_110"),
    ]
    boot_type = "BIOS"

    guest_customization = AhvVmGC.CloudInit(filename="scripts/guest_customizations/guest_cus.yaml")


class MongoDBAhvVm(AhvVm):

    resources = MongoDBAhvVmResources


class MongoDBVM(Substrate):
    """
    MongoDB AHV Spec
    Default 1 CPU & 1 GB of memory
    1 disks 
    """

    provider_spec = MongoDBAhvVm
    provider_spec.name = "mongodb-vm-@@{calm_unique}@@"

    os_type = "Linux"
    readiness_probe = {
        "disabled": False,
        "delay_secs": "60",
        "connection_type": "SSH",
        "connection_port": 22,
        "credential": ref(NutanixCred),
    }


class MongoDBDeployment(Deployment):
    """
    MongoDB deployment
    """

    packages = [ref(MongoDBPackage)]
    substrate = ref(MongoDBVM)
    min_replicas = "2"
    max_replicas = "5"


class NodeJSF5(Service):
    """Calm DSL Service"""

    service_name = CalmVariable.Simple.string(
        "nodejs",
    )
    service_port = CalmVariable.Simple.string(
        "3000",
    )
    f5_vs_ip = CalmVariable.Simple.string(
        "",
    )
    app_name = CalmVariable.Simple.string(
        "",
    )
    f5_virtual_name = CalmVariable.Simple.string(
        "",
    )

    @action
    def ProvisionF5():
        CalmTask.SetVariable.escript(
            name="Set App Name",
            filename="scripts/common/set_app_name.py",
            variables=["app_name"]
        )
        CalmTask.HTTP.post(
            name="Provision Infoblox Virtual Server Host Record",
            url="https://@@{infoblox_ip}@@/wapi/v2.7/record:host",
            body='{\n\t"name":"@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@.@@{domain_name}@@",\n\t"ipv4addrs":[{"ipv4addr":"func:nextavailableip:@@{network}@@"}]\n}',
            content_type="application/json",
            credential=InfobloxCred,
            status_mapping={200: True, 400: False},
            response_paths={"host_ref":"$"}
        )
        CalmTask.HTTP.get(
            name="Get Virtual Server IP Address",
            url="https://@@{infoblox_ip}@@/wapi/v2.7/@@{host_ref}@@",
            content_type="application/json",
            credential=InfobloxCred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_vs_ip":"$.ipv4addrs[0].ipv4addr", "f5_vs_ip_ref":"$.ipv4addrs[0]._ref"}
        )
        CalmTask.HTTP.post(
            name="Create F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool",
            body='{\n\t"loadBalancingMode": "@@{loadBalancingMode}@@",\n\t"monitor": "@@{monitor}@@",\n\t"name": "@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool",\n\t"description": "@@{service_name}@@ @@{app_name}@@ Pool."\n}',
            content_type="application/json",
            credential=F5Cred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_pool_name":"$.name"}
        )
        CalmTask.HTTP.post(
            name="Create F5 Virtual Server",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/virtual",
            body='{\n\t"destination": "/@@{partition}@@/@@{f5_vs_ip}@@:@@{service_port}@@",\n\t"sourceAddressTranslation": {"type": "automap"},\n\t"name": "@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-vs",\n\t"pool": "/@@{partition}@@/@@{f5_pool_name}@@",\n\t"description": "@@{service_name}@@ @@{app_name}@@ virtual server."\n}',
            content_type="application/json",
            credential=F5Cred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_virtual_name":"$.name"}
        )

    @action
    def DeprovisionF5():
        CalmTask.HTTP.delete(
            name="Delete F5 Virtual Server",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/virtual/~@@{partition}@@~@@{f5_virtual_name}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )
        CalmTask.HTTP.delete(
            name="Delete F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool/~@@{partition}@@~@@{f5_pool_name}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )
        CalmTask.HTTP.delete(
            name="Delete Host Record from Infoblox",
            url="https://@@{infoblox_ip}@@/wapi/v2.7/@@{host_ref}@@",
            content_type="text/html",
            credential=InfobloxCred,
            status_mapping={200: True, 400: True}
        )



class NodeJSF5Package(Package):
    """NodeJS F5 Package"""

    services = [ref(NodeJSF5)]

    @action
    def __install__():
        NodeJSF5.ProvisionF5(name="Provision F5")

    @action
    def __uninstall__():
        NodeJSF5.DeprovisionF5(name="Deprovision F5")


class NodeJSF5VM(Substrate):
    """NodeJS F5 VM"""

    provider_type = "EXISTING_VM"
    provider_spec = provider_spec({"address": "0.0.0.0"})
    readiness_probe = {
        "disabled": True,
        "delay_secs": "0",
        "connection_type": "SSH",
        "connection_port": 22,
        "credential": ref(NutanixCred),
    }


class NodeJSF5Deployment(Deployment):
    """
    NodeJS F5 Deployment 
    """

    packages = [ref(NodeJSF5Package)]
    substrate = ref(NodeJSF5VM)

class NodeJS(Service):
    """NodeJS service"""

    dependencies = [ref(NodeJSF5Deployment), ref(MongoDBDeployment)]

    service_name = CalmVariable.Simple.string(
        "nodejs",
    )
    service_port = CalmVariable.Simple.string(
        "3000",
    )
    app_name = CalmVariable.Simple.string(
        "",
    )
    f5_virtual_name = CalmVariable.Simple.string(
        "@@{NodeJSF5.f5_virtual_name}@@",
    )

    @action
    def NodeJSInstallation():
        CalmTask.Exec.ssh(
            name="Intall NodeJS", 
            filename="scripts/nodejs/install_nodejs.sh", 
            cred=NutanixCred
        )
    
    @action
    def NodeJSConfiguration():
        CalmTask.Exec.ssh(
            name="Configure NodeJS", 
            filename="scripts/nodejs/configure_nodejs.sh", 
            cred=NutanixCred
        )
    
    @action
    def NPMInstallation():
        CalmTask.Exec.ssh(
            name="Install NPM", 
            filename="scripts/nodejs/install_npm.sh", 
            cred=NutanixCred
        )
    
    @action
    def NodejsMongoInstallForTesting():
        CalmTask.Exec.ssh(
            name="Nodejs Install Mongo", 
            filename="scripts/nodejs/nodejs_install_mongo.sh", 
            cred=NutanixCred
        )

    @action
    def NodeJSF5ConfigurationAdd():
        CalmTask.SetVariable.escript(
            name="Set App Name",
            filename="scripts/nodejs/set_app_name.py",
            variables=["app_name","f5_virtual_name"]
        )
        CalmTask.HTTP.post(
            name="Add Member to F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool/~@@{partition}@@~@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool/members",
            body=' {\n"description": "Node: @@{name}@@ is member of Pool: @@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool.",\n\t"name": "@@{name}@@:@@{service_port}@@",\n\t"address": "@@{address}@@"\n}',
            content_type="application/json",
            credential=F5Cred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_pool_name":"$.name"}
        )

    @action
    def NodeJSF5ConfigurationRemove():
        CalmTask.HTTP.delete(
            name="Remove Member from F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool/~@@{partition}@@~@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool/members/~@@{partition}@@~@@{name}@@:@@{service_port}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )
        CalmTask.HTTP.delete(
            name="Remove Node from F5",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/node/~@@{partition}@@~@@{name}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )

    @action
    def __create__():
        NodeJS.NodeJSConfiguration(name="NodeJS Configuration")
        NodeJS.NodeJSF5ConfigurationAdd(name="Add Member to F5 Pool")
    
    @action
    def __delete__():
        NodeJS.NodeJSF5ConfigurationRemove(name="Remove Member to F5 Pool")


class NodeJSPackage(Package):
    """NodeJS Package"""

    services = [ref(NodeJS)]

    @action
    def __install__():
        NodeJS.NodeJSInstallation(name="NodeJS Installation")
        NodeJS.NodejsMongoInstallForTesting(name="Nodejs Mongo Install for Testing")


class NodeJSAhvVmResources(AhvVmResources):

    memory = 1
    vCPUs = 1
    cores_per_vCPU = 1
    disks = [
        AhvVmDisk.Disk.Scsi.cloneFromVMDiskPackage(Centos74_Image, bootable=True)
    ]
    nics = [
        AhvVmNic.NormalNic("vLAN_110"),
    ]
    boot_type = "BIOS"

    guest_customization = AhvVmGC.CloudInit(filename="scripts/guest_customizations/guest_cus.yaml")


class NodeJSAhvVm(AhvVm):

    resources = NodeJSAhvVmResources


class NodeJSVM(Substrate):
    """
    NodeJS AHV Spec
    Default 1 CPU & 1 GB of memory
    1 disks 
    """

    provider_spec = NodeJSAhvVm
    provider_spec.name = "nodejs-vm-@@{calm_unique}@@"

    os_type = "Linux"
    readiness_probe = {
        "disabled": False,
        "delay_secs": "60",
        "connection_type": "SSH",
        "connection_port": 22,
        "credential": ref(NutanixCred),
    }


class NodeJSDeployment(Deployment):
    """
    NodeJS deployment
    """

    packages = [ref(NodeJSPackage)]
    substrate = ref(NodeJSVM)
    min_replicas = "2"
    max_replicas = "5"


class NginxF5(Service):
    """Calm DSL Service"""

    service_name = CalmVariable.Simple.string(
        "nginx",
    )
    service_port = CalmVariable.Simple.string(
        "80",
    )
    f5_vs_ip = CalmVariable.Simple.string(
        "",
    )
    app_name = CalmVariable.Simple.string(
        "",
    )
    f5_virtual_name = CalmVariable.Simple.string(
        "",
    )

    @action
    def ProvisionF5():
        CalmTask.SetVariable.escript(
            name="Set App Name",
            filename="scripts/common/set_app_name.py",
            variables=["app_name"]
        )
        CalmTask.HTTP.post(
            name="Provision Infoblox Virtual Server Host Record",
            url="https://@@{infoblox_ip}@@/wapi/v2.7/record:host",
            body='{\n\t"name":"@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@.@@{domain_name}@@",\n\t"ipv4addrs":[{"ipv4addr":"func:nextavailableip:@@{network}@@"}]\n}',
            content_type="application/json",
            credential=InfobloxCred,
            status_mapping={200: True, 400: False},
            response_paths={"host_ref":"$"}
        )
        CalmTask.HTTP.get(
            name="Get Virtual Server IP Address",
            url="https://@@{infoblox_ip}@@/wapi/v2.7/@@{host_ref}@@",
            content_type="application/json",
            credential=InfobloxCred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_vs_ip":"$.ipv4addrs[0].ipv4addr", "f5_vs_ip_ref":"$.ipv4addrs[0]._ref"}
        )
        CalmTask.HTTP.post(
            name="Create F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool",
            body='{\n\t"loadBalancingMode": "@@{loadBalancingMode}@@",\n\t"monitor": "@@{monitor}@@",\n\t"name": "@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool",\n\t"description": "@@{service_name}@@ @@{app_name}@@ Pool."\n}',
            content_type="application/json",
            credential=F5Cred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_pool_name":"$.name"}
        )
        CalmTask.HTTP.post(
            name="Create F5 Virtual Server",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/virtual",
            body='{\n\t"destination": "/@@{partition}@@/@@{f5_vs_ip}@@:@@{service_port}@@",\n\t"sourceAddressTranslation": {"type": "automap"},\n\t"name": "@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-vs",\n\t"pool": "/@@{partition}@@/@@{f5_pool_name}@@",\n\t"description": "@@{service_name}@@ @@{app_name}@@ virtual server."\n}',
            content_type="application/json",
            credential=F5Cred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_virtual_name":"$.name"}
        )

    @action
    def DeprovisionF5():
        CalmTask.HTTP.delete(
            name="Delete F5 Virtual Server",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/virtual/~@@{partition}@@~@@{f5_virtual_name}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )
        CalmTask.HTTP.delete(
            name="Delete F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool/~@@{partition}@@~@@{f5_pool_name}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )
        CalmTask.HTTP.delete(
            name="Delete Host Record from Infoblox",
            url="https://@@{infoblox_ip}@@/wapi/v2.7/@@{host_ref}@@",
            content_type="text/html",
            credential=InfobloxCred,
            status_mapping={200: True, 400: True}
        )



class NginxF5Package(Package):
    """NodeJS F5 Package"""

    services = [ref(NginxF5)]

    @action
    def __install__():
        NginxF5.ProvisionF5(name="Provision F5")

    @action
    def __uninstall__():
        NginxF5.DeprovisionF5(name="Deprovision F5")


class NginxF5VM(Substrate):
    """Nginx F5 VM"""

    provider_type = "EXISTING_VM"
    provider_spec = provider_spec({"address": "0.0.0.0"})
    readiness_probe = {
        "disabled": True,
        "delay_secs": "0",
        "connection_type": "SSH",
        "connection_port": 22,
        "credential": ref(NutanixCred),
    }


class NginxF5Deployment(Deployment):
    """
    Nginx F5 Deployment 
    """

    packages = [ref(NginxF5Package)]
    substrate = ref(NginxF5VM)

class Nginx(Service):
    """Nginx service"""

    dependencies = [ref(NginxF5Deployment), ref(NodeJSDeployment)]

    service_name = CalmVariable.Simple.string(
        "nginx",
    )
    service_port = CalmVariable.Simple.string(
        "80",
    )
    app_name = CalmVariable.Simple.string(
        "",
    )
    f5_virtual_name = CalmVariable.Simple.string(
        "@@{NginxF5.f5_virtual_name}@@",
    )

    @action
    def NginxInstallation():
        CalmTask.Exec.ssh(
            name="Intall Nginx", 
            filename="scripts/nginx/install_nginx.sh", 
            cred=NutanixCred
        )
    
    @action
    def NginxConfiguration():
        CalmTask.Exec.ssh(
            name="Configure Base User", 
            filename="scripts/nginx/configure_nginx.sh", 
            cred=NutanixCred
        )
    
    @action
    def NginxF5ConfigurationAdd():
        CalmTask.SetVariable.escript(
            name="Set App Name",
            filename="scripts/nginx/set_app_name.py",
            variables=["app_name","f5_virtual_name"]
        )
        CalmTask.HTTP.post(
            name="Add Member to F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool/~@@{partition}@@~@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool/members",
            body=' {\n"description": "Node: @@{name}@@ is member of Pool: @@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool.",\n\t"name": "@@{name}@@:@@{service_port}@@",\n\t"address": "@@{address}@@"\n}',
            content_type="application/json",
            credential=F5Cred,
            status_mapping={200: True, 400: False},
            response_paths={"f5_pool_name":"$.name"}
        )

    @action
    def NginxF5ConfigurationRemove():
        CalmTask.HTTP.delete(
            name="Remove Member from F5 Pool",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/pool/~@@{partition}@@~@@{service_name}@@-@@{app_name}@@-@@{project_name}@@@@{build_number}@@-pool/members/~@@{partition}@@~@@{name}@@:@@{service_port}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )
        CalmTask.HTTP.delete(
            name="Remove Node from F5",
            url="https://@@{f5_ip}@@/mgmt/tm/ltm/node/~@@{partition}@@~@@{name}@@",
            content_type="text/html",
            credential=F5Cred,
            status_mapping={200: True, 404: True}
        )

    @action
    def __create__():
        Nginx.NginxConfiguration(name="Nginx Configuration")
        Nginx.NginxF5ConfigurationAdd(name="Add Member to F5 Pool")

    @action
    def __delete__():
        Nginx.NginxF5ConfigurationRemove(name="Remove Member to F5 Pool")


class NginxPackage(Package):
    """Nginx Package"""

    services = [ref(Nginx)]

    @action
    def __install__():
        Nginx.NginxInstallation(name="Nginx Installation")


class NginxAhvVmResources(AhvVmResources):

    memory = 1
    vCPUs = 1
    cores_per_vCPU = 1
    disks = [
        AhvVmDisk.Disk.Scsi.cloneFromVMDiskPackage(Centos74_Image, bootable=True)
    ]
    nics = [
        AhvVmNic.NormalNic("vLAN_110"),
    ]
    boot_type = "BIOS"

    guest_customization = AhvVmGC.CloudInit(filename="scripts/guest_customizations/guest_cus.yaml")


class NginxAhvVm(AhvVm):

    resources = NginxAhvVmResources


class NginxVM(Substrate):
    """
    Nginx AHV Spec
    Default 1 CPU & 1 GB of memory
    1 disks 
    """

    provider_spec = NginxAhvVm
    provider_spec.name = "nginx-vm-@@{calm_unique}@@"

    os_type = "Linux"
    readiness_probe = {
        "disabled": False,
        "delay_secs": "60",
        "connection_type": "SSH",
        "connection_port": 22,
        "credential": ref(NutanixCred),
    }


class NginxDeployment(Deployment):
    """
    Nginx deployment
    """

    packages = [ref(NginxPackage)]
    substrate = ref(NginxVM)
    min_replicas = "2"
    max_replicas = "5"



class Default(Profile):
    """
    Default Application Deployment VMs profile.
    """

    deployments = [
            MongoDBF5Deployment,
            MongoDBDeployment,
            NodeJSF5Deployment,
            NodeJSDeployment,
            NginxF5Deployment,
            NginxDeployment
            ]
    nutanix_public_key = CalmVariable.Simple.Secret(
        NutanixPublicKey, 
        label="Nutanix Public Key", 
        is_hidden=True 
    )
    domain_name = CalmVariable.Simple(
        DomainName,
        label="Domain Name",
        is_mandatory=True,
        runtime=True,
    )
    build_number = CalmVariable.Simple(
        "1",
        label="Build Number",
        is_mandatory=True,
        runtime=True,
    )
    project_name = CalmVariable.Simple.string(
        "devops",
        label="Project Name",
        is_mandatory=True,
        runtime=True,
    )
    cicd_app_name = CalmVariable.Simple.string(
        "cicddevelopergroup01",
        label="CICD Application Name",
        is_mandatory=True,
        runtime=True,
    )
    artifactory_ip = CalmVariable.Simple.string(
        "",
        label="Aritifactory IP",
        is_mandatory=True,
        runtime=True,
    )
    infoblox_ip = CalmVariable.Simple.string(
        InfobloxIP,
        label="Infoblox IP",
        is_mandatory=True,
        runtime=True,
    )
    f5_ip = CalmVariable.Simple.string(
        F5IP,
        label="F5 IP",
        is_mandatory=True,
        runtime=True,
    )
    network = CalmVariable.Simple.string(
        Network,
        label="Network",
        is_mandatory=True,
        runtime=True,
    )
    partition = CalmVariable.Simple.string(
        "Common",
        label="Partition Name",
        is_mandatory=True,
        runtime=True,
    )
    loadBalancingMode = CalmVariable.Simple.string(
        "observed-member",
        label="Load Balancing Mode",
        is_mandatory=True,
        runtime=True,
    )
    monitor = CalmVariable.Simple.string(
        "tcp",
        label="Monitor Protocol",
        is_mandatory=True,
        runtime=True,
    )
    source_address_translation_type = CalmVariable.Simple.string(
        "automap",
        label="Source Address Translation Type",
        is_mandatory=True,
        runtime=True,
    )



    @action
    def ScaleOutNginx():
        name = "Scale Out Nginx"
        COUNT = CalmVariable.Simple.int("1", is_mandatory=True, runtime=True) 
        CalmTask.Scaling.scale_out(
            "@@{COUNT}@@", 
            target=ref(NginxDeployment), 
            name="Scale Out Nginx"
        )

    @action
    def ScaleInNginx():
        name = "Scale In Nginx"
        COUNT = CalmVariable.Simple.int("1", is_mandatory=True, runtime=True) 
        CalmTask.Scaling.scale_in(
            "@@{COUNT}@@", 
            target=ref(NginxDeployment), 
            name="Scale In Nginx"
        )

    @action
    def ScaleOutNodeJS():
        name = "Scale Out NodeJS"
        COUNT = CalmVariable.Simple.int("1", is_mandatory=True, runtime=True) 
        CalmTask.Scaling.scale_out(
            "@@{COUNT}@@", 
            target=ref(NodeJSDeployment), 
            name="Scale Out NodeJS"
        )

    @action
    def ScaleInNodeJS():
        name = "Scale In NodeJS"
        COUNT = CalmVariable.Simple.int("1", is_mandatory=True, runtime=True) 
        CalmTask.Scaling.scale_in(
            "@@{COUNT}@@", 
            target=ref(NodeJSDeployment), 
            name="Scale In NodeJS"
        )

    @action
    def ScaleOutMongoDB():
        name = "Scale Out MongoDB"
        COUNT = CalmVariable.Simple.int("1", is_mandatory=True, runtime=True) 
        CalmTask.Scaling.scale_out(
            "@@{COUNT}@@", 
            target=ref(MongoDBDeployment), 
            name="Scale Out MongoDB"
        )

    @action
    def ScaleInMongoDB():
        name = "Scale In MongoDB"
        COUNT = CalmVariable.Simple.int("1", is_mandatory=True, runtime=True) 
        CalmTask.Scaling.scale_in(
            "@@{COUNT}@@", 
            target=ref(MongoDBDeployment), 
            name="Scale In MongoDB"
        )

    @action
    def DeploytoPrimaryF5VirtualServer():
        name="Deploy to Primary F5 Virtual Server",
        CalmTask.Exec.escript(
            name="Set F5 Virtual Server Resource",
            filename="scripts/nginxf5/set_f5_vs_resource.py",
            target=ref(NginxF5),
        )

class ApplicationDeploymentF5(Blueprint):
    """Application Deployment VMs with F5 and Infoblox Integration blueprint"""

    profiles = [Default]
    substrates = [
            MongoDBF5VM,
            MongoDBVM,
            NodeJSF5VM,
            NodeJSVM,
            NginxF5VM,
            NginxVM
            ]
    services = [
            MongoDBF5,
            MongoDB,
            NodeJSF5,
            NodeJS,
            NginxF5,
            Nginx
            ]
    packages = [
            MongoDBF5Package,
            MongoDBPackage,
            NodeJSF5Package,
            NodeJSPackage,
            NginxF5Package,
            NginxPackage,
            Centos74_Image
            ]
    credentials = [NutanixCred,
            ArtifactoryCred,
            InfobloxCred,
            F5Cred
            ]


def main():
    print(ApplicationDeploymentVMs.json_dumps(pprint=True))


if __name__ == "__main__":
    main()
