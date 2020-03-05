FROM mongo
MAINTAINER DevOps Team
COPY ./db/mongo/data/collections.json /tmp/
CMD mongo mongodb/demodb < /tmp/collections.json
