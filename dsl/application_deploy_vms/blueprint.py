"""
CALM DSL Application Deployment VMs Blueprint

"""
import os
from calm.dsl.builtins import *
from calm.dsl.config import get_context

ContextObj = get_context()
init_data = ContextObj.get_init_config()

if file_exists(os.path.join(init_data["LOCAL_DIR"]["location"], "pc_instance_ip")):
    PCInstanceIP = read_local_file("pc_instance_ip")
else:
    PCInstanceIP = ""

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

PrismCentralPassword = read_local_file("prism_central_password")
PrismCentralUser = read_local_file("prism_central_user")
PrismCentralCred = basic_cred(
                    PrismCentralUser, 
                    name="Prism Central User", 
                    type="PASSWORD", 
                    password=PrismCentralPassword, 
                    default=False
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

Centos74_Image = vm_disk_package(
                    name="centos7_generic", 
                    config_file="image_configs/centos74_disk.yaml"
                )


class MongoDB(Service):
    name = "Mongo DB"

    @action
    def MongoDBInstallation(name="Mongo DB Installation"):
        CalmTask.Exec.ssh(
            name="Intall MongoDB", 
            filename="scripts/mongodb/install_mongodb.sh", 
            cred=NutanixCred
        )

    @action
    def MongoDBLoad(name="Mongo DB Load"):
        CalmTask.Exec.ssh(
            name="Load Data", 
            filename="scripts/mongodb/load_data.sh", 
            cred=NutanixCred
        )
    

class MongoDBPackage(Package):
    name = "Mongo DB Package"

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
        AhvVmNic.NormalNic("vLAN_115"),
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

    name = "Mongo DB VM"

    provider_spec = MongoDBAhvVm
    provider_spec.name = "mongodb-vm-@@{calm_unique}@@"

    os_type = "Linux"
    readiness_probe = {
        "disabled": False,
        "delay_secs": "15",
        "retries": "10",
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
    min_replicas = "1"
    max_replicas = "1"


class NodeJS(Service):
    name = "NodeJS"

    dependencies = [ref(MongoDBDeployment)]

    @action
    def NodeJSInstallation(name="NodeJS Installation"):
        CalmTask.Exec.ssh(
            name="Intall NodeJS", 
            filename="scripts/nodejs/install_nodejs.sh", 
            cred=NutanixCred
        )
    
    @action
    def NodeJSConfiguration(name="NodeJS Configuration"):
        CalmTask.Exec.ssh(
            name="Configure NodeJS", 
            filename="scripts/nodejs/configure_nodejs.sh", 
            cred=NutanixCred
        )
    
    @action
    def NPMInstallation(name="NPM Installation"):
        CalmTask.Exec.ssh(
            name="Install NPM", 
            filename="scripts/nodejs/install_npm.sh", 
            cred=NutanixCred
        )
    
    @action
    def NodejsMongoInstallForTesting(name="NodeJS Mongo DB Installation For Testing"):
        CalmTask.Exec.ssh(
            name="Nodejs Install Mongo", 
            filename="scripts/nodejs/nodejs_install_mongo.sh", 
            cred=NutanixCred
        )

    @action
    def __create__():
        NodeJS.NodeJSConfiguration(name="NodeJS Configuration")
    

class NodeJSPackage(Package):
    name = "NodeJS Package"

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
        AhvVmNic.NormalNic("vLAN_115"),
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

    name = "NodeJS VM"

    provider_spec = NodeJSAhvVm
    provider_spec.name = "nodejs-vm-@@{calm_unique}@@"

    os_type = "Linux"
    readiness_probe = {
        "disabled": False,
        "delay_secs": "15",
        "retries": "10",
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
    min_replicas = "1"
    max_replicas = "1"


class Nginx(Service):
    name = "Nginx"

    dependencies = [ref(NodeJSDeployment)]

    @action
    def NginxInstallation(name="Nginx Installation"):
        CalmTask.Exec.ssh(
            name="Intall Nginx", 
            filename="scripts/nginx/install_nginx.sh", 
            cred=NutanixCred
        )
    
    @action
    def NginxConfiguration(name="Nginx Configuration"):
        CalmTask.Exec.ssh(
            name="Configure Base User", 
            filename="scripts/nginx/configure_nginx.sh", 
            cred=NutanixCred
        )
    
    @action
    def __create__():
        Nginx.NginxConfiguration(name="Nginx Configuration")


class NginxPackage(Package):
    name = "Nginx Package"

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
        AhvVmNic.NormalNic("vLAN_115"),
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

    name = "Nginx VM"

    provider_spec = NginxAhvVm
    provider_spec.name = "nginx-vm-@@{calm_unique}@@"

    os_type = "Linux"
    readiness_probe = {
        "disabled": False,
        "delay_secs": "15",
        "retries": "10",
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
    min_replicas = "1"
    max_replicas = "1"



class Default(Profile):
    """
    Default Application Deployment VMs profile.
    """

    deployments = [
            MongoDBDeployment,
            NodeJSDeployment,
            NginxDeployment
            ]
    nutanix_public_key = CalmVariable.Simple.Secret(
        NutanixPublicKey, 
        label="Nutanix Public Key", 
        is_hidden=True, 
        is_mandatory=True, 
        runtime=True,
        description="SSH public key for the Nutanix user."
    )
    domain_name = CalmVariable.Simple(
        DomainName,
        label="Domain Name",
        is_mandatory=True,
        runtime=True,
        description="Domain name used as suffix for FQDN. Entered similar to 'test.lab' or 'lab.local'."
    )
    build_number = CalmVariable.Simple(
        "1",
        label="Build Number",
        is_mandatory=True,
        runtime=True,
        description="Jenkins build number. This is passed by Jenkins when called via the pipeline."
    )
    pc_instance_ip = CalmVariable.Simple.string(
        PCInstanceIP,
        label="Prism Central IP",
        is_mandatory=True,
        runtime=True,
        description="IP address of the Prism Central instance that manages this Calm instance."
    )
    project_name = CalmVariable.Simple.string(
        "devops",
        label="Project Name",
        is_mandatory=True,
        runtime=True,
        description="Project name in Gitolite, Artifactory and the pipeline in Jenkins. This is passed by Jenkins when called via the pipeline."
    )
    artifactory_ip = CalmVariable.Simple.string(
        "",
        label="Aritifactory IP",
        is_mandatory=True,
        runtime=True,
        description="IP address of the Artifactory instance. This is passed by Jenkins when called via the pipeline."
    )


    @action
    def ScaleOutNginx(name="Scale Out Nginx"):
        COUNT = CalmVariable.Simple.int("1", is_mandatory=True, runtime=True) 
        CalmTask.Scaling.scale_out(
            "@@{COUNT}@@", 
            target=ref(NginxDeployment), 
            name="Scale Out Nginx"
        )

    @action
    def ScaleInNginx(name="Scale In Nginx"):
        COUNT = CalmVariable.Simple.int("1", is_mandatory=True, runtime=True) 
        CalmTask.Scaling.scale_in(
            "@@{COUNT}@@", 
            target=ref(NginxDeployment), 
            name="Scale In Nginx"
        )


class ApplicationDeploymentVMs(Blueprint):
    """Application Deployment VMs  blueprint"""

    profiles = [Default]
    substrates = [
            MongoDBVM,
            NodeJSVM,
            NginxVM
            ]
    services = [
            MongoDB,
            NodeJS,
            Nginx
            ]
    packages = [
            MongoDBPackage,
            NodeJSPackage,
            NginxPackage,
            Centos74_Image
            ]
    credentials = [
            NutanixCred,
            PrismCentralCred,
            ArtifactoryCred
            ]


def main():
    print(ApplicationDeploymentVMs.json_dumps(pprint=True))


if __name__ == "__main__":
    main()
