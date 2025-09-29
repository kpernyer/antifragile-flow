# Dockerfile for React frontend

# Build environment
FROM node:18-alpine as build
WORKDIR /app
COPY . ./
RUN npm install -g pnpm
RUN pnpm install
RUN pnpm build

# Production environment
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
# Copy the default nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
