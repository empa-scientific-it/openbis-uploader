

FROM alpine:latest
#Parameters
ENV SOURCE "/incoming"
ENV DEST "/datastore"
ENV LOG "transfer.log"
#Install rsync
RUN apk add --no-cache rsync
RUN apk add --no-cache inotify-tools
RUN apk add openrc --no-cache
#Move scripts
COPY prepare.sh .
COPY entrypoint.sh .
COPY transfer.sh .
#Run the script to prepare folders
RUN sh ./prepare.sh

RUN chmod +x ./entrypoint.sh && chmod +x ./transfer.sh

CMD ["sh", "-c", "./entrypoint.sh"]