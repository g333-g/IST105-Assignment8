from django.shortcuts import render
from pymongo import MongoClient
from .forms import LeaseForm
import time

client = MongoClient("mongodb://172.31.27.209:27017/")
db = client["dhcpdb"]
leases = db["leases"]

def mac_to_eui64(mac):
    p = mac.split(':')
    e = p[:3] + ['ff','fe'] + p[3:]
    e[0] = f"{int(e[0],16)^2:02x}"
    return '{:02x}{:02x}:{:02x}{:02x}:{:02x}{:02x}:{:02x}{:02x}'.format(*[int(x,16) for x in e])

def get_next_ip(v, m):
    if v=="DHCPv4":
        u = [l['assigned_ip'] for l in leases.find({"dhcp_version":"DHCPv4"})]
        for i in range(10,255):
            ip=f"192.168.1.{i}"
            if ip not in u: return ip
    else:
        ip="2001:db8::"+mac_to_eui64(m)
        u = [l['assigned_ip'] for l in leases.find({"dhcp_version":"DHCPv6"})]
        if ip not in u: return ip
    return None

def index(request):
    if request.method=="POST":
        f=LeaseForm(request.POST)
        if f.is_valid():
            m=f.cleaned_data['mac_address']
            v=f.cleaned_data['dhcp_version']
            t=3600
            n=int(time.time())
            e=leases.find_one({"mac_address":m,"dhcp_version":v})
            if e and n-e.get("timestamp",0)<e.get("lease_time",t):
                leases.update_one({"_id":e["_id"]},{"$set":{"timestamp":n}})
                a=e["assigned_ip"]
            else:
                a=get_next_ip(v,m)
                leases.insert_one({"mac_address":m,"dhcp_version":v,"assigned_ip":a,"lease_time":t,"timestamp":n})
            return render(request,"result.html",{
                "mac_address": m,
                "assigned_ip": a,
                "lease_time": f"{t} seconds"
            })
    else:
        f=LeaseForm()
    return render(request,"form.html",{"form":f})

def leases_list(request):
    d=list(leases.find())
    return render(request,"leases_list.html",{"lease_data":d})

