# Copyright (c) 2012 Trend Micro, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

from sclib.resultset import ResultSet
from sclib.sc.scobject import SCObject
from sclib.sc.device import Device
from sclib.sc.provider import Provider
from xml.etree import ElementTree

class Instance(SCObject):
    def __init__(self, connection=None):
        pass

    
class VirtualMachine(SCObject):
    #===========================================================================
    # present vm object
    #===========================================================================
    
    # Required fields
    Required = ['imageGUID', 'imageName', 'autoProvision', 'SecurityGroupGUID', 'imageDescription']
    
    # Present valid vm object attributes, not inner objects
    ValidAttributes = [ 'SecurityGroupGUID', 'autoProvision',
                        'detectedKeyCount', 'encryptedDeviceCount', 'encryptingDeviceCount', 'href',
                        'imageGUID', 'imageID', 'imageName', 
                        'instanceGUID','instanceID', 'lastModified', 
                        'nonEncryptedDeviceCount', 'pendingDeviceCount']
    
    
    def __init__(self, connection):
        SCObject.__init__(self, connection)
        #-----------------------------------------------------------------------
        # # Attributes
        #-----------------------------------------------------------------------
        self.SecurityGroupGUID = None
        self.autoProvision = None
        self.detectedKeyCount = None
        self.encryptedDeviceCount = None
        self.encryptingDeviceCount = None
        self.href = None
        self.imageGUID = None
        self.imageID = None
        self.imageName = None
        self.instanceGUID = None
        self.instanceID = None
        self.lastModified = None
        self.nonEncryptedDeviceCount = None
        self.pendingDeviceCount = None
        #-----------------------------------------------------------------------
        # # elements
        #-----------------------------------------------------------------------
        self.imageDescription = None
        #-----------------------------------------------------------------------
        # # Inner objects
        #-----------------------------------------------------------------------
        self.provider = None
        self.platform = None
        self.securecloudAgent = None
        self.devices = None
        
        pass

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'vm':
            # keep all attributes
            for key, value in attrs.items():
                setattr(self, key, value)
        elif name == 'provider':
            self.provider = Provider(connection)
            self.provider.startElement(name, attrs, connection)
            return self.provider
        elif name == 'securecloudAgent':
            self.securecloudAgent = SCAgent(connection)
            self.securecloudAgent.startElement(name, attrs, connection)
            return self.securecloudAgent
        elif name == 'devices':
            self.devices = ResultSet([('device', Device)])
            self.devices.name = name
            return self.devices
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'platform':
            self.platform = value
        elif name == 'imageDescription':
            self.imageDescription = value
        else:
            setattr(self, name, value)
            
    def buildElements(self):

        vm = ElementTree.Element('vm')
        
        # build attributes
        for e in self.ValidAttributes:
            if getattr(self, e): vm.attrib[e] = getattr(self, e)

        if self.imageDescription:
            description = ElementTree.SubElement(vm, "imageDescription")
            description.text = self.imageDescription

        # append inner objects
        if getattr(self, 'provider'): vm.append( self.provider.buildElements() )
        if getattr(self, 'platform'): vm.append( self.platform.buildElements() )
        if getattr(self, 'securecloudAgent'): vm.append( self.securecloudAgent.buildElements() )
        if getattr(self, 'devices'): vm.append( self.devices.buildElements() )
            
        return vm

    def _update(self, updated):
        self.__dict__.update(updated.__dict__)

    # ----- functions start 

    def update(self):
        action = 'vm/%s/' % self.imageGUID
        data = self.tostring()
        updated = self.connection.get_object(action, VirtualMachine, data=data, method='POST')
        if updated:
            self._update(updated)
            return self
        
        return updated
    
    def delete(self):
        #-----------------------------------------------------------------------
        # delete vm itself
        #-----------------------------------------------------------------------
        action = 'vm/%s/' % self.imageGUID
        return self.connection.get_status(action, method='DELETE')

    def listDevices(self):
        #-----------------------------------------------------------------------
        # list all devices
        #-----------------------------------------------------------------------
        action = 'vm/%s/device/' % self.imageGUID
        return self.connection.get_list(action, [('device', Device)])

    
    def deleteDevice(self, deviceID):
        #-----------------------------------------------------------------------
        # delete device inside a virtual machine
        #-----------------------------------------------------------------------
        ':deviceID the targe device to be delete in a virtual machine'
        
        action = 'vm/%s/device/%s/' % (self.imageGUID, deviceID)
        return self.connection.get_status(action, method='DELETE')
        


class SCAgent(SCObject):
    
    # Present valid vm object attributes, not inner objects
    ValidAttributes = ['agentStatus', 'agentVersion']

    def __init__(self, connection):
        # member information
        self.agentStatus = None
        self.agentVersion = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'securecloudAgent':
            for key, value in attrs.items():
                setattr(self, key, value)
            return self
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)
            
    def buildElements(self):
        agent = ElementTree.Element('securecloudAgent')
        if self.agentStatus: agent.attrib['agentStatus'] = self.agentStatus
        if self.agentVersion: agent.attrib['agentVersion'] = self.agentVersion
        return agent

class Image(SCObject):

    # Present valid vm object attributes, not inner objects
    ValidAttributes = ['id', 'msUID', 'href']

    def __init__(self, connection):
        # member information
        self.id = None
        self.msUID = None
        self.href = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'image':
            # keep all attributes
            for key, value in attrs.items():
                setattr(self, key, value)
            return self
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)
            
    def buildElements(self):
        agent = ElementTree.Element('image')
        #-----------------------------------------------------------------------
        # build attributes
        #-----------------------------------------------------------------------
        for e in self.ValidAttributes:
            if getattr(self, e): agent.attrib[e] = getattr(self, e)

        return agent

    
    
    