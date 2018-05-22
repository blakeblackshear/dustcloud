# Docker containers for easy Xiaomi Vacuum Rooting

## Build an image

1. Build your docker container
```
cd image_builder
docker build . -t image_builder
```

2. Copy `v11_XXX.pkg`, `english.pkg`, and `id_rsa.pub` to `data`

3. Build your firmware
```
docker run --rm --privileged -v $PWD/../data:/data -v $PWD/../..:/dustcloud image_builder -f /data/v11_XXXX.pkg -s /data/english.pkg -k /data/id_rsa.pub -t "America/Chicago"
```

## Flash the image

1. Place the output files from the previous step on any http server. (`python -m SimpleHTTPServer` works fine)

2. Build the flasher docker container
```
cd flasher
docker build . -t flasher
```

3. Reset the wifi on your vacuum and connect to the network it broadcasts

4. Flash your vacuum (update with actual url and md5)
```
docker run --rm -v $PWD/../..:/dustcloud flasher -f http://path.to/your_custom_firmware.pkg -m md5_of_custom_firmware
```
