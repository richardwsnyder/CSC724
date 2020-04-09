import time
import sys
sys.path.insert(1, '../http_server/user_profile')
from views import get_user

start = time.time()
# call get_user here
end = time.time()
print(end - start)