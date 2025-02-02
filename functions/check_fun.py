from mainrobot.models import v2panel , inovices , users
from datetime import datetime , timedelta 
import jdatetime



def check_time_passed(inovice_id : int):
    inovices_ = inovices.objects.get(id = inovice_id)
    created_date = str(inovices_.created_date)
    created_datetime = jdatetime.datetime.strptime(created_date ,  "%Y/%m/%d-%H:%M:%S")
    created_date_timstamp = created_datetime.timestamp()
    current_time = jdatetime.datetime.now().timestamp()
    check_30_min_pass = current_time - created_date_timstamp

    if check_30_min_pass >= 1800:
         return 'time_passed'
    else :
         return 'have-time'





