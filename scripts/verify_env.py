"""Full ML stack verification — tests all libraries needed for the CV pipeline."""

import sys
import time

print(f"Python: {sys.version}")
print("-" * 60)

# Core
import numpy as np
print(f"[OK] NumPy {np.__version__}")

import cv2
print(f"[OK] OpenCV {cv2.__version__}")

from PIL import Image
import PIL
print(f"[OK] Pillow {PIL.__version__}")

# ML/DL Runtime
import onnxruntime as ort
providers = ort.get_available_providers()
print(f"[OK] ONNX Runtime {ort.__version__}")
print(f"     Providers: {providers}")

# Face Detection
import mediapipe as mp
print(f"[OK] MediaPipe {mp.__version__}")

# Face Recognition
import insightface
print(f"[OK] InsightFace {insightface.__version__}")

# ML Utilities
import sklearn
print(f"[OK] scikit-learn {sklearn.__version__}")

import scipy
print(f"[OK] SciPy {scipy.__version__}")

import matplotlib
print(f"[OK] Matplotlib {matplotlib.__version__}")

# Web Framework
import fastapi
print(f"[OK] FastAPI {fastapi.__version__}")

import uvicorn
print(f"[OK] Uvicorn {uvicorn.__version__}")

import sqlalchemy
print(f"[OK] SQLAlchemy {sqlalchemy.__version__}")

import pydantic
print(f"[OK] Pydantic {pydantic.__version__}")

import jose
print(f"[OK] python-jose (JWT)")

import passlib
print(f"[OK] passlib (bcrypt)")

import redis
print(f"[OK] Redis {redis.__version__}")

print("-" * 60)
print(f"CUDA: {'CUDAExecutionProvider' in providers}")
print(f"TensorRT: {'TensorrtExecutionProvider' in providers}")
print("=" * 60)
print("ALL LIBRARIES VERIFIED SUCCESSFULLY!")
