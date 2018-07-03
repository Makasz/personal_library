from datetime import datetime, timedelta
print(datetime.now())
print(datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f"))