from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Project
from .serializers import ProjectSerializer

import subprocess
import os
from django.http import JsonResponse
from django.conf import settings

@api_view(['GET'])
def get_projects(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

MODEL_OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, "models")

def generate_3d_model(request):
    width = request.GET.get("width", 5)
    length = request.GET.get("length", 5)
    height = request.GET.get("height", 3)
    location_size = request.GET.get("location_size", 50)  
    budget = request.GET.get("budget", 5000) 

    script_path = os.path.abspath("blender_scripts/generate_model.py")
    output_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, "models/room_model.glb"))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    command = [
        "blender", "--background", "--python", script_path,
        "--", str(width), str(length), str(height), str(location_size), str(budget), output_path
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",  
            errors="replace",  
        )

        print("Blender Output:", result.stdout)
        print("Blender Errors:", result.stderr)
        print("Expected Output Path:", output_path)

        if os.path.exists(output_path):
            model_url = request.build_absolute_uri(settings.MEDIA_URL + "models/room_model.glb")
            return JsonResponse({"model_url": model_url})
        else:
            return JsonResponse({"error": f"Model not found at: {output_path}"}, status=500)

    except subprocess.SubprocessError as e:
        print("Subprocess Error:", str(e))
        return JsonResponse({"error": f"Blender execution failed: {str(e)}"}, status=500)
