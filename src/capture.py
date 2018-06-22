print("oi")
Exception
import requests
from dateutil.relativedelta import relativedelta
import datetime
import zipfile
from io import BytesIO
import os
import threading
import json

from utils import Timer


def generate_month_year(starting_from=datetime.date(2018, 4, 1)):
    result = []

    today = datetime.date.today()
    current = starting_from

    while current <= today:
        result.append({'month': current.month,
                       'year':  current.year})
        current += relativedelta(months=1)

    return result


def download_data(year, month, verbose=False):
    url = 'http://arquivos.portaldatransparencia.gov.br/downloads.asp?a={}&m={}&d=C&consulta=Servidores'.format(year,
                                                                                                                str(month).zfill(2))

    if verbose:
        print('Downloading {}-{}'.format(year, month))
        print(url)
    with Timer(verbose=verbose) as t:
        res = requests.get(url)

    return res


def extract_data(res, year, month, verbose=False):
    path = '../package/data/'
    folder_name = '{}-{}'.format(year, month)
    directory = os.path.join(path, folder_name)

    if verbose:
        print('Extracting {}-{}'.format(year, month))
    with Timer(verbose=verbose) as t:
        file = zipfile.ZipFile(BytesIO(res.content))
        if not os.path.exists(directory):
            os.makedirs(directory)
        file.extractall(directory)


def transform_data(date, sema=False, verbose=False):

    #sema.acquire()
    res = download_data(date['year'], date['month'], verbose=verbose)
    extract_data(res, date['year'], date['month'], verbose=verbose)
    #sema.release()


def create_datapackage(verbose=False):

    # Criar o datapackage.json

    if verbose:
        print("Criando datapackage.json")
    with Timer(verbose=verbose) as t:
        with open("metadata.json", "r") as mfd:
            output = json.load(mfd)

            with open("resources.json", "r") as rfd:
                output['resources'] = json.load(rfd)
            
            with open("../package/datapackage.json", "w") as datapackage:
                json.dump(output, datapackage, indent=2)
        
        
def manage_transform(maxthreads=10, verbose=False):

    # sema = threading.Semaphore(value=maxthreads)
    # threads = list()

    # for date in generate_month_year():
    #     thread = threading.Thread(target=transform_data, args=(date, sema, verbose))
    #     threads.append(thread)
    #     thread.start()

    create_datapackage(verbose=verbose)
import time
if __name__ == '__main__':
    manage_transform(1, verbose=True)
    transform_data(generate_month_year()[0], True)
    create_datapackage(verbose=True)
