"""
Application Deployment K8s Containers Blueprint
"""

from calm.dsl.builtins import ref, basic_cred
from calm.dsl.builtins import action
from calm.dsl.builtins import CalmTask
from calm.dsl.builtins import CalmVariable
from calm.dsl.builtins import Service, Package, Substrate
from calm.dsl.builtins import Deployment, Profile, Blueprint, PODDeployment
from calm.dsl.builtins import read_provider_spec, read_spec, read_local_file

NutanixPassword = read_local_file("nutanix_password")
NutanixUser = read_local_file("nutanix_user")
NutanixCred = basic_cred(
                    NutanixUser,
                    name="Nutanix",
                    type="PASSWORD",
                    password=NutanixPassword,
                    default=True
                )

class mongo_db_service(Service):
    @action
    def __create__():
        CalmTask.HTTP.get(
            name="Get Data",
            url="@@{data_url}@@/peaks-demo-app/master/db/mongo/data/peaksdata.json",
            content_type="application/json",
            status_mapping={200: True},
            response_paths={"insert_script":"$.entities"}
        )
        CalmTask.Exec.ssh(
            name="Load MongoDB Data",
            filename="scripts/mongodb/load_data.sh",
            cred=NutanixCred
        )


class mongo_db_deployment(PODDeployment):
    """Mongo DB Deployment"""

    containers = [mongo_db_service]
    deployment_spec = read_spec("mongo_deployment.yaml")
    service_spec = read_spec("mongo_service.yaml")


class nodejs_service(Service):
    dependencies = [ref(mongo_db_service)]


class nodejs_deployment(PODDeployment):
    """NodeJS Deployment"""

    containers = [nodejs_service]
    deployment_spec = read_spec("nodejs_deployment.yaml")
    service_spec = read_spec("nodejs_service.yaml")


class nginx_service(Service):
    dependencies = [ref(nodejs_service)]


class nginx_deployment(PODDeployment):
    """Nginx Deployment"""

    containers = [nginx_service]
    deployment_spec = read_spec("nginx_deployment.yaml")
    service_spec = read_spec("nginx_service.yaml")


class Default(Profile):
    """Default application profile with variables"""

    docker_registry = CalmVariable.Simple(
        "", 
        label="Docker Registry",
        is_mandatory=True,
        runtime=True,
    )
    project_name = CalmVariable.Simple(
        "k8sdemo", 
        label="Project Name",
        is_mandatory=True,
        runtime=True,
    )
    cicd_app_name = CalmVariable.Simple(
        "cicdenvironmentdevelopmentgroup01", 
        label="Application Name",
        is_mandatory=True,
        runtime=True,
    )
    build_number = CalmVariable.Simple(
        "6", 
        label="Build Number",
        is_mandatory=True,
        runtime=True,
    )
    data_url = CalmVariable.Simple(
        "https://raw.githubusercontent.com/nutanixdev", 
        label="Data URL",
        is_mandatory=True,
        runtime=True,
    )


    deployments = [
        mongo_db_deployment,
        nodejs_deployment,
        nginx_deployment,
    ]


class ApplicationDeploymentK8sContainers(Blueprint):
    """Application Deployment K8s Containers Blueprint"""

    credentials = [NutanixCred]
    services = [mongo_db_service,
                nodejs_service,
                nginx_service]
    profiles = [Default]


def main():
    print(ApplicationDeploymentK8sContainers.json_dumps(pprint=True))


if __name__ == "__main__":
    main()
