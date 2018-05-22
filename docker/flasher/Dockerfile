FROM python:3.5

RUN pip3 install python-miio

VOLUME /dustcloud

ENTRYPOINT  ["python", "-u", "/dustcloud/devices/xiaomi.vacuum/firmwarebuilder/flasher.py"]
CMD ["--help"]
