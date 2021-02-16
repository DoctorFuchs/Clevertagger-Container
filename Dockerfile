FROM ubuntu:latest
WORKDIR /clevertagger

RUN apt-get -y update

RUN apt-get -y install tzdata
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime

#==========================> main requirements
RUN apt-get -y install git
RUN apt-get -y install curl
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get -y install unzip
RUN apt-get -y install make 
#<========================== end main requirements


#==========================> SMORLemma 
RUN apt-get -y install build-essential
RUN apt-get -y install xsltproc
RUN apt-get -y install sfst

RUN git clone -b lemmatiser https://github.com/rsennrich/SMORLemma.git

RUN curl https://pub.cl.uzh.ch/users/sennrich/zmorge/transducers/zmorge-20150315-smor_newlemma.ca.zip --output zmorge-20150315-smor_newlemma.ca.zip
RUN mkdir /data
RUN mkdir /zmorge
RUN unzip zmorge-20150315-smor_newlemma.ca.zip -d /data/zmorge/

RUN curl https://pub.cl.uzh.ch/users/sennrich/zmorge/models/hdt_ab.zmorge-20140521-smor_newlemma.model.zip --output zmorge.model.zip
RUN unzip zmorge.model.zip -d /data/zmorge/

RUN make ./SMORLemma
#<========================== end SMORLemma 


#==========================> Clevertagger
RUN curl https://www.cis.uni-muenchen.de/~schmid/tools/SFST/data/SFST-1.4.7f.zip --output SFST.zip
RUN unzip SFST.zip -d /clevertagger/

RUN git clone https://github.com/rsennrich/clevertagger.git

RUN rm /clevertagger/clevertagger/config.py
COPY config.py /clevertagger/clevertagger/

RUN curl https://wapiti.limsi.fr/model-pos.de.gz --output wapitiModel.gz

RUN git clone https://github.com/Jekub/Wapiti.git
RUN mv ./Wapiti ./wapiti

WORKDIR /clevertagger/wapiti
RUN make 
RUN make install

WORKDIR /clevertagger
RUN pip3 install pexpect
#<========================== end Clevertagger

#==========================> (fast)-API
RUN pip3 install uvicorn
RUN pip3 install fastapi
#RUN pip3 install flask
#RUN pip3 install requests
#RUN pip3 install flask-restplus

COPY main.py ./clevertagger
#<========================== end (fast)-API

WORKDIR /clevertagger/clevertagger

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

EXPOSE 80