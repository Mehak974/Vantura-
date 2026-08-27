import csv
import urllib.request
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import Product, Category
from django.utils.text import slugify
import os

class Command(BaseCommand):
    help = 'Import products from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))
            return

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0

            for row in reader:
                name = row.get('Name', '').strip()
                if not name:
                    continue
                
                # Check if product already exists
                if Product.objects.filter(name=name).exists():
                    self.stdout.write(self.style.WARNING(f"Product '{name}' already exists. Skipping."))
                    continue

                # Category handling
                categories_str = row.get('Categories', '')
                category_name = 'Uncategorized'
                if categories_str:
                    cats = [c.strip() for c in categories_str.split(',')]
                    # Use the last category as the main one, typically most specific, or if "All Products" is first, use the second
                    category_name = cats[-1] if len(cats) > 0 else 'Uncategorized'
                
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={'slug': slugify(category_name)}
                )

                # Pricing
                reg_price = row.get('Regular price', '').strip()
                sale_price = row.get('Sale price', '').strip()
                
                price = 0
                if reg_price:
                    try: price = float(reg_price)
                    except ValueError: pass
                
                compare_price = None
                if sale_price:
                    try: compare_price = float(sale_price)
                    except ValueError: pass

                # Fallback if no reg price but there is a sale price
                if price == 0 and compare_price is not None:
                    price = compare_price
                    compare_price = None
                elif price == 0:
                    price = 10.00 # fallback

                is_featured = row.get('Is featured?', '0') == '1'
                
                # Descriptions
                short_desc = row.get('Short description', '')[:300]
                desc = row.get('Description', '')
                
                product = Product(
                    name=name,
                    category=category,
                    description=desc,
                    short_description=short_desc,
                    price=price,
                    compare_price=compare_price,
                    stock=100,
                    is_featured=is_featured,
                    is_active=True
                )
                
                # Image downloading
                images_str = row.get('Images', '')
                if images_str:
                    urls = [u.strip() for u in images_str.split(',')]
                    # Download first image
                    if len(urls) > 0 and urls[0]:
                        try:
                            # Add headers to avoid 403 Forbidden
                            req = urllib.request.Request(urls[0], headers={'User-Agent': 'Mozilla/5.0'})
                            response = urllib.request.urlopen(req)
                            file_name = urls[0].split('/')[-1].split('?')[0] # remove query params
                            product.image.save(file_name, ContentFile(response.read()), save=False)
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Error downloading image 1 for {name}: {e}"))
                    # Download second image
                    if len(urls) > 1 and urls[1]:
                        try:
                            req = urllib.request.Request(urls[1], headers={'User-Agent': 'Mozilla/5.0'})
                            response = urllib.request.urlopen(req)
                            file_name = urls[1].split('/')[-1].split('?')[0]
                            product.image2.save(file_name, ContentFile(response.read()), save=False)
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Error downloading image 2 for {name}: {e}"))
                    # Download third image
                    if len(urls) > 2 and urls[2]:
                        try:
                            req = urllib.request.Request(urls[2], headers={'User-Agent': 'Mozilla/5.0'})
                            response = urllib.request.urlopen(req)
                            file_name = urls[2].split('/')[-1].split('?')[0]
                            product.image3.save(file_name, ContentFile(response.read()), save=False)
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Error downloading image 3 for {name}: {e}"))

                product.save()
                count += 1
                self.stdout.write(self.style.SUCCESS(f"Imported product: {name}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} products"))
