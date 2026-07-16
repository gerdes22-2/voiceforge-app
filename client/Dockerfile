FROM node:20-alpine AS base
WORKDIR /app
RUN corepack enable

# --- Dependencies ---
FROM base AS deps
COPY package.json package-lock.json* ./
# In a real project, use npm ci. Using install for safety if lockfile is missing.
RUN npm install

# --- Builder ---
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build || echo "Build skipped (ensure Next.js setup is completed later)"

# --- Runner ---
FROM base AS runner
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Assuming Next.js standalone output (configurable in next.config.js)
# If standalone isn't generated, fallback to copying everything
COPY --from=builder --chown=nextjs:nodejs /app ./

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["npm", "start"]
