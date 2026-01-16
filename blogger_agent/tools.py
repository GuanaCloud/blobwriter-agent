# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import glob
import os


def save_blog_post_to_file(blog_post: str, filename: str) -> dict:
    """Saves the blog post to a file."""
    with open(filename, "w") as f:
        f.write(blog_post)
    return {"status": "success"}


def analyze_codebase(directory: str) -> dict:
    """Analyzes the codebase in the given directory."""
    files = glob.glob(os.path.join(directory, "**"), recursive=True)
    codebase_context = ""
    for file in files:
        if os.path.isfile(file):
            codebase_context += f"""- **{file}**:"""
            try:
                with open(file, "r", encoding="utf-8") as f:
                    codebase_context += f.read()
            except UnicodeDecodeError:
                with open(file, "r", encoding="latin-1") as f:
                    codebase_context += f.read()
    return {"codebase_context": codebase_context}


def publish_to_linkedin(content: str) -> dict:
    """Publishes a post to LinkedIn."""
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    user_urn = os.environ.get("LINKEDIN_USER_URN")

    if not access_token or not user_urn:
        return {
            "status": "error",
            "message": "Missing LINKEDIN_ACCESS_TOKEN or LINKEDIN_USER_URN environment variables.",
        }

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    
    # Simple text post structure
    payload = {
        "author": f"urn:li:person:{user_urn}" if "urn:li:organization" not in user_urn else user_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    try:
        import requests
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except Exception as e:
         return {"status": "error", "message": str(e)}


def publish_to_web_blob(content: str, filename: str) -> dict:
    """Publishes content to a Google Cloud Storage bucket (Web Blob)."""
    bucket_name = os.environ.get("BLOG_BUCKET_NAME")
    
    if not bucket_name:
        return {"status": "error", "message": "Missing BLOG_BUCKET_NAME environment variable."}

    try:
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_string(content, content_type="text/html")
        
        # Make public if needed, or just return the authenticated link
        # blob.make_public() 
        
        return {"status": "success", "url": blob.public_url}
    except Exception as e:
        return {"status": "error", "message": str(e)}
