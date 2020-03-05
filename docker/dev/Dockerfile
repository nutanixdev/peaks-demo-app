FROM node:7
RUN mkdir -p /usr/src/app/tests
RUN mkdir /output
COPY app/src /usr/src/app/
COPY app/tests/test.js /usr/src/app/tests
COPY app/tests/package.json /usr/src/app/tests
WORKDIR /usr/src/app
RUN npm update
RUN npm install
WORKDIR /usr/src/app/tests
RUN npm install
CMD ["npm", "test"]
