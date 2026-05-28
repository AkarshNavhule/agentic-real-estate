# STAGE 1: Build the React application using Node
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# STAGE 2: Serve the app using Nginx
FROM nginx:alpine
# Copy the built files from Stage 1 into the Nginx server directory
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]