FROM python:3.5

RUN apt-get update
RUN apt-get install ccrypt git wget -y

VOLUME /dustcloud
VOLUME /data

WORKDIR /data

ENTRYPOINT  ["/dustcloud/devices/xiaomi.vacuum/firmwarebuilder/imagebuilder.sh"]
CMD ["--help"]
