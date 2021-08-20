.. _Observation:

CybORG Observation Design
=========================

The observation space in CybORG is set up as a complex dictionary data structure that also features methods to add information to this data structure.

The dictionary always contains a trinary value for a ``success`` entry that indicates if the previous action was successful, unsuccessful or had an unknown result.

The other keys within the observation are host IDs and are string values that are used to collect information that is believed to originate from a single host. Examples of host IDs are IP addresses or hostnames. These host ID is not guaranteed to represent any information and for the agents to infer information from the environment.


Each host ID also has a dictionary structure within that has information collected about the host. These entries have keys:

* Sessions
* Files
* Interfaces
* Processes
* Users
* System Info

An example of the observation data structure is shown here:

.. code-block:: python

    {
        "Success": TrinaryEnum,
        "<hostid0>" : {
            "Processes":[
                {"PID": int
                "PPID": int
                "Process name": str
                "Known Process": ProcessNameEnum
                "Program name": FileNameEnum
                "Username": str
                "Path": str
                "Known Path": PathEnum
                "Connections": {
                    "local_port": int
                    "local_address": IPv4Address
                    "Remote port": int
                    "Remote Address": IPv4Address
                    "Application Protocol": ApplicationProtocolEnum,
                    "Transport Protocol": TransportProtocolEnum
                }
                "status": ProcessStateEnum
                "type": ProcessTypeEnum
                "version": ProcessVersionEnum
                "vulnerabilities": [VulnerabilityEnum]},
                ...
            ],
            "System info":{
                    "Hostname": str,
                    "OSType": OperatingSystemTypeEnum,
                    "OSDistribution": OperatingSystemDistributionEnum,
                    "OSVersion": OperatingSystemVersionEnum,
                    "OSKernelVersion": OperatingSystemKernelVersionEnum,
                    "Patches": [OperatingSystemPatchEnum],
                    "Architecture": ArchitectureEnum
            },
            "Interfaces":[
                {"Interface": str,
                "IP Address" : IPv4Address,
                "Subnet": IPv4Subnet
                },
                ...
            ],
            "User Info":[
                    {"Username" : str,
                    "UID" : int,
                    "Password" : str,
                    "Password Hash" : str,
                    "Password Hash Type" : PasswordHashType,
                    "Groups" : [
                        {"Group Name" : str,
                         "Builtin Group" : BuiltInGroupsEnum,
                         "GID" : int},
                        ...
                    ]
                },
                ...
            ],
            "Files":[
                {"Name" : str,
                "Known File" : FileNameEnum,
                "Group" : str,
                "GroupPermission" : int,
                "User" : str,
                "UserPermission" : int,
                "DefaultPermission" : int
                "Path": str,
                "Known Path": PathEnum,
                "Vendor": VendorEnum,
                "Version": str
                },
                ...
            ],
            "Sessions": [
                {"ID": int,
                "Username": str,
                "Timeout": int,
                "PID": int,
                "Type": SessionTypeEnum,
                "Agent": str}
            ]
        }
    ...
    }

Here is an example of how an action will utilise the necessary keys within this data structure format. This example shows a successful port scan and revealing an open port.

.. code-block:: python

    {"success": True,
    str(scanned_ip_address): {
        'Interface': [{'IP Address': scanned_ip_address}],
        'Processes': [{
            'Connections': [{
                'local_address': scanned_ip_address,
                'local_port': 22}]}]},
    }

