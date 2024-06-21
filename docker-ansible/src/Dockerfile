FROM ubuntu:jammy
ENV TERM=xterm-256color
RUN apt-get update -qy && \
    apt-get install -qy software-properties-common && \
    apt-get install -qy vim && \
    apt-get install -qy iputils-ping && \
    apt-get install -qy openssh-client && \
    apt-add-repository -y ppa:ansible/ansible && \
    apt-get update -qy && \
    apt-get install -qy ansible
VOLUME /ansible
WORKDIR /ansible
ENTRYPOINT ["ansible-playbook"]
CMD ["site.yml"]
