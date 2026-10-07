from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProjectCreateSerializer


class ProjectCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProjectCreateSerializer,
        responses={201: ProjectCreateSerializer},
    )
    def post(self, request):
        serializer = ProjectCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            project = serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid project data.",
                    "details": serializer.errors,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )