import uuid
import tempfile
import shutil
import os
from ignition.service.resourcedriver import InfrastructureNotFoundError, InvalidDriverFilesError, InvalidRequestError
from ignition.model.references import FindReferenceResponse, FindReferenceResult
from ignition.model.associated_topology import AssociatedTopology
from ignition.model.lifecycle import LifecycleExecution, LifecycleExecuteResponse
from ignition.utils.file import DirectoryTree
from osvimdriver.service.resourcedriver import ResourceDriverHandler, StackNameCreator, PropertiesMerger, AdditionalResourceDriverProperties
from osvimdriver.service.tosca import ToscaValidationError
from osvimdriver.tosca.discover import DiscoveryResult, NotDiscoveredError
from osvimdriver.openstack.heat.driver import StackNotFoundError
from osvimdriver.openstack.environment import OpenstackDeploymentLocationTranslator
from ignition.utils.propvaluemap import PropValueMap

class OSConnector:
    resource_driver_config = AdditionalResourceDriverProperties()

    def setupResourceDriver(self):
        driver = ResourceDriverHandler(OpenstackDeploymentLocationTranslator(), resource_driver_config=self.resource_driver_config, heat_translator_service=None, tosca_discovery_service=None)
        return driver

class ConnectionRunner:

    def __create_mock_driver_files(self):
        heat_driver_files_path = tempfile.mkdtemp()
        self.heat_template = 'heat_template'
        with open(os.path.join(heat_driver_files_path, 'heat.yaml'), 'w') as f:
            f.write(self.heat_template)
        tosca_driver_files_path = tempfile.mkdtemp()
        self.tosca_template = 'tosca_template'
        self.tosca_template_path = os.path.join(tosca_driver_files_path, 'tosca.yaml')
        with open(self.tosca_template_path, 'w') as f:
            f.write(self.tosca_template)
        self.discover_template = 'discover_template'
        with open(os.path.join(tosca_driver_files_path, 'discover.yaml'), 'w') as f:
            f.write(self.discover_template)
        self.heat_driver_files = DirectoryTree(heat_driver_files_path)
        self.tosca_driver_files = DirectoryTree(tosca_driver_files_path)    


    def __resource_properties(self):
        props = {}
        props['propA'] = {'type': 'string', 'value': 'valueA'}
        props['propB'] = {'type': 'string', 'value': 'valueB'}
        return PropValueMap(props)

    def __system_properties(self):
        props = {}
        props['resourceId'] = '123'
        props['resourceName'] = 'TestResource'
        return PropValueMap(props)        

    def __created_associated_topology(self, adopt=False):
        associated_topology = AssociatedTopology()
        associated_topology.add_entry('InfrastructureStack', '1', 'Openstack')
        if adopt==True:
            associated_topology.add_entry('adoptTopology', '2c8d23db-2974-405a-9f16-da1e148dd469', 'Openstack')
            #associated_topology.add_entry('adoptTopology', '41589088-72d7-4232-a6cb-3c74392ff29f', 'Openstack')
            #associated_topology.add_entry('adoptTopology', '48c965cd-e846-4e92-ab63-493babaecf25', 'Openstack')
        return associated_topology


    def __deployment_location(self):
        return {
            "name": "openstack-yeast",
            "properties": {
                "os_auth_project_name": "bluesquad",
                "os_auth_project_domain_name": "default",
                "os_auth_username": "admin",
                "os_auth_password": "password", 
                "os_auth_user_domain_name": "Default",
                "os_auth_api": "identity/v3",
                "os_api_url": "http://9.46.89.226",
                "os_auth_project_id": "701600a059af40e1865a3c494288712a"},
                # "os_auth_project_name": "Brownfield",
                # "os_auth_project_domain_name": "default",
                # "os_auth_username": "admin",
                # "os_auth_password": "password", 
                # "os_auth_user_domain_name": "Default",
                # "os_auth_api": "identity/v3",
                # "os_api_url": "http://9.46.87.109",
                # "os_auth_project_id": "de1a51da2de142caa35de6425108b9b6"},                
            "type": "Openstack"
        }             

    def doIt(self):
        connectTest = OSConnector()
        driver = connectTest.setupResourceDriver()

        self.__create_mock_driver_files()       
        self.resource_properties = self.__resource_properties()
        self.system_properties = self.__system_properties()        
        self.created_adopted_topology = self.__created_associated_topology(True)
        self.deployment_location = self.__deployment_location()

        print(str(self.created_adopted_topology))
        executionRequestResponse = driver.execute_lifecycle("Adopt", self.heat_driver_files, self.system_properties, self.resource_properties, {}, self.created_adopted_topology, self.deployment_location)

        print("executionRequestResponse.request_id = "+str(executionRequestResponse.request_id))
        executionResponse = driver.get_lifecycle_execution(executionRequestResponse.request_id, self.deployment_location)
        
        print("response: "+executionResponse.status)
        print("response outputs: "+str(executionResponse.outputs))
        print("request ID: "+str(executionResponse.request_id))

print("start: " + __name__)
runner = ConnectionRunner()
runner.doIt()
