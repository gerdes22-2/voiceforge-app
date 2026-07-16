with open(".env.example", "r") as f:
    content = f.read()

# Replace MinIO placeholder with R2 structure
content = content.replace(
"""# --- Storage (MinIO / S3) ---
STORAGE_PROVIDER=minio
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=voiceforge-storage
S3_REGION=us-east-1""",
"""# --- Storage (Cloudflare R2 / AWS S3) ---
STORAGE_PROVIDER=s3
S3_ENDPOINT_URL=https://<your-account-id>.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=<your-access-key-id>
S3_SECRET_ACCESS_KEY=<your-secret-access-key>
S3_BUCKET_NAME=voiceforge-bucket
S3_REGION_NAME=auto"""
)

with open(".env.example", "w") as f:
    f.write(content)
