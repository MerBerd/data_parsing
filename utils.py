import logging
from datetime import datetime, timedelta

def get_logger():
    logger = logging.getLogger(__name__)

    logging.basicConfig(filename="myapp.log", level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def cleanInfo(info):
    info = info.strip().split('\n')
    n = len(info)
    if n == 6:
        return [info[0]] + [info[2]] + info[-2:]
    else:
        return [info[0]] + [info[1]] + info[-2:]
    
def stringToInt(price: str):
    price = price.replace('.', '')

    return int(price)/1000
    
def dateToTimestamp(dt: str):
    dt = dt.lower()
    result = datetime.now()
    if dt == 'şu wagt':
        return result.timestamp()
    elif 'sag öň' in dt:
        hours = int(dt.split()[0])
        result = result - timedelta(hours=hours)
        # subtract the given amount of hours from now and return the timestamp
    elif 'gün öň' in dt:
        days = int(dt.split()[0])
        result = result - timedelta(days=days)
        # subtract the given amount of days from now and return the timestamp
    elif 'düýn' in dt:
        result = result - timedelta(days=1)
        # subtract a day from now and return the timestamp
    else:
        dt = dt.strip().split('.')
        result = datetime(int(dt[2]), int(dt[1]), int(dt[0]), 0, 0, 0)
        # means there is a exact date given, try to convert it to a datetime object then return the timestamp
        
    return result.timestamp()