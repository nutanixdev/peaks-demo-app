FROM node:7
ARG VERSION=1.0.0
ENV NODE_ENV production
COPY app/src /usr/src/app/
WORKDIR /usr/src/app
RUN npm update
RUN npm install
CMD ["node", "app.js"]
EXPOSE 3000
