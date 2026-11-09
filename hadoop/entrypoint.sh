#!/bin/bash
set -e

# Crear directorios de SSH
mkdir -p /home/usuario/.ssh /root/.ssh /shared-ssh
chmod 700 /home/usuario/.ssh /root/.ssh

# Generar llaves SSH en el volumen compartido si no existen
if [ ! -f /shared-ssh/id_rsa ]; then
    echo "[HADOOP] Generando nuevas llaves SSH sin contraseña..."
    ssh-keygen -t rsa -b 2048 -N "" -f /shared-ssh/id_rsa -C "datamart-pipeline-key"
    chmod 600 /shared-ssh/id_rsa
    chmod 644 /shared-ssh/id_rsa.pub
fi

# Instalar llaves para el usuario 'usuario'
cp /shared-ssh/id_rsa /home/usuario/.ssh/id_rsa
cp /shared-ssh/id_rsa.pub /home/usuario/.ssh/id_rsa.pub
cat /shared-ssh/id_rsa.pub > /home/usuario/.ssh/authorized_keys
chmod 600 /home/usuario/.ssh/id_rsa /home/usuario/.ssh/authorized_keys
chmod 644 /home/usuario/.ssh/id_rsa.pub
chown -R usuario:usuario /home/usuario/.ssh

# Instalar llaves para el usuario 'root'
cp /shared-ssh/id_rsa /root/.ssh/id_rsa
cp /shared-ssh/id_rsa.pub /root/.ssh/id_rsa.pub
cat /shared-ssh/id_rsa.pub > /root/.ssh/authorized_keys
chmod 600 /root/.ssh/id_rsa /root/.ssh/authorized_keys
chmod 644 /root/.ssh/id_rsa.pub

# Configurar SSH client para no pedir confirmacion de fingerprint
cat <<'EOF' > /home/usuario/.ssh/config
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    LogLevel ERROR
EOF
chmod 600 /home/usuario/.ssh/config
chown usuario:usuario /home/usuario/.ssh/config

cp /home/usuario/.ssh/config /root/.ssh/config
chmod 600 /root/.ssh/config

# Iniciar servicio SSH Daemon
service ssh start
echo "[HADOOP] Servidor OpenSSH iniciado y escuchando."

# Asegurar wrapper de hadoop en /usr/local/bin
cat <<'EOF' > /usr/local/bin/hadoop
#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/default-java
export HADOOP_HOME=/opt/hadoop
exec /opt/hadoop/bin/hadoop "$@"
EOF
chmod +x /usr/local/bin/hadoop

# Ejecutar el comando principal
exec "$@"
