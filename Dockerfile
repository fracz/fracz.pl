FROM yourls:1.10.2-apache

ADD https://github.com/fredl99/YOURLS-Upload-and-Shorten/archive/master.tar.gz /opt/Uplad-and-Shorten.tar.gz

# https://github.com/guessi/docker-yourls/blob/master/dockerfiles/Dockerfile
RUN for i in $(ls /opt/*.tar.gz); do                                          \
      plugin_name="$(basename ${i} '.tar.gz')"                              ; \
      mkdir -p user/plugins/${plugin_name}                                  ; \
      tar zxvf /opt/${plugin_name}.tar.gz                                     \
        --strip-components=1                                                  \
        -C user/plugins/${plugin_name}                                      ; \
    done

RUN echo "define('SHARE_URL','https://fracz.com/uploads/');" >> /usr/src/yourls/user/config-docker.php \
  && echo "define('SHARE_DIR','/var/www/html/uploads/');" >> /usr/src/yourls/user/config-docker.php

COPY static/ /var/www/html

COPY apache/uploads.ini /usr/local/etc/php/conf.d/uploads.ini
COPY apache/temp.fracz.com.conf /etc/apache2/sites-available/temp.fracz.com.conf

RUN { \
		echo 'opcache.memory_consumption=128'; \
		echo 'opcache.interned_strings_buffer=8'; \
		echo 'opcache.max_accelerated_files=4000'; \
		echo 'opcache.revalidate_freq=2'; \
		echo 'opcache.fast_shutdown=1'; \
		echo 'opcache.enable_cli=1'; \
	} > /usr/local/etc/php/conf.d/opcache-recommended.ini \
    && a2enmod rewrite expires proxy proxy_http headers deflate ssl cgi alias env \
    && a2ensite temp.fracz.com.conf
