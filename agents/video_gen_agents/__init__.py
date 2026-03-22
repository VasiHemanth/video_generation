"""Foundational backend package for the video generation system."""

from .config import Settings
from .models import GenerateVideoRequest, GenerateVideoResponse, ProjectIR
from .pipeline import VideoGenerationService
from .rendering import render_project_ir

__all__ = [
    "GenerateVideoRequest",
    "GenerateVideoResponse",
    "ProjectIR",
    "render_project_ir",
    "Settings",
    "VideoGenerationService",
]
