import boto3
import json
import uuid
import os
import logging
import requests
import time

# DEFINE
IP_FILE_LOCATION = 'currentIp.txt'
IP_RETRIVAL_INTERVAL = 2  # seconds

# intiate logging
logging.basicConfig(
    filename='audel.log', filemode='a',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


# get public IP function
def get_public_ip():
    try:
        return requests.get('https://checkip.amazonaws.com').text.strip()
    except:
        return False


def get_public_ip_with_retry():
    while True:
        ipres = get_public_ip()
        if not ipres == False:
            return ipres
        else:
            time.sleep(IP_RETRIVAL_INTERVAL)


try:  # try to read existing IP file
    with open(IP_FILE_LOCATION, "r") as f:
        OLD_IP = f.read()
        NEW_IP = get_public_ip_with_retry()
        if OLD_IP == NEW_IP:
            logging.info("No IP change Detected!")
            os._exit(0)
        else:
            TARGET_IP = NEW_IP
except:
    logging.warning('IP file does not exists.. Creating new file')
    with open(IP_FILE_LOCATION, "w") as f:
        NEW_IP = get_public_ip_with_retry()
        f.write(NEW_IP)
        TARGET_IP = NEW_IP


with open('config.json') as f:
    config = json.load(f)

lightsail = boto3.client('lightsail')

# check & get the domain
response = lightsail.get_domain(
    domainName=config.get('domain')
)

full_domain_name = config.get('subdomain') + '.' + config.get('domain')

domainEnteriesArray = []
# check the occurancy number of times subdomain occured in list
for entry in response.get('domain').get('domainEntries'):
    if(entry.get('name') == full_domain_name):
        if(entry.get('type') == config.get('type')):
            domainEnteriesArray.append(entry.get('id'))

arr_len = len(domainEnteriesArray)

# function to create new domain entry


def create_entry():
    response = lightsail.create_domain_entry(
        domainName=config.get('domain'),
        domainEntry={
            'id': str(uuid.uuid4()),
            'name': full_domain_name,
            'target': TARGET_IP,
            'isAlias': False,
            'type': config.get('type')
        }
    )
    return response


def update_entry(id):
    response = lightsail.update_domain_entry(
        domainName=config.get('domain'),
        domainEntry={
            'id': id,
            'name': full_domain_name,
            'target': TARGET_IP,
            'isAlias': False,
            'type': config.get('type')
        }
    )
    return(response)


# sys.exit()

if arr_len == 0:
    logging.info('No domain entry Found. Creating new one...')
    print(create_entry())

elif arr_len == 1:
    # update
    logging.info('Updating domain entry...')
    logging.info(update_entry(domainEnteriesArray[0]))
else:
    logging.error(
        'Found multiple domain entries... Deleting all old entries...')
    # delete all then create
    for entry in response.get('domain').get('domainEntries'):
        if(entry.get('name') == full_domain_name):
            if(entry.get('type') == config.get('type')):
                response = lightsail.delete_domain_entry(
                    domainName=config.get('domain'),
                    domainEntry={
                        'id': entry.get('id'),
                        'name': full_domain_name,
                        'target': entry.get('target'),
                        'isAlias': False,
                        'type': entry.get('type')
                    }
                )
                logging.info(response)
    # create_domain entry
    logging.info('Creating new Domain Entry...')
    logging.info(create_entry())
