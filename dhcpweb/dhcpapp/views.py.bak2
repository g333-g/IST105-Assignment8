from django.shortcuts import render
from pymongo import MongoClient
from .forms import LeaseForm

client = MongoClient("mongodb://172.31.27.209:27017/")
db = client["dhcpdb"]
leases = db["leases"]

def mac_to_eui64(mac):
    parts = mac.split(':')
    eui64 = parts[:3] + ['ff', 'fe'] + parts[3:]
    first_octet = int(eui64[0], 16) ^ 0x02
    eui64[0] = f"{first_octet:02x}"
    return '{:02x}{:02x}:{:02x}{:02x}:{:02x}{:02x}:{:02x}{:02x}'.format(*[int(x,16) for x in eui64])

def get_next_ip(dhcp_version, mac=''):
    if dhcp_version == "DHCPv4":
        base = "192.168.1."
        used = [l['assigned_ip'] for l in leases.find({"dhcp_version": "DHCPv4"})]
        for i in range(10, 255):
            ip = f"{base}{i}"
            if ip not in used:
                return ip
    else:
        base = "2001:db8::"
        if mac:
            eui = mac_to_eui64(mac)
            ip = base + eui
            used = [l['assigned_ip'] for l in leases.find({"dhcp_version": "DHCPv6"})]
            if ip not in used:
                return ip
        return None

def index(request):
    if request.method == "POST":
        form = LeaseForm(request.POST)
        if form.is_valid():
            mac = form.cleaned_data['mac_address']
            dhcp = form.cleaned_data['dhcp_version']
            assigned_ip = get_next_ip(dhcp, mac)
            lease_time = 3600
            leases.insert_one({
                "mac_address": mac,
                "dhcp_version": dhcp,
                "assigned_ip": assigned_ip,
                "lease_time": lease_time,
            })
            return render(request, "result.html", {"assigned_ip": assigned_ip})
    else:
        form = LeaseForm()
    return render(request, "form.html", {"form": form})

def leases_list(request):
    lease_data = list(leases.find())
    return render(request, "leases_list.html", {"lease_data": lease_data})

