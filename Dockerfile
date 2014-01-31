FROM debian:latest

RUN apt-get update

RUN apt-get install -y proftpd
RUN echo "root:pass" | chpasswd
RUN sed -i 'N;N;s/\(DefaultRoot.*\n\n\)/\1RootLogin\t\t\ton\n\n/' /etc/proftpd/proftpd.conf
RUN sed -i 'N;s/root\n//' /etc/ftpusers

CMD /etc/init.d/proftpd start && bash
