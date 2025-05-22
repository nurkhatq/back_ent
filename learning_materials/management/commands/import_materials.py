# # learning_materials/management/commands/import_materials.py
# import os
# from django.core.management.base import BaseCommand
# from django.core.files import File
# from django.core.files.base import ContentFile
# from django.db import transaction
# from learning_materials.models import Section, Material, MaterialImage
# from learning_materials.utils import DocxToHtmlConverter
# import logging

# logger = logging.getLogger(__name__)

# class Command(BaseCommand):
#     help = 'Import learning materials from DOCX files'

#     def handle(self, *args, **options):
#         base_dir = '/code/bolimder'
        
#         if not os.path.exists(base_dir):
#             self.stderr.write(f"Directory {base_dir} does not exist!")
#             return

#         for dir_name in sorted(os.listdir(base_dir)):
#             if dir_name.startswith('_') or not os.path.isdir(os.path.join(base_dir, dir_name)):
#                 continue

#             try:
#                 with transaction.atomic():
#                     self._process_directory(os.path.join(base_dir, dir_name))
#             except Exception as e:
#                 self.stderr.write(f"Error processing directory {dir_name}: {str(e)}")
#                 logger.exception(f"Full error details for {dir_name}:")

#     def _process_directory(self, dir_path):
#         dir_name = os.path.basename(dir_path)
#         parts = dir_name.split('_', 1)
        
#         if len(parts) != 2:
#             raise ValueError(f"Invalid directory name format: {dir_name}")
            
#         try:
#             section_num = int(parts[0])
#             section_title = parts[1]
#         except (IndexError, ValueError) as e:
#             raise ValueError(f"Could not parse section number from {dir_name}: {str(e)}")

#         # Create or update section
#         section, created = Section.objects.get_or_create(
#             number=section_num,
#             defaults={'title': section_title}
#         )
        
#         status = 'Created' if created else 'Updated'
#         self.stdout.write(f"{status} section: {section.title}")

#         # Process DOCX files
#         for file_name in os.listdir(dir_path):
#             if not file_name.endswith('.docx'):
#                 continue

#             self._process_file(section, os.path.join(dir_path, file_name))

#     def _process_file(self, section, file_path):
#         file_name = os.path.basename(file_path)
        
#         try:
#             # Convert DOCX to HTML
#             converter = DocxToHtmlConverter()
#             result = converter.convert(file_path)
            
#             # Create material
#             with open(file_path, 'rb') as f:
#                 material = Material.objects.create(
#                     section=section,
#                     title=os.path.splitext(file_name)[0],
#                     content_html=result['html'],
#                     has_tables=result['has_tables'],
#                     has_formulas=result['has_formulas'],
#                     has_images=bool(result['images']),
#                     original_file=File(f, name=file_name)
#                 )

#             # Save images
#             for idx, img_data in enumerate(result['images']):
#                 try:
#                     image_file = ContentFile(
#                         img_data['image_data'],
#                         name=f'{material.id}_image_{idx}.{img_data["format"]}'
#                     )
#                     MaterialImage.objects.create(
#                         material=material,
#                         image=image_file,
#                         order=idx
#                     )
#                 except Exception as e:
#                     logger.error(f"Error saving image {idx} for {file_name}: {str(e)}")

#             self.stdout.write(
#                 self.style.SUCCESS(f'Imported material: {material.title}')
#             )
            
#         except Exception as e:
#             self.stderr.write(f"Error processing file {file_name}: {str(e)}")
#             logger.exception(f"Full error details for {file_name}:")

# learning_materials/management/commands/import_materials.py
import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import transaction
from learning_materials.models import Section, Material, MaterialImage
from learning_materials.utils import DocxToHtmlConverter
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import learning materials from DOCX files'

    def handle(self, *args, **options):
        base_dir = 'bolimder'
        
        if not os.path.exists(base_dir):
            self.stderr.write(f"Directory {base_dir} does not exist!")
            return

        for dir_name in sorted(os.listdir(base_dir)):
            if dir_name.startswith('_') or not os.path.isdir(os.path.join(base_dir, dir_name)):
                continue

            try:
                with transaction.atomic():
                    self._process_directory(os.path.join(base_dir, dir_name))
            except Exception as e:
                self.stderr.write(f"Error processing directory {dir_name}: {str(e)}")
                logger.exception(f"Full error details for {dir_name}:")

    def _process_directory(self, dir_path):
        dir_name = os.path.basename(dir_path)
        parts = dir_name.split('_', 1)
        
        if len(parts) != 2:
            raise ValueError(f"Invalid directory name format: {dir_name}")
            
        try:
            section_num = int(parts[0])
            section_title = parts[1]
        except (IndexError, ValueError) as e:
            raise ValueError(f"Could not parse section number from {dir_name}: {str(e)}")

        # Create or update section
        section, created = Section.objects.get_or_create(
            number=section_num,
            defaults={'title': section_title}
        )
        
        status = 'Created' if created else 'Updated'
        self.stdout.write(f"{status} section: {section.title}")

        # Process DOCX files
        for file_name in os.listdir(dir_path):
            if not file_name.endswith('.docx'):
                continue

            self._process_file(section, os.path.join(dir_path, file_name))

    def _process_file(self, section, file_path):
        file_name = os.path.basename(file_path)
        
        try:
            # Сначала создаем запись материала
            with open(file_path, 'rb') as f:
                material = Material.objects.create(
                    section=section,
                    title=os.path.splitext(file_name)[0],
                    content_html='',  # Временно пустой HTML
                    original_file=File(f, name=file_name)
                )
            
            # Теперь, когда у нас есть ID материала, конвертируем с сохранением изображений
            converter = DocxToHtmlConverter()
            result = converter.convert(file_path, material.id)
            
            # Обновляем материал с полученным HTML и флагами
            material.content_html = result['html']
            material.has_tables = result['has_tables']
            material.has_formulas = result['has_formulas']
            material.has_images = bool(result['saved_images'])
            material.save()
            
            # Создаем записи для изображений
            for img_data in result['saved_images']:
                MaterialImage.objects.create(
                    material=material,
                    image=img_data['image'],
                    caption=img_data['caption'],
                    order=img_data['order']
                )
                
            self.stdout.write(
                self.style.SUCCESS(f'Imported material: {material.title}')
            )
                
        except Exception as e:
            self.stderr.write(f"Error processing file {file_name}: {str(e)}")
            logger.exception(f"Full error details for {file_name}:")