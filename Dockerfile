FROM ubuntu:latest
WORKDIR /clevertagger

#update packages
RUN apt-get -y update

#timezone
RUN apt-get -y install tzdata
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime

#==========================> main requirements
#install git, python, python2-pip, python3, python3-pip
RUN apt-get -y install git
RUN apt-get -y install python
RUN apt-get -y install curl
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get -y install unzip
#<========================== end main requirements

#==========================> SMORLemma 
#install requirements for smor
RUN apt-get -y install build-essential
RUN apt-get -y install xsltproc
RUN apt-get -y install sfst

#clone SMORLemma-lemmatiser branch
RUN git clone -b lemmatiser https://github.com/rsennrich/SMORLemma.git

#copy zmorge
#COPY zmorge.ca .
RUN curl https://pub.cl.uzh.ch/users/sennrich/zmorge/transducers/zmorge-20150315-smor_newlemma.ca.zip --output zmorge-20150315-smor_newlemma.ca.zip
RUN mkdir /data
RUN mkdir /zmorge
RUN unzip zmorge-20150315-smor_newlemma.ca.zip -d /data/zmorge/

#make main dict
RUN make ./SMORLemma
#<========================== end SMORLemma 

#==========================> Clevertagger
#install python requirements
RUN pip3 install wapiti3
RUN pip3 install pexpect 

#clone clevertagger
RUN git clone https://github.com/rsennrich/clevertagger.git

#RUN git clone http://git.savannah.gnu.org/r/m4.git
#COPY clevertagger ./clevertagger
#COPY bison-3.7 ./bison
#COPY ncurses-6.2 ./ncurses

COPY runner.sh .
COPY text.txt .

RUN cd /clevertagger

#CMD [ "ls", "/data/zmorge" ]
CMD [ "bash", "runner.sh" ]