FROM python:3.10

ENV BASE_PATH=
ENV LDAP_SERVER=
ENV LDAP_PORT= 
ENV LDAP_PRINCIPAL_NAME= 
ENV LDAP_PRINCIPAL_PASSWORD= 
ENV LDAP_BASE= 
ENV OPENBIS_SERVER= 
ENV JWS_SECRET_KEY= 

COPY ./data-discovery/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./data-discovery/ data-discovery

RUN cd data-discovery/app && pip install -e .

COPY ./openbis-configuration/instance_creator instance_creator
RUN cd instance_creator/ && pip install -e .

RUN cd ../data-discovery

CMD ["python3", "app/main.py", "--host", "0.0.0.0", "--port", "80"]
