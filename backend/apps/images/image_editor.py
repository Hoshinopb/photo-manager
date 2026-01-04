"""
图片编辑工具模块

提供图片裁剪、旋转、翻转、色调调整等功能
"""
import os
import uuid
from io import BytesIO
from PIL import Image as PILImage, ImageEnhance, ImageFilter
from django.core.files.base import ContentFile
from django.conf import settings


class ImageEditor:
    """图片编辑器"""
    
    def __init__(self, image_instance):
        """
        初始化编辑器
        
        Args:
            image_instance: Image 模型实例
        """
        self.image_instance = image_instance
        self.image_instance.file.seek(0)
        self.pil_image = PILImage.open(self.image_instance.file)
        
        # 保持原始模式，用于后续保存
        self.original_mode = self.pil_image.mode
        self.original_format = self.pil_image.format or 'JPEG'
        
        # 转换为 RGB 进行处理（保持 alpha 通道如有）
        if self.pil_image.mode == 'RGBA':
            self._has_alpha = True
        else:
            self._has_alpha = False
            if self.pil_image.mode not in ('RGB', 'L'):
                self.pil_image = self.pil_image.convert('RGB')
    
    def crop(self, x, y, width, height):
        """
        裁剪图片
        
        Args:
            x: 左上角 x 坐标
            y: 左上角 y 坐标
            width: 裁剪宽度
            height: 裁剪高度
        """
        if width <= 0 or height <= 0:
            raise ValueError("裁剪尺寸必须大于0")
        
        img_width, img_height = self.pil_image.size
        
        # 确保裁剪区域在图片范围内
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))
        right = min(x + width, img_width)
        bottom = min(y + height, img_height)
        
        self.pil_image = self.pil_image.crop((x, y, right, bottom))
        return self
    
    def rotate(self, angle):
        """
        旋转图片
        
        Args:
            angle: 旋转角度（正数逆时针，支持 90, 180, 270, -90, -180, -270）
        """
        # 标准化角度
        angle = angle % 360
        if angle == 0:
            return self
        
        # PIL 的 rotate 是逆时针的，我们这里使用 transpose 来做精确的 90 度旋转
        if angle == 90:
            self.pil_image = self.pil_image.transpose(PILImage.Transpose.ROTATE_90)
        elif angle == 180:
            self.pil_image = self.pil_image.transpose(PILImage.Transpose.ROTATE_180)
        elif angle == 270:
            self.pil_image = self.pil_image.transpose(PILImage.Transpose.ROTATE_270)
        else:
            # 任意角度旋转，expand=True 保持完整图像
            self.pil_image = self.pil_image.rotate(angle, expand=True, resample=PILImage.Resampling.BICUBIC)
        
        return self
    
    def flip(self, direction='horizontal'):
        """
        翻转图片
        
        Args:
            direction: 'horizontal' 水平翻转，'vertical' 垂直翻转
        """
        if direction == 'horizontal':
            self.pil_image = self.pil_image.transpose(PILImage.Transpose.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            self.pil_image = self.pil_image.transpose(PILImage.Transpose.FLIP_TOP_BOTTOM)
        else:
            raise ValueError("翻转方向必须是 'horizontal' 或 'vertical'")
        
        return self
    
    def adjust_brightness(self, value):
        """
        调整亮度
        
        Args:
            value: -100 到 100，0 表示不变
        """
        if value == 0:
            return self
        
        # 将 -100~100 映射到 0~2 (0.5 表示减半，1 表示不变，2 表示加倍)
        factor = 1 + (value / 100)
        factor = max(0, min(factor, 2))
        
        enhancer = ImageEnhance.Brightness(self.pil_image)
        self.pil_image = enhancer.enhance(factor)
        
        return self
    
    def adjust_contrast(self, value):
        """
        调整对比度
        
        Args:
            value: -100 到 100，0 表示不变
        """
        if value == 0:
            return self
        
        factor = 1 + (value / 100)
        factor = max(0, min(factor, 2))
        
        enhancer = ImageEnhance.Contrast(self.pil_image)
        self.pil_image = enhancer.enhance(factor)
        
        return self
    
    def adjust_saturation(self, value):
        """
        调整饱和度
        
        Args:
            value: -100 到 100，0 表示不变，-100 为灰度
        """
        if value == 0:
            return self
        
        factor = 1 + (value / 100)
        factor = max(0, min(factor, 2))
        
        enhancer = ImageEnhance.Color(self.pil_image)
        self.pil_image = enhancer.enhance(factor)
        
        return self
    
    def adjust_sharpness(self, value):
        """
        调整锐度
        
        Args:
            value: -100 到 100，0 表示不变
        """
        if value == 0:
            return self
        
        factor = 1 + (value / 100)
        factor = max(0, min(factor, 2))
        
        enhancer = ImageEnhance.Sharpness(self.pil_image)
        self.pil_image = enhancer.enhance(factor)
        
        return self
    
    def apply_filter(self, filter_name):
        """
        应用滤镜
        
        Args:
            filter_name: 滤镜名称
                - blur: 模糊
                - sharpen: 锐化
                - edge_enhance: 边缘增强
                - emboss: 浮雕
                - smooth: 平滑
        """
        filters = {
            'blur': ImageFilter.BLUR,
            'sharpen': ImageFilter.SHARPEN,
            'edge_enhance': ImageFilter.EDGE_ENHANCE,
            'emboss': ImageFilter.EMBOSS,
            'smooth': ImageFilter.SMOOTH,
            'contour': ImageFilter.CONTOUR,
            'detail': ImageFilter.DETAIL,
        }
        
        if filter_name not in filters:
            raise ValueError(f"不支持的滤镜: {filter_name}")
        
        self.pil_image = self.pil_image.filter(filters[filter_name])
        return self
    
    def resize(self, width=None, height=None, keep_aspect=True):
        """
        调整图片尺寸
        
        Args:
            width: 目标宽度
            height: 目标高度
            keep_aspect: 是否保持宽高比
        """
        if width is None and height is None:
            return self
        
        orig_width, orig_height = self.pil_image.size
        
        if keep_aspect:
            if width and height:
                # 计算等比例缩放
                ratio = min(width / orig_width, height / orig_height)
                width = int(orig_width * ratio)
                height = int(orig_height * ratio)
            elif width:
                ratio = width / orig_width
                height = int(orig_height * ratio)
            else:
                ratio = height / orig_height
                width = int(orig_width * ratio)
        
        self.pil_image = self.pil_image.resize(
            (width, height),
            PILImage.Resampling.LANCZOS
        )
        return self
    
    def save(self):
        """保存编辑后的图片（覆盖原文件）"""
        # 确定保存格式
        filename = self.image_instance.filename.lower()
        if filename.endswith('.png'):
            format = 'PNG'
            content_type = 'image/png'
        elif filename.endswith('.gif'):
            format = 'GIF'
            content_type = 'image/gif'
        elif filename.endswith('.webp'):
            format = 'WEBP'
            content_type = 'image/webp'
        else:
            format = 'JPEG'
            content_type = 'image/jpeg'
        
        # 转换颜色模式
        save_image = self.pil_image
        if format == 'JPEG' and save_image.mode in ('RGBA', 'P', 'LA'):
            # JPEG 不支持透明通道，转换为 RGB
            background = PILImage.new('RGB', save_image.size, (255, 255, 255))
            if save_image.mode == 'P':
                save_image = save_image.convert('RGBA')
            if save_image.mode in ('RGBA', 'LA'):
                background.paste(save_image, mask=save_image.split()[-1])
            save_image = background
        
        # 保存到内存
        buffer = BytesIO()
        save_options = {'quality': 95, 'optimize': True} if format == 'JPEG' else {}
        save_image.save(buffer, format=format, **save_options)
        buffer.seek(0)
        
        # 删除旧文件
        old_path = self.image_instance.file.path
        if os.path.exists(old_path):
            os.remove(old_path)
        
        # 保存新文件
        self.image_instance.file.save(
            self.image_instance.filename,
            ContentFile(buffer.read()),
            save=False
        )
        
        # 更新图片尺寸
        self.image_instance.width = self.pil_image.size[0]
        self.image_instance.height = self.pil_image.size[1]
        self.image_instance.size = self.image_instance.file.size
        
        # 重新生成缩略图
        self.image_instance.thumbnail_generated = False
        self.image_instance.save()
        
        # 异步生成新缩略图
        try:
            from .tasks import generate_thumbnail_task
            generate_thumbnail_task.delay(self.image_instance.id)
        except Exception:
            # 如果 Celery 不可用，同步生成
            from .tasks import generate_thumbnail
            try:
                generate_thumbnail(self.image_instance)
            except Exception:
                pass
        
        return self.image_instance
    
    def save_as_new(self, owner):
        """
        保存为新图片
        
        Args:
            owner: 图片所有者
        
        Returns:
            新创建的 Image 实例
        """
        from .models import Image
        
        # 生成新文件名
        original_name = self.image_instance.filename
        name, ext = os.path.splitext(original_name)
        new_filename = f"{name}_edited_{uuid.uuid4().hex[:8]}{ext}"
        
        # 确定保存格式
        if ext.lower() in ['.png']:
            format = 'PNG'
        elif ext.lower() in ['.gif']:
            format = 'GIF'
        elif ext.lower() in ['.webp']:
            format = 'WEBP'
        else:
            format = 'JPEG'
        
        # 转换颜色模式
        save_image = self.pil_image
        if format == 'JPEG' and save_image.mode in ('RGBA', 'P', 'LA'):
            background = PILImage.new('RGB', save_image.size, (255, 255, 255))
            if save_image.mode == 'P':
                save_image = save_image.convert('RGBA')
            if save_image.mode in ('RGBA', 'LA'):
                background.paste(save_image, mask=save_image.split()[-1])
            save_image = background
        
        # 保存到内存
        buffer = BytesIO()
        save_options = {'quality': 95, 'optimize': True} if format == 'JPEG' else {}
        save_image.save(buffer, format=format, **save_options)
        buffer.seek(0)
        
        # 创建新的 Image 实例
        new_image = Image.objects.create(
            owner=owner,
            filename=new_filename,
            size=buffer.getbuffer().nbytes,
            width=self.pil_image.size[0],
            height=self.pil_image.size[1],
            is_public=False,  # 新图片默认为私有
            description=f"编辑自: {original_name}",
            processing_status='pending'
        )
        
        # 保存文件
        new_image.file.save(new_filename, ContentFile(buffer.read()), save=True)
        
        # 异步处理
        try:
            from .tasks import process_image_async
            process_image_async.delay(new_image.id)
        except Exception:
            pass
        
        return new_image
    
    def get_preview(self, max_size=800):
        """
        获取预览图（不保存）
        
        Args:
            max_size: 预览图最大尺寸
        
        Returns:
            base64 编码的图片数据
        """
        import base64
        
        # 创建预览图
        preview = self.pil_image.copy()
        
        # 限制尺寸
        width, height = preview.size
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            new_size = (int(width * ratio), int(height * ratio))
            preview = preview.resize(new_size, PILImage.Resampling.LANCZOS)
        
        # 转换为 base64
        buffer = BytesIO()
        
        # 转换颜色模式
        if preview.mode in ('RGBA', 'P', 'LA'):
            background = PILImage.new('RGB', preview.size, (255, 255, 255))
            if preview.mode == 'P':
                preview = preview.convert('RGBA')
            if preview.mode in ('RGBA', 'LA'):
                background.paste(preview, mask=preview.split()[-1])
            preview = background
        
        preview.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode('utf-8')
