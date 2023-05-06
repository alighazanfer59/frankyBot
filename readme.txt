BTC 4H trade with 50$
BTC daily trade with 75$
ETH 4h Trade with 100$
ETH Daily trade with 125$
QNT 4H trade with 150$
QNT Daily trade with 175$


API call to run instance
{
  "MaxCount": 1,
  "MinCount": 1,
  "ImageId": "ami-052f483c20fa1351a",
  "InstanceType": "t2.micro",
  "KeyName": "frankyBot",
  "EbsOptimized": false,
  "BlockDeviceMappings": [
    {
      "DeviceName": "/dev/xvda",
      "Ebs": {
        "Encrypted": false,
        "DeleteOnTermination": true,
        "Iops": 3000,
        "SnapshotId": "snap-05995f21734667fb6",
        "VolumeSize": 8,
        "VolumeType": "gp3",
        "Throughput": 125
      }
    }
  ],
  "NetworkInterfaces": [
    {
      "DeviceIndex": 0,
      "AssociatePublicIpAddress": true,
      "Groups": [
        "<groupId of the new security group created below>"
      ]
    }
  ],
  "TagSpecifications": [
    {
      "ResourceType": "instance",
      "Tags": [
        {
          "Key": "Name",
          "Value": "frankyBot"
        }
      ]
    }
  ],
  "PrivateDnsNameOptions": {
    "HostnameType": "ip-name",
    "EnableResourceNameDnsARecord": true,
    "EnableResourceNameDnsAAAARecord": false
  }
}