"""
EXIF 解析工具模块

用于从图片中提取 EXIF 元数据信息
"""
import exifread
from datetime import datetime
from PIL import Image as PILImage
from PIL.ExifTags import TAGS, GPSTAGS
import io


def parse_exif(file):
    """
    解析图片的 EXIF 信息
    
    Args:
        file: 文件对象或文件路径
        
    Returns:
        dict: 包含解析出的 EXIF 信息
    """
    exif_data = {
        'camera_make': '',
        'camera_model': '',
        'datetime': None,
        'exposure_time': '',
        'f_number': '',
        'iso': None,
        'focal_length': '',
        'gps_latitude': None,
        'gps_longitude': None,
        'width': None,
        'height': None,
    }
    
    try:
        # 确保文件指针在开头
        if hasattr(file, 'seek'):
            file.seek(0)
        
        # 使用 exifread 库读取 EXIF
        tags = exifread.process_file(file, details=False)
        
        # 重置文件指针
        if hasattr(file, 'seek'):
            file.seek(0)
        
        # 相机品牌
        if 'Image Make' in tags:
            exif_data['camera_make'] = str(tags['Image Make']).strip()
        
        # 相机型号
        if 'Image Model' in tags:
            exif_data['camera_model'] = str(tags['Image Model']).strip()
        
        # 拍摄时间
        datetime_str = None
        for key in ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime']:
            if key in tags:
                datetime_str = str(tags[key])
                break
        
        if datetime_str:
            try:
                exif_data['datetime'] = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
            except ValueError:
                pass
        
        # 曝光时间
        if 'EXIF ExposureTime' in tags:
            exif_data['exposure_time'] = str(tags['EXIF ExposureTime'])
        
        # 光圈值
        if 'EXIF FNumber' in tags:
            f_number = tags['EXIF FNumber']
            try:
                # 尝试转换为 f/x.x 格式
                if hasattr(f_number, 'values') and len(f_number.values) > 0:
                    ratio = f_number.values[0]
                    if hasattr(ratio, 'num') and hasattr(ratio, 'den'):
                        value = ratio.num / ratio.den
                        exif_data['f_number'] = f"f/{value:.1f}"
                    else:
                        exif_data['f_number'] = f"f/{float(ratio):.1f}"
                else:
                    exif_data['f_number'] = str(f_number)
            except:
                exif_data['f_number'] = str(f_number)
        
        # ISO
        if 'EXIF ISOSpeedRatings' in tags:
            try:
                iso_value = tags['EXIF ISOSpeedRatings']
                if hasattr(iso_value, 'values') and len(iso_value.values) > 0:
                    exif_data['iso'] = int(iso_value.values[0])
                else:
                    exif_data['iso'] = int(str(iso_value))
            except:
                pass
        
        # 焦距
        if 'EXIF FocalLength' in tags:
            focal = tags['EXIF FocalLength']
            try:
                if hasattr(focal, 'values') and len(focal.values) > 0:
                    ratio = focal.values[0]
                    if hasattr(ratio, 'num') and hasattr(ratio, 'den'):
                        value = ratio.num / ratio.den
                        exif_data['focal_length'] = f"{value:.1f}mm"
                    else:
                        exif_data['focal_length'] = f"{float(ratio):.1f}mm"
                else:
                    exif_data['focal_length'] = str(focal)
            except:
                exif_data['focal_length'] = str(focal)
        
        # GPS 信息
        gps_lat = _get_gps_coordinate(tags, 'GPS GPSLatitude', 'GPS GPSLatitudeRef')
        gps_lon = _get_gps_coordinate(tags, 'GPS GPSLongitude', 'GPS GPSLongitudeRef')
        
        if gps_lat is not None:
            exif_data['gps_latitude'] = gps_lat
        if gps_lon is not None:
            exif_data['gps_longitude'] = gps_lon
        
        # 使用 PIL 获取图片尺寸（更可靠）
        if hasattr(file, 'seek'):
            file.seek(0)
        try:
            img = PILImage.open(file)
            exif_data['width'], exif_data['height'] = img.size
        except:
            pass
        
    except Exception as e:
        print(f"EXIF 解析错误: {e}")
    
    return exif_data


