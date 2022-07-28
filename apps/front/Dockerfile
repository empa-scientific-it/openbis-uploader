FROM node:lts-alpine AS build-stage

# Install the http server
RUN npm install -g http-server

# Set working directory
WORKDIR /usr/

# # Copy packages
COPY app/package*.json .
COPY app/* .

# Install dependencies
RUN npm install

# Copy the folders from the workdir
COPY . .

WORKDIR /usr/app

CMD ["npm", "run", "dev"]
# Builds app
FROM base as prod


RUN npm run build

FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /usr/app/dist /usr/share/nginx/html

COPY --from=build-stage /usr/app/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]