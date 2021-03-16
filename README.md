# QRmisp
Tool para cargar ioc's de MISP a referenceSets de Qradar.
## Descarga
git clone https://github.com/4rth4S/QRmisp.git
## Modo de Uso

python QRmisp.py funcion ioc_type referenceSet_name días_atrás

### Por ejemplo:

python QRmisp.py load_iocs URL _MISP_Event_IOC_URLS 20


Admite como parámetros de ioc_type : 
- URL 
- MD5 
- SHA256 
- DOMAIN 
- IP_SRC 
- IP_DST
