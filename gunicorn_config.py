# gunicorn_config.py
import multiprocessing

# Configuración de trabajadores
workers = multiprocessing.cpu_count() * 2 + 1
# Limitar el número máximo de trabajadores a 6 para evitar sobrecargar el sistema
workers = min(workers, 6)
worker_class = 'gthread'
threads = 2
worker_connections = 1000
max_requests = 500
max_requests_jitter = 50

# Configuración de tiempo de espera
timeout = 120
keepalive = 5

# Opciones de memoria
# Limitar el uso de memoria por trabajador
# Esta configuración es crucial para evitar el error "Worker was sent SIGKILL! Perhaps out of memory?"
# En bytes (128 MB)
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de registro
accesslog = '-'
errorlog = '-'
loglevel = 'warning'

# Configuración de reinicio graceful
graceful_timeout = 30
