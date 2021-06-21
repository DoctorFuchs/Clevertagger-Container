FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

ARG ZMORGE_NEWLEMMA_FILE=zmorge-20150315-smor_newlemma.ca.zip
ARG ZMORGE_NEWLEMMA_SHA256=8135bbee51a91f11d8177e772d25812336980eb3e5e031ff5927a1760fc1d211

ARG ZMORGE_MODEL_FILE=hdt_ab.zmorge-20140521-smor_newlemma.model.zip
ARG ZMORGE_MODEL_SHA256=db4ac7ba3f4ab1f38db08e239e3c5f3ec6ed21c6161e02797744416bd7acd6db

ARG SFST_FILE=SFST-1.4.7f.zip
ARG SFST_SHA256=31f331a1cc94eb610bcefc42b18a7cf62c55f894ac01a027ddff29e2a71cc31b

ARG CLEVERTAGGER_COMMIT=b45832ef1f89dcc5ad8fde9a1b19cdd847720ecc
ARG CLEVERTAGGER_TGZ_SHA=d4c651c8b7f3ea8e9fb6ac23dc225956d7faed62d1861d86df13f50adc15c9e3

ARG WAPITI_COMMIT=v1.5.0
ARG WAPITI_TGZ_SHA=671dee4c2b9bd790a6414f576bd94926add651490e5dad8eb4929d1b737be193

WORKDIR /clevertagger

COPY requirements.txt .

RUN apt-get -y update \
    && apt-get -y install tzdata \
    && ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone \
    && apt-get install -y \
        # main requirements \
        git \
        curl \
        python3 \
        python3-pip \
        unzip \
        make \
        # SMORLemma \
        build-essential \
        xsltproc \
        sfst \
    # fastapi dependencies \
    && pip3 install -r requirements.txt \
    # \
    # ZMORGE \
    && mkdir --parent /data/zmorge \
    && curl \
        --location "https://pub.cl.uzh.ch/users/sennrich/zmorge/transducers/${ZMORGE_NEWLEMMA_FILE}" \
        --output ${ZMORGE_NEWLEMMA_FILE} \
    && echo "${ZMORGE_NEWLEMMA_SHA256}  ${ZMORGE_NEWLEMMA_FILE}" | sha256sum -c \
    && unzip "${ZMORGE_NEWLEMMA_FILE}" -d /data/zmorge/ \
    && unlink "${ZMORGE_NEWLEMMA_FILE}" \
    && curl \
        --location "https://pub.cl.uzh.ch/users/sennrich/zmorge/models/${ZMORGE_MODEL_FILE}" \
        --output "${ZMORGE_MODEL_FILE}" \
    && echo "${ZMORGE_MODEL_SHA256}  ${ZMORGE_MODEL_FILE}" | sha256sum -c \
    && unzip "${ZMORGE_MODEL_FILE}" -d /data/zmorge/ \
    && unlink "${ZMORGE_MODEL_FILE}" \
    # \
    # Clevertagger \
    && curl \
        --location "https://www.cis.uni-muenchen.de/~schmid/tools/SFST/data/${SFST_FILE}" \
        --output "${SFST_FILE}" \
    && echo "${SFST_SHA256}  ${SFST_FILE}" | sha256sum -c \
    && unzip "${SFST_FILE}" -d /clevertagger/ \
    && unlink "${SFST_FILE}" \
    && curl \
        --location "https://github.com/rsennrich/clevertagger/archive/${CLEVERTAGGER_COMMIT}.tar.gz" \
        --output clevertagger.tar.gz \
    && echo "${CLEVERTAGGER_TGZ_SHA}  clevertagger.tar.gz" | sha256sum -c \
    && mkdir clevertagger \
    && tar --strip-components=1 -C clevertagger -xzf clevertagger.tar.gz \
    && unlink clevertagger.tar.gz \
    && unlink clevertagger/config.py \
    && curl \
        --location "https://github.com/Jekub/Wapiti/archive/${WAPITI_COMMIT}.tar.gz" \
        --output wapiti.tar.gz \
    && echo "${WAPITI_TGZ_SHA}  wapiti.tar.gz" | sha256sum -c \
    && mkdir wapiti \
    && tar --strip-components=1 -C wapiti -xzf wapiti.tar.gz \
    && unlink wapiti.tar.gz \
    && cd wapiti \
    && make \
    && make install \
    && cd .. \
    # \
    # remove build dependencies \
    && apt-get purge -y git unzip make build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /clevertagger/clevertagger

COPY config.py .
COPY main.py .

HEALTHCHECK CMD curl --silent --fail -X GET 'http://localhost:80/docs' || exit 1

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
