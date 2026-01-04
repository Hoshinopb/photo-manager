from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib


def get_encryption_key():
    """从 SECRET_KEY 生成加密密钥"""
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)


class UserProfile(models.Model):
    """用户扩展信息，包括头像设置和API密钥"""
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ForeignKey(
        'images.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='avatar_users'
    )
    # 加密存储的 API Key
    _vision_api_key = models.TextField(
        blank=True,
        default='',
        db_column='vision_api_key',
        verbose_name='Vision API Key (加密)'
    )
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f'{self.user.username} 的资料'
    
    @property
    def avatar_url(self):
        if self.avatar:
            # Image模型使用 thumbnail 字段而不是 thumbnail_url
            if self.avatar.thumbnail:
                return self.avatar.thumbnail.url
            return self.avatar.file.url
        return None
    
    @property
    def vision_api_key(self):
        """解密并返回 API Key"""
        if not self._vision_api_key:
            return None
        try:
            f = Fernet(get_encryption_key())
            return f.decrypt(self._vision_api_key.encode()).decode()
        except Exception:
            return None
    
    @vision_api_key.setter
    def vision_api_key(self, value):
        """加密并存储 API Key"""
        if not value:
            self._vision_api_key = ''
        else:
            f = Fernet(get_encryption_key())
            self._vision_api_key = f.encrypt(value.encode()).decode()
    
    @property
    def has_vision_api_key(self):
        """检查是否设置了 API Key"""
        return bool(self._vision_api_key)


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    """创建用户时自动创建对应的 Profile"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())
def save_user_profile(sender, instance, **kwargs):
    """保存用户时同时保存 Profile"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
