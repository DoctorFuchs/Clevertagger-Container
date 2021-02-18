# Clevertagger-Container

Docker script for "Clevertagger" and "SMORLemma". Both tools have been developed by
[Rico Sennrich](https://github.com/rsennrich). Dockerfile based on work by
[DoctorFuchs](https://github.com/DoctorFuchs).

## Build

```console
docker build -t clever .
```

## Run

```console
docker run --rm -it --init -d -p 8888:80 --name clever clever
```

## Stop

```console
docker stop clever
```

## API Docs

In your browser, navigate to [http://localhost:8888/docs](http://localhost:8888/docs) to access the OpenAPI GUI.

## Linguistic Todos

Clevertagger expects an array of tokenised sentences as input. Provide proper tokenisation.
