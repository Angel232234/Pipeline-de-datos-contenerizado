#!/bin/bash
set -e

# Configurar SSH cliente para conectarse a hadoop por nombre de servicio
mkdir -p /root/.ssh
if [ -f /shared-ssh/id_rsa ]; then
    cp /shared-ssh/id_rsa /root/.ssh/id_rsa
    chmod 600 /root/.ssh/id_rsa
fi

cat <<'EOF' > /root/.ssh/config
Host hadoop
    HostName hadoop
    User usuario
    IdentityFile /root/.ssh/id_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR

Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR
EOF
chmod 600 /root/.ssh/config

echo "[API] Cliente SSH configurado para usuario@hadoop."

# Ejecutar el comando principal (app.py)
exec "$@"
