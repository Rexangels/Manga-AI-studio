# manga/api.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class MangaProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MangaProject.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new manga project"""
        try:
            # Extract parameters
            narrative = request.data.get('narrative')
            panel_count = int(request.data.get('panel_count', 4))
            model_id = request.data.get('model_id')
            template_id = request.data.get('template_id')
            
            # Validate
            if not narrative:
                return Response(
                    {'error': 'Narrative is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate manga
            service = MangaGenerationService(request.user)
            project = service.generate_manga(
                narrative=narrative,
                panel_count=panel_count,
                model_id=model_id,
                template_id=template_id
            )
            
            # Return project data
            serializer = MangaProjectSerializer(project)
            return Response(serializer.data)
            
        except QuotaExceeded as e:
            return Response(
                {'error': str(e), 'type': 'quota_exceeded'},
                status=status.HTTP_402_PAYMENT_REQUIRED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Export project as PDF or image"""
        project = self.get_object()
        export_format = request.data.get('format', 'pdf')
        
        try:
            export_service = ExportService()
            result = export_service.export_project(
                project=project,
                format=export_format
            )
            
            return Response({
                'download_url': result['url'],
                'expires_at': result['expires_at']
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )