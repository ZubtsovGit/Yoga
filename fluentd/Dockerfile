FROM fluent/fluentd:v1.16

USER root

# Установка плагинов
RUN apk add --no-cache --update sudo build-base ruby-dev \
    && sudo gem install fluent-plugin-elasticsearch \
    && sudo gem install faraday-excon \
    && sudo gem sources --clear-all \
    && apk del build-base ruby-dev \
    && rm -rf /tmp/* /var/tmp/* /usr/lib/ruby/gems/*/cache/*.gem

# Создание директорий для логов и установка прав доступа
RUN mkdir -p /fluentd/log \
    && chmod -R 777 /fluentd/log

USER fluent 
