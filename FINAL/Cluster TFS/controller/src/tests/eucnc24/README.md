# DataPlane-in-a-Box - Control an Emulated DataPlane through TeraFlowSDN

## Emulated DataPlane Deployment
- ContainerLab
- Scenario
- Descriptor

## TeraFlowSDN Deployment
```bash
cd ~/tfs-ctrl
source dataplane-in-a-box/deploy_specs.sh
./deploy/all.sh
```

# ContainerLab - Arista cEOS - Commands

## Download and install ContainerLab
```bash
sudo bash -c "$(curl -sL https://get.containerlab.dev)" -- -v 0.48.6
```

## Download Arista cEOS image and create Docker image
```bash
cd ~/tfs-ctrl/dataplane-in-a-box
docker import arista/cEOS64-lab-4.31.2F.tar ceos:4.31.2F
```

## Deploy scenario
```bash
cd ~/tfs-ctrl/dataplane-in-a-box
sudo containerlab deploy --topo arista.clab.yml
```

## Inspect scenario
```bash
cd ~/tfs-ctrl/dataplane-in-a-box
sudo containerlab inspect --topo arista.clab.yml
```

## Destroy scenario
```bash
cd ~/tfs-ctrl/dataplane-in-a-box
sudo containerlab destroy --topo arista.clab.yml
sudo rm -rf clab-arista/ .arista.clab.yml.bak
```

## Access cEOS Bash
```bash
docker exec -it clab-arista-r1 bash
```

## Access cEOS CLI
```bash
docker exec -it clab-arista-r1 Cli
docker exec -it clab-arista-r2 Cli
```

## Configure ContainerLab clients
```bash
docker exec -it clab-arista-client1 bash
    ip address add 192.168.1.10/24 dev eth1
    ip route add 192.168.2.0/24 via 192.168.1.1
    ip route add 192.168.3.0/24 via 192.168.1.1
    ping 192.168.2.10
    ping 192.168.3.10

docker exec -it clab-arista-client2 bash
    ip address add 192.168.2.10/24 dev eth1
    ip route add 192.168.1.0/24 via 192.168.2.1
    ip route add 192.168.3.0/24 via 192.168.2.1
    ping 192.168.1.10
    ping 192.168.3.10

docker exec -it clab-arista-client3 bash
    ip address add 192.168.3.10/24 dev eth1
    ip route add 192.168.2.0/24 via 192.168.3.1
    ip route add 192.168.3.0/24 via 192.168.3.1
    ping 192.168.2.10
    ping 192.168.3.10
```

## Install gNMIc
```bash
sudo bash -c "$(curl -sL https://get-gnmic.kmrd.dev)"
```

## gNMI Capabilities request
```bash
gnmic --address clab-arista-wan1 --port 6030 --username admin --password admin --insecure capabilities
```

## gNMI Get request
```bash
gnmic --address clab-arista-wan1 --port 6030 --username admin --password admin --insecure --encoding json_ietf get --path / > wan1.json
gnmic --address clab-arista-wan1 --port 6030 --username admin --password admin --insecure --encoding json_ietf get --path /interfaces/interface > wan1-ifaces.json
```

## gNMI Set request
```bash
#gnmic --address clab-arista-wan1 --port 6030 --username admin --password admin --insecure --encoding json_ietf set --update-path /system/config/hostname --update-value srl11
#gnmic --address clab-arista-wan1 --port 6030 --username admin --password admin --insecure --encoding json_ietf get --path /system/config/hostname
```

## Subscribe request
```bash
gnmic --address clab-arista-wan1 --port 6030 --username admin --password admin --insecure --encoding json_ietf subscribe --path /interfaces/interface[name=Management0]/state/

# In another terminal, you can generate traffic opening SSH connection
ssh admin@clab-arista-wan1
```

# Check configurations done:
```bash
gnmic --address clab-arista-wan1 --port 6030 --username admin --password admin --insecure --encoding json_ietf get --path '/network-instances' > wan1-nis.json
gnmic --address clab-arista-wan1 --port 6030 --username admin --password admin --insecure --encoding json_ietf get --path '/interfaces' > wan1-ifs.json
```

# Delete elements:
```bash
--address clab-arista-wan1 --port 6030 --username admin --password admin --insecure --encoding json_ietf set --delete '/network-instances/network-instance[name=b19229e8]'
--address clab-arista-wan1 --port 6030 --username admin --password admin --insecure --encoding json_ietf set --delete '/interfaces/interface[name=ethernet-1/1]/subinterfaces/subinterface[index=0]'
--address clab-arista-wan1 --port 6030 --username admin --password admin --insecure --encoding json_ietf set --delete '/interfaces/interface[name=ethernet-1/2]/subinterfaces/subinterface[index=0]'
```
