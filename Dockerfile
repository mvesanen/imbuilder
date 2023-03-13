FROM python:3.8-slim-buster


COPY apt-packages.txt /apt-packages.txt
RUN apt-get update && apt-get install -y $(cat apt-packages.txt)

COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

RUN mkdir /docbuild
COPY docbuild/* /docbuild/

RUN mkdir /artefact

RUN mkdir /git

RUN git config --global --add safe.directory /git

ENTRYPOINT ["/docbuild/default-build.sh"]
CMD ["/docbuild/test.md"]
