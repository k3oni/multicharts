from datetime import datetime
from pytz import timezone

date_str = "2014-05-28 22:28:15"
datetime_obj_naive = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

# Wrong way!
datetime_obj_pacific = datetime_obj_naive.replace(tzinfo=timezone('US/Pacific'))
print datetime_obj_pacific.strftime("%Y-%m-%d %H:%M:%S %Z%z")

# Right way!
datetime_obj_pacific = timezone('US/Pacific').localize(datetime_obj_naive)
print datetime_obj_pacific.strftime("%Y-%m-%d %H:%M:%S %Z%z")
