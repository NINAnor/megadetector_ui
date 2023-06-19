# MegaDetector UI

An User Interface (UI) deployed on our server to run MegaDetector for a set of images and return a database of the detections made by MegaDetector.

It is also possible to use the application locally using `Docker`:

```
docker build -t comvis -f Dockerfile .
docker run --rm- it -p 8999:8999 --gpus all comvis
```
