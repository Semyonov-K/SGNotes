from datetime import datetime
format = '%d.%m.%Y'
deadline_str = "2023-07-21T03:21"
x = datetime.fromisoformat(deadline_str)
print(x)