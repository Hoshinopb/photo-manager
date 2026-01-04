from django.db import models
from django.conf import settings
import os
import uuid


def image_upload_path(instance, filename):
    """生成图片上传路径：uploads/user_{id}/{uuid}.{ext}"""
    ext = filename.split('.')[-1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads', f'user_{instance.owner.id}', new_filename)


def thumbnail_upload_path(instance, filename):
    """生成缩略图上传路径：thumbnails/user_{id}/{uuid}_thumb.jpg"""
    ext = 'jpg'  # 缩略图统一使用 jpg 格式
    name_without_ext = os.path.splitext(filename)[0]
    return os.path.join('thumbnails', f'user_{instance.owner.id}', f"{name_without_ext}.{ext}")


class Image(models.Model):
    """图片模型"""
    
    # 允许的图片格式
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='上传者'
    )
    file = models.ImageField(
        upload_to=image_upload_path,
        verbose_name='图片文件'
    )
    thumbnail = models.ImageField(
        upload_to=thumbnail_upload_path,
        blank=True,
        default='',
        verbose_name='缩略图'
    )
    thumbnail_generated = models.BooleanField(
        default=False,
        verbose_name='缩略图已生成'
    )
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '等待处理'),
            ('processing', '处理中'),
            ('completed', '已完成'),
            ('failed', '处理失败'),
        ],
        default='pending',
        verbose_name='处理状态'
    )
    filename = models.CharField(
        max_length=255,
        verbose_name='原始文件名'
    )
    size = models.PositiveIntegerField(
        verbose_name='文件大小(字节)'
    )
    width = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='宽度'
    )
    height = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='高度'
    )
    upload_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='上传时间'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='是否公开'
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='描述'
    )
    
    # 标签关联 (多对多)
    tags = models.ManyToManyField(
        'tags.Tag',
        through='ImageTag',
        related_name='images',
        blank=True,
        verbose_name='标签'
    )
    
    # EXIF 信息字段
    exif_camera_make = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='相机品牌'
    )
    exif_camera_model = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='相机型号'
    )
    exif_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='拍摄时间'
    )
    exif_exposure_time = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='曝光时间'
    )
    exif_f_number = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='光圈值'
    )
    exif_iso = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='ISO感光度'
    )
    exif_focal_length = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='焦距'
    )
    exif_gps_latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='GPS纬度'
    )
    exif_gps_longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='GPS经度'
    )
    exif_parsed = models.BooleanField(
        default=False,
        verbose_name='EXIF已解析'
    )
    
    class Meta:
        db_table = 'images'
        ordering = ['-upload_time']
        verbose_name = '图片'
        verbose_name_plural = '图片'
    
    def __str__(self):
        return f"{self.filename} - {self.owner.username}"
    
    @property
    def storage_path(self):
        """返回存储路径"""
        return self.file.name if self.file else None
    
    @property
    def file_url(self):
        """返回文件URL"""
        return self.file.url if self.file else None
    
    @property
    def resolution(self):
        """返回分辨率字符串"""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return None


class ImageTag(models.Model):
    """图片-标签关联表"""
    
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        verbose_name='图片'
    )
    tag = models.ForeignKey(
        'tags.Tag',
        on_delete=models.CASCADE,
        verbose_name='标签'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='添加时间'
    )
    
    class Meta:
        db_table = 'image_tags'
        unique_together = ['image', 'tag']
        verbose_name = '图片标签'
        verbose_name_plural = '图片标签'
    
    def __str__(self):
        return f"{self.image.filename} - {self.tag.name}"
