from datetime import datetime
format = '%d.%m.%Y'
default=datetime.utcnow()
print(default)

x = datetime.strptime(default, format)
print(x)