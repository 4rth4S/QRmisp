#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import pymisp
import json
requests.packages.urllib3.disable_warnings()
from keys import misp_fqdn, misp_token, qradar_fqdn, qradar_token
import fire

# ioc_type puede ser URL, MD5, SHA256, DOMAIN, IP_DST ,IP_SRC
# referece_set_name es el nombre del referenceSet de QRadar donde van a ir los IoCs 
# days , es la cant. de dias previos que se quiere retornar la data , por ej: "los IoCs de los ultimos 10 dias"
# Uso:
# python3 QRmisp.py load_iocs MD5 _MISP_Events_IOCS-MD5 10

def load_iocs (ioc_type, reference_set_name,days):
  url_pull = "https://"+misp_fqdn+"/attributes/restSearch/json"
  headers_pull = {'Authorization': misp_token , 'Content-Type': 'application/json', 'Accept': 'application/json'}
  if str(ioc_type).upper() == 'URL':
    data_pull = {"request": {"type": "url", "category": "Network activity", "last": str(days)+"d", "enforceWarnlinglist": "True"}}
  elif str(ioc_type).upper() == 'MD5':
    data_pull = {"request": {"type": "md5", "category": "Payload delivery", "last": str(days)+"d", "enforceWarnlinglist": "True"}}
  elif str(ioc_type).upper() == 'SHA256':
    data_pull = {"request": {"type": "sha256", "category": "Payload delivery", "last": str(days)+"d", "enforceWarnlinglist": "True"}}
  elif str(ioc_type).upper() == 'DOMAIN':
    data_pull = {"request": {"type": "domain", "category": "Network activity", "last": str(days)+"d", "enforceWarnlinglist": "True"}}
  elif str(ioc_type).upper() == 'IP_DST':
    data_pull = {"request": {"type": "ip-dst", "category": "Network activity", "last": str(days)+"d", "enforceWarnlinglist": "True"}}
  elif str(ioc_type).upper() == 'IP_SRC':
    data_pull = {"request": {"type": "ip-src", "category": "Network activity", "last": str(days)+"d", "enforceWarnlinglist": "True"}}
  else:
    return 'Ese tal \"'+str(ioc_type)+'\" no existe, no flashees.. los disponibles son: \n\nURL\tMD5\tSHA256\tDOMAIN\tIP_DST\tIP_SRC'
  r = requests.post(url_pull, headers=headers_pull, json=data_pull, verify=False)
  r.raise_for_status() #Raise exception on HTTP errors
  
  print("Ya me traje los datos del MISP.. ahora me falta extraer los IOCs desde el JSON... bancame un cachito..")

  j1 = r.json()
  j2 = j1['response']
  j3 = j2['Attribute']
 
  iocs = []

  if ioc_type=='URL':
    clean_iocs = []
    SCHEMES = ('http://', 'https://', 'ftp://', 'git://')

    for value in j3:
        iocs.append(value["value"])

    for ioc in iocs:
        if ioc.startswith(SCHEMES):
            clean_iocs.append(ioc)
        else:
            continue
    json.dumps(clean_iocs)
    number_of_IOCs = str(len(clean_iocs))
    print("IOCs extraídos del JSON en un formato piola...ahí lo mandamos al QRadar...")
  else:
    for value in j3:
      iocs.append(value["value"])
    json.dumps(iocs)
    number_of_IOCs = str(len(iocs))
    print("IOCs extraídos del JSON en un formato piola...ahí lo mandamos al QRadar...")
  url_push = "https://"+qradar_fqdn+"/api/reference_data/sets/bulk_load/"+reference_set_name
  headers_push = {'SEC': qradar_token , 'Content-Type': 'application/json', 'Version': '9.0', 'Accept': 'application/json'}
  if ioc_type=='URL':
    p = requests.post(url_push, headers=headers_push, json=clean_iocs, verify=False)
  else:
    p = requests.post(url_push, headers=headers_push, json=iocs, verify=False)
  p.raise_for_status() #Raise exception on HTTP errors
  print('un total de: ' + number_of_IOCs + ' IOCs pusheados a QRadar!') 

if __name__ == '__main__':
  fire.Fire()
