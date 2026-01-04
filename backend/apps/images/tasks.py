"""
图片处理异步任务

包含：
- 缩略图生成
- EXIF 解析
- AI 标注（预留）
"""
import os
import logging
from celery import shared_task
from django.conf import settings
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_image_async(self, image_id):
    """
    异步处理图片的主任务
    
    包含：
    1. 生成缩略图
    2. 解析 EXIF
    3. 生成自动标签
    """
    from apps.images.models import Image
    
    try:
        image = Image.objects.get(id=image_id)
        logger.info(f"开始异步处理图片: {image.filename} (ID: {image_id})")
        
        # 更新状态为处理中
        image.processing_status = 'processing'
        image.save(update_fields=['processing_status'])
        
        # 1. 生成缩略图
        generate_thumbnail(image)
        
        # 2. 解析 EXIF 并生成自动标签
        parse_exif_and_generate_tags(image)
        
        # 更新状态为完成
        image.processing_status = 'completed'
        image.save(update_fields=['processing_status'])
        
        logger.info(f"图片处理完成: {image.filename} (ID: {image_id})")
        return {'status': 'success', 'image_id': image_id}
        
    except Image.DoesNotExist:
        logger.error(f"图片不存在: ID={image_id}")
        return {'status': 'error', 'message': '图片不存在'}
    except Exception as exc:
        logger.error(f"处理图片失败: {exc}")
        # 更新状态为失败
        try:
            image = Image.objects.get(id=image_id)
            image.processing_status = 'failed'
            image.save(update_fields=['processing_status'])
        except:
            pass
        # 重试
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_thumbnail_task(self, image_id):
    """异步生成缩略图任务"""
    from apps.images.models import Image
    
    try:
        image = Image.objects.get(id=image_id)
        generate_thumbnail(image)
        return {'status': 'success', 'image_id': image_id}
    except Image.DoesNotExist:
        logger.error(f"图片不存在: ID={image_id}")
        return {'status': 'error', 'message': '图片不存在'}
    except Exception as exc:
        logger.error(f"生成缩略图失败: {exc}")
        raise self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=3)
def parse_exif_task(self, image_id):
    """异步解析 EXIF 任务"""
    from apps.images.models import Image
    
    try:
        image = Image.objects.get(id=image_id)
        parse_exif_and_generate_tags(image)
        return {'status': 'success', 'image_id': image_id}
    except Image.DoesNotExist:
        logger.error(f"图片不存在: ID={image_id}")
        return {'status': 'error', 'message': '图片不存在'}
    except Exception as exc:
        logger.error(f"解析 EXIF 失败: {exc}")
        raise self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=3)
def ai_analyze_image_task(self, image_id):
    """
    AI 分析图片任务（预留）
    
    TODO: 接入 AI 模型进行图片内容识别
    """
    from apps.images.models import Image
    
    try:
        image = Image.objects.get(id=image_id)
        logger.info(f"AI 分析任务（预留）: {image.filename}")
        
        # TODO: 调用 AI API 分析图片
        # 1. 读取图片文件
        # 2. 调用远程 AI 模型 API
        # 3. 解析返回的标签
        # 4. 写入数据库
        
        return {'status': 'success', 'image_id': image_id, 'message': 'AI功能待实现'}
    except Image.DoesNotExist:
        logger.error(f"图片不存在: ID={image_id}")
        return {'status': 'error', 'message': '图片不存在'}
    except Exception as exc:
        logger.error(f"AI 分析失败: {exc}")
        raise self.retry(exc=exc, countdown=60)


def generate_thumbnail(image):
    """
    生成缩略图
    
    Args:
        image: Image 模型实例
    """
    if not image.file:
        logger.warning(f"图片文件不存在: ID={image.id}")
        return
    
    try:
        # 获取缩略图尺寸配置
        thumb_size = getattr(settings, 'THUMBNAIL_SIZE', (300, 300))
        thumb_quality = getattr(settings, 'THUMBNAIL_QUALITY', 85)
        
        # 打开原图
        image.file.seek(0)
        img = PILImage.open(image.file)
        
        # 保持 EXIF 方向信息
        try:
            from PIL import ExifTags
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif:
                orientation_value = exif.get(orientation)
                if orientation_value == 3:
                    img = img.rotate(180, expand=True)
                elif orientation_value == 6:
                    img = img.rotate(270, expand=True)
                elif orientation_value == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass
        
        # 转换为 RGB（处理 RGBA 或其他模式）
        if img.mode in ('RGBA', 'P', 'LA'):
            # 创建白色背景
            background = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 生成缩略图（保持比例）
        img.thumbnail(thumb_size, PILImage.Resampling.LANCZOS)
        
        # 保存到内存
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG', quality=thumb_quality, optimize=True)
        thumb_io.seek(0)
        
        # 生成缩略图文件名
        original_name = os.path.basename(image.file.name)
        name_without_ext = os.path.splitext(original_name)[0]
        thumb_filename = f"{name_without_ext}_thumb.jpg"
        
        # 保存缩略图
        image.thumbnail.save(thumb_filename, ContentFile(thumb_io.read()), save=False)
        image.thumbnail_generated = True
        image.save(update_fields=['thumbnail', 'thumbnail_generated'])
        
        logger.info(f"缩略图生成成功: {image.filename}")
        
    except Exception as e:
        logger.error(f"生成缩略图失败 (ID={image.id}): {e}")
        raise


def parse_exif_and_generate_tags(image):
    """
    解析 EXIF 并生成自动标签
    
    Args:
        image: Image 模型实例
    """
    from apps.images.exif_utils import apply_exif_to_image
    
    try:
        apply_exif_to_image(image)
        logger.info(f"EXIF 解析完成: {image.filename}")
    except Exception as e:
        logger.error(f"EXIF 解析失败 (ID={image.id}): {e}")
        raise


@shared_task
def cleanup_orphaned_files():
    """
    清理孤立文件（定期任务）
    
    清理没有数据库记录对应的图片文件
    """
    from apps.images.models import Image
    
    media_root = settings.MEDIA_ROOT
    uploads_dir = os.path.join(media_root, 'uploads')
    
    if not os.path.exists(uploads_dir):
        return {'status': 'success', 'cleaned': 0}
    
    cleaned_count = 0
    
    # 获取所有数据库中的文件路径
    db_files = set(Image.objects.values_list('file', flat=True))
    db_thumbnails = set(Image.objects.exclude(thumbnail='').values_list('thumbnail', flat=True))
    all_db_files = db_files | db_thumbnails
    
    # 遍历上传目录
    for root, dirs, files in os.walk(uploads_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, media_root)
            
            if relative_path not in all_db_files:
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                    logger.info(f"清理孤立文件: {relative_path}")
                except OSError as e:
                    logger.error(f"清理文件失败: {relative_path}, 错误: {e}")
    
    logger.info(f"清理完成，共清理 {cleaned_count} 个文件")
    return {'status': 'success', 'cleaned': cleaned_count}
