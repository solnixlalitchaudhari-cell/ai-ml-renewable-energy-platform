
import sys
import os

def test_docker_env():
    print("Checking Docker Environment...")
    
    # Check 1: Python version
    print(f"Python Version: {sys.version}")
    
    # Check 2: Key Imports
    try:
        import tensorflow as tf
        print("✅ TensorFlow imported successfully")
    except ImportError as e:
        print(f"❌ TensorFlow import failed: {e}")

    try:
        import tf_keras
        print("✅ tf-keras imported successfully")
    except ImportError as e:
        print(f"❌ tf-keras import failed: {e}")

    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers imported successfully")
    except ImportError as e:
        print(f"❌ sentence-transformers import failed: {e}")

    # Check 3: File Structure (basic check if volume mount is working or copy worked)
    expected_path = "/app/phase_12_vector_rag/ingestion_pipeline.py"
    if os.path.exists(expected_path):
        print(f"✅ Application code found at {expected_path}")
    else:
        print(f"⚠️  Application code NOT found at {expected_path} (Are we inside Docker?)")

    print("\nEnvironment check complete.")

if __name__ == "__main__":
    test_docker_env()