def _get_gps_coordinate(tags, coord_key, ref_key):
    """
    从 EXIF 标签中提取 GPS 坐标
    
    Args:
        tags: EXIF 标签字典
        coord_key: 坐标键名
        ref_key: 方向参考键名
        
    Returns:
        float or None: GPS 坐标值
    """
    if coord_key not in tags:
        return None
    
    try:
        coord = tags[coord_key]
        ref = str(tags.get(ref_key, 'N'))
        
        if hasattr(coord, 'values') and len(coord.values) >= 3:
            degrees = coord.values[0]
            minutes = coord.values[1]
            seconds = coord.values[2]
            
            # 转换为浮点数
            if hasattr(degrees, 'num'):
                d = degrees.num / degrees.den
            else:
                d = float(degrees)
            
            if hasattr(minutes, 'num'):
                m = minutes.num / minutes.den
            else:
                m = float(minutes)
            
            if hasattr(seconds, 'num'):
                s = seconds.num / seconds.den
            else:
                s = float(seconds)
            
            # 计算十进制度数
            decimal = d + (m / 60.0) + (s / 3600.0)
            
            # 根据参考方向调整正负
            if ref in ['S', 'W']:
                decimal = -decimal
            
            return decimal
    except Exception as e:
        print(f"GPS 坐标解析错误: {e}")
    
    return None


def generate_auto_tags(exif_data, image):
    """
    根据 EXIF 信息自动生成标签
    
    Args:
        exif_data: EXIF 数据字典
        image: Image 模型实例
        
    Returns:
        list: 生成的标签名称列表
    """
    from apps.tags.models import Tag
    
    tags = []
    
    # 相机品牌标签
    if exif_data.get('camera_make'):
        make = exif_data['camera_make'].lower()
        # 简化品牌名称
        brand_mapping = {
            'canon': 'Canon',
            'nikon': 'Nikon',
            'sony': 'Sony',
            'fujifilm': 'Fujifilm',
            'panasonic': 'Panasonic',
            'olympus': 'Olympus',
            'apple': 'iPhone',
            'samsung': 'Samsung',
            'huawei': 'Huawei',
            'xiaomi': 'Xiaomi',
            'oppo': 'OPPO',
            'vivo': 'vivo',
        }
        for key, value in brand_mapping.items():
            if key in make:
                tags.append(value)
                break
    
    # 拍摄时间标签（年份、季节）
    if exif_data.get('datetime'):
        dt = exif_data['datetime']
        tags.append(f"{dt.year}年")
        
        # 季节
        month = dt.month
        if month in [3, 4, 5]:
            tags.append('春季')
        elif month in [6, 7, 8]:
            tags.append('夏季')
        elif month in [9, 10, 11]:
            tags.append('秋季')
        else:
            tags.append('冬季')
    
    # 分辨率标签
    width = exif_data.get('width') or image.width
    height = exif_data.get('height') or image.height
    
    if width and height:
        pixels = width * height
        if pixels >= 8000000:  # 800万像素以上
            tags.append('高清')
        if width > height:
            tags.append('横向')
        elif height > width:
            tags.append('竖向')
        else:
            tags.append('方形')
    
    # 有 GPS 信息
    if exif_data.get('gps_latitude') and exif_data.get('gps_longitude'):
        tags.append('有地理位置')
    
    return tags


def apply_exif_to_image(image_instance):
    """
    解析图片 EXIF 并应用到 Image 模型实例
    
    Args:
        image_instance: Image 模型实例
    """
    from apps.tags.models import Tag
    from apps.images.models import ImageTag
    
    if not image_instance.file:
        return
    
    try:
        # 解析 EXIF
        exif_data = parse_exif(image_instance.file)
        
        # 更新图片的 EXIF 字段
        image_instance.exif_camera_make = exif_data.get('camera_make', '')[:100]
        image_instance.exif_camera_model = exif_data.get('camera_model', '')[:100]
        image_instance.exif_datetime = exif_data.get('datetime')
        image_instance.exif_exposure_time = exif_data.get('exposure_time', '')[:50]
        image_instance.exif_f_number = exif_data.get('f_number', '')[:20]
        image_instance.exif_iso = exif_data.get('iso')
        image_instance.exif_focal_length = exif_data.get('focal_length', '')[:50]
        image_instance.exif_gps_latitude = exif_data.get('gps_latitude')
        image_instance.exif_gps_longitude = exif_data.get('gps_longitude')
        
        # 如果没有宽高信息，从 EXIF 获取
        if not image_instance.width and exif_data.get('width'):
            image_instance.width = exif_data['width']
        if not image_instance.height and exif_data.get('height'):
            image_instance.height = exif_data['height']
        
        image_instance.exif_parsed = True
        image_instance.save()
        
        # 生成自动标签
        auto_tag_names = generate_auto_tags(exif_data, image_instance)
        
        for tag_name in auto_tag_names:
            tag = Tag.get_or_create_tag(tag_name, tag_type='auto')
            # 检查是否已存在关联
            if not ImageTag.objects.filter(image=image_instance, tag=tag).exists():
                ImageTag.objects.create(image=image_instance, tag=tag)
        
        return exif_data
        
    except Exception as e:
        print(f"应用 EXIF 到图片时出错: {e}")
        return None
