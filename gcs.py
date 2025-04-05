import os
from google.cloud import storage
from app.config import GCP_BUCKET_NAME, GOOGLE_APPLICATION_CREDENTIALS

# ✅ Validate bucket name
if not GCP_BUCKET_NAME:
    raise EnvironmentError("GCP_BUCKET_NAME is not set in the environment.")

# ✅ Set local credentials path (important for local dev only)
if GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
else:
    raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS is missing or invalid.")

def upload_file_to_gcs(file_path: str, destination_folder="recordings") -> str:
    file_path = os.path.abspath(file_path)

    print("🔍 Checking local file exists:", os.path.exists(file_path))
    print("📍 File path:", file_path)
    print("🪣 Bucket name:", GCP_BUCKET_NAME)

    try:
        client = storage.Client()  # ✅ Uses service account for local
        bucket = client.bucket(GCP_BUCKET_NAME)

        blob_name = f"{destination_folder}/{os.path.basename(file_path)}"
        blob = bucket.blob(blob_name)

        print("⏫ Uploading file to GCS...")
        blob.upload_from_filename(file_path)

        # ⚠️ Don't make public if using Uniform access
        print(f"✅ File uploaded to GCS: {blob_name}")
        return f"gs://{GCP_BUCKET_NAME}/{blob_name}"

    except Exception as e:
        print(f"[GCS ERROR] Upload failed: {e}")
        raise
