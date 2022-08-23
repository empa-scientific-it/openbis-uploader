FROM openbis/debian-openbis:latest
RUN apt update && apt install python3-pip -y
RUN pip install javaproperties 
WORKDIR /home/openbis/openbis/servers/openBIS-server/jetty/etc/
RUN cp service.properties service.properties.bup
COPY update_properties.py .
COPY auth.properties .
#RUN  python3 ./update_properties.py ./service.properties.bup ./auth.properties ./service.properties
#RUN echo service.properties | grep ldap
