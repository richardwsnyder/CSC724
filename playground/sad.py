import multiprocessing

import kad_server
import http_server

kad_proc = multiprocessing.Process(target=kad_server.kad_server_worker_thread)
kad_proc.start()

http_proc = multiprocessing.Process(target=http_server.http_server_worker_thread)
http_proc.start()
