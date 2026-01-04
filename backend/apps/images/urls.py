from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, MyImagesViewSet, AdminImageViewSet

router = DefaultRouter()
router.register(r'images', ImageViewSet, basename='image')
router.register(r'my-images', MyImagesViewSet, basename='my-image')
router.register(r'admin/images', AdminImageViewSet, basename='admin-image')

urlpatterns = [
    path('', include(router.urls)),
]
