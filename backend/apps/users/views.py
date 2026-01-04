from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile


class VisionApiKeyView(APIView):
    """管理用户的 Vision API Key"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取 API Key 状态（不返回实际密钥）"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        return Response({
            'has_api_key': profile.has_vision_api_key,
            'masked_key': self._mask_key(profile.vision_api_key) if profile.has_vision_api_key else None
        })
    
    def post(self, request):
        """设置或更新 API Key"""
        api_key = request.data.get('api_key')
        if not api_key:
            return Response(
                {'detail': 'API Key 不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.vision_api_key = api_key
        profile.save()
        
        return Response({
            'detail': 'API Key 设置成功',
            'has_api_key': True,
            'masked_key': self._mask_key(api_key)
        })
    
    def delete(self, request):
        """删除 API Key"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.vision_api_key = None
        profile.save()
        
        return Response({
            'detail': 'API Key 已删除',
            'has_api_key': False
        })
    
    def _mask_key(self, key):
        """遮蔽 API Key，只显示前4位和后4位"""
        if not key or len(key) < 12:
            return '*' * 8
        return key[:4] + '*' * (len(key) - 8) + key[-4:]
