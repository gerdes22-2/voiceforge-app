with open("backend/app/core/config.py", "r") as f:
    content = f.read()

s3_vars = """    
    # Storage
    STORAGE_PROVIDER: str = "local"
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET_NAME: str | None = None
    S3_REGION_NAME: str = "auto"
"""

if "STORAGE_PROVIDER" not in content:
    content = content.replace("model_config =", s3_vars + "\n    model_config =")
    with open("backend/app/core/config.py", "w") as f:
        f.write(content)
