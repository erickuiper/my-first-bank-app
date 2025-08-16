# Use Node.js 20 Alpine as base image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install Expo CLI globally
RUN npm install -g @expo/cli

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies needed for build)
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build the Expo app
RUN npx expo export --platform web

# Install serve to host the built app
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start the server to serve the built web app
CMD ["serve", "-s", "dist", "-l", "3000"]
