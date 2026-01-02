from django.db import models


class Tag(models.Model):
    """标签模型"""
    
    # 标签类型
    TYPE_CHOICES = [
        ('auto', '自动生成'),      # EXIF解析自动生成
        ('user', '用户自定义'),    # 用户手动添加
        ('ai', 'AI识别'),          # AI模型识别生成
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='标签名称'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='user',
        verbose_name='标签类型'
    )
    color = models.CharField(
        max_length=20,
        default='',
        blank=True,
        verbose_name='标签颜色'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        db_table = 'tags'
        ordering = ['name']
        verbose_name = '标签'
        verbose_name_plural = '标签'
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_or_create_tag(cls, name, tag_type='user'):
        """获取或创建标签"""
        tag, created = cls.objects.get_or_create(
            name=name.strip().lower(),
            defaults={'type': tag_type}
        )
        return tag
