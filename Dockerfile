# Use Node.js LTS image
FROM node:18-slim

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY package*.json ./
RUN npm install --production

# Bundle app source
COPY . .

# Expose the port Express is running on
EXPOSE 3000

# Start the server
CMD [ "node", "server.js" ]
