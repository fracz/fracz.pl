FROM yourls:1.9.2-apache

ADD https://github.com/fredl99/YOURLS-Upload-and-Shorten/archive/master.tar.gz /opt/Uplad-and-Shorten.tar.gz

# https://github.com/guessi/docker-yourls/blob/master/dockerfiles/Dockerfile
RUN for i in $(ls /opt/*.tar.gz); do                                          \
      plugin_name="$(basename ${i} '.tar.gz')"                              ; \
      mkdir -p user/plugins/${plugin_name}                                  ; \
      tar zxvf /opt/${plugin_name}.tar.gz                                     \
        --strip-components=1                                                  \
        -C user/plugins/${plugin_name}                                      ; \
    done

RUN echo "define('SHARE_URL','http://fracz.com/uploads/');" >> /usr/src/yourls/user/config-docker.php \
  && echo "define('SHARE_DIR','/var/www/html/uploads/');" >> /usr/src/yourls/user/config-docker.php

COPY static/ /var/www/html
