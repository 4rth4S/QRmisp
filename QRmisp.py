#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import pymisp
import json
requests.packages.urllib3.disable_warnings()
from keys import misp_fqdn, misp_token, qradar_fqdn, qradar_token
import fire
import logging
# ioc_type puede ser URL, MD5, SHA256, DOMAIN, IPDST ,IPSRC
# referece_set_name es el nombre del referenceSet de QRadar donde van a ir los IoCs 
# days , es la cant. de dias previos que se quiere retornar la data , por ej: "los IoCs de los ultimos 10 dias"
# Uso:
# python3 QRmisp.py load_iocs MD5 _MISP_Events_IOCS-MD5 10

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('QR_MISP')


def pull_misp (ioc_type, days):
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
  elif str(ioc_type).upper() == 'IPDST':
    data_pull = {"request": {"type": "ip-dst", "category": "Network activity", "last": str(days)+"d", "enforceWarnlinglist": "True"}}
  elif str(ioc_type).upper() == 'IPSRC':
    data_pull = {"request": {"type": "ip-src", "category": "Network activity", "last": str(days)+"d", "enforceWarnlinglist": "True"}}
  else:
    return 'Ese tal \"'+str(ioc_type)+'\" no es aceptado.  Los disponibles para elegir son: \n\nURL\tMD5\tSHA256\tDOMAIN\tIP_DST\tIP_SRC'
  try:
    r = requests.post(url_pull, headers=headers_pull, json=data_pull, verify=False)
    print(r.json)
    logger.info('se hizo bien la peticion hacia el MISP para '+str(ioc_type)+' .')
    if r.status_code != 200:
      logger.error('El codigo de error es  %s'%r.status_code)
  except:
    logger.error('Algo paso cuando quisimos traernos los IOC\'s desde misp') #Raise exception on HTTP errors
  return r

def limpiar_iocs(r,ioc_type):
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
    logger.info("IOCs del tipo URL extraídos del JSON en un formato aceptable...ahí lo mandamos al QRadar...")
    return clean_iocs
  else:
    for value in j3:
      iocs.append(value["value"])
    json.dumps(iocs)
    logger.info("IOCs extraídos del JSON en un formato aceptable...ahí lo mandamos al QRadar...")
    print(iocs)
    return iocs

def push_Qradar(indicadores, reference_set_name):
  url_push = "https://"+qradar_fqdn+"/api/reference_data/sets/bulk_load/"+reference_set_name
  headers_push = {'SEC': qradar_token , 'Content-Type': 'application/json', 'Version': '9.0', 'Accept': 'application/json'}
#  if ioc_type=='URL':
#    p = requests.post(url_push, headers=headers_push, json=indicadores, verify=False)
#  else:

  try:
   p = requests.post(url_push, headers=headers_push, json=indicadores, verify=False)
   print(p.status_code)
   if p.status_code != 200:
    logger.error('El codigo de error es  %s'%p.status_code)
  except:
    logger.error('Algo malo paso cuando quisimos pushear los IOC\'s a QRadar') #Raise exception on HTTP errors
  number_of_IOCs = str(len(indicadores))
  logger.info('un total de: ' + number_of_IOCs + ' IOCs pusheados a QRadar!')
  return number_of_IOCs

def load_iocs(ioc_type, reference_set_name,days):
  r= pull_misp(ioc_type, days)
  indicadores = limpiar_iocs(r, ioc_type)
  number_of_IOCs=push_Qradar(indicadores, reference_set_name)
  logger.info('un total de: ' + number_of_IOCs + ' IOCs pusheados a QRadar!')
  return number_of_IOCs

if __name__ == '__main__':
  fire.Fire()