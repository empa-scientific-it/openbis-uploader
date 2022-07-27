FROM openbis/debian-openbis:latest
WORKDIR /home/openbis/openbis/servers/datastore_server/etc/
RUN cp service.properties service.properties.bup
COPY auth.properties .
COPY change_properties.sh .
RUN chmod +x ./change_properties.sh
RUN  ./change_properties.sh