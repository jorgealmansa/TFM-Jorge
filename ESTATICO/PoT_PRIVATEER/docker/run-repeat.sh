#!/bin/sh

    sleep 30
    p4c-bm2-ss --p4v 16 --p4runtime-files p4/pot.p4.p4info.txt -o p4/pot.json p4/pot.p4
    sudo python3 controller/runtimev2.py --p4info p4/pot.p4.p4info.txt --bmv2-json p4/pot.json --ssl