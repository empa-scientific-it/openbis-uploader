FROM python:3.10
ENV OPENBIS_URL=openbis
ENV OPENBIS_PORT=8443
ENV OPENBIS_ADMIN_USER=admin
ENV OPENBIS_ADMIN_PASSWORD=changeit

COPY openbis-configuration/ /openbis-configuration/
COPY openbis-initialiser/ /openbis-initialiser/

WORKDIR /openbis-configuration/instance_creator
RUN pip install -e .
WORKDIR /openbis-initialiser
RUN chmod +x initialise.sh
CMD ["/bin/bash", "./initialise.sh"]
