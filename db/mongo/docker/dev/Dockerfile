FROM mongo:5.0.11
MAINTAINER DevOps Team
COPY ./db/mongo/data/collections.json /tmp/
CMD mongo mongodb/demodb < /tmp/collections.json
