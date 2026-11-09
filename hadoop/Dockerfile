FROM debian:bookworm-slim

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema, Java, Python3 y OpenSSH
RUN apt-get update -o Acquire::Retries=3 && apt-get install -y --no-install-recommends --fix-missing -o Acquire::Retries=3 \
    default-jdk-headless \
    python3 \
    python3-pip \
    openssh-server \
    openssh-client \
    curl \
    tar \
    procps \
    sudo \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Configurar variables de entorno de Java y Hadoop
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Enlazar binarios de Hadoop y Java a /usr/local/bin para sesiones SSH no interactivas
RUN ln -s /usr/lib/jvm/default-java/bin/* /usr/local/bin/ 2>/dev/null || true
RUN ln -s /opt/hadoop/bin/* /usr/local/bin/ 2>/dev/null || true

# Descargar e instalar Hadoop (modo standalone)
ENV HADOOP_VERSION=3.3.6
RUN (curl -fSL https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz -o /tmp/hadoop.tar.gz || \
     curl -fSL https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz -o /tmp/hadoop.tar.gz) \
    && tar -xzf /tmp/hadoop.tar.gz -C /opt/ \
    && mv /opt/hadoop-${HADOOP_VERSION} /opt/hadoop \
    && rm -rf /tmp/hadoop.tar.gz /opt/hadoop/share/doc

# Configurar JAVA_HOME en hadoop-env.sh
RUN echo "export JAVA_HOME=${JAVA_HOME}" >> /opt/hadoop/etc/hadoop/hadoop-env.sh

# Crear usuario 'usuario' y agregarlo a sudoers sin contraseña
RUN useradd -m -s /bin/bash usuario && \
    echo "usuario ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Crear directorios de trabajo y datos
RUN mkdir -p /data/input /data/output /mapreduce /shared-ssh /var/run/sshd && \
    chown -R usuario:usuario /data /mapreduce /shared-ssh /opt/hadoop

# Configurar SSH daemon
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Copiar script de entrada
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Establecer directorio de trabajo
WORKDIR /mapreduce

# Exponer puerto SSH
EXPOSE 22

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["tail", "-f", "/dev/null"]
