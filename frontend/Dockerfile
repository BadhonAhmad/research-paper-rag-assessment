# Frontend Dockerfile - Optimized
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with optimizations
RUN npm ci --prefer-offline --no-audit

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run in development mode with host binding
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]
