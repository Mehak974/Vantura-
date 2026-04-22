# Generated migration for Vantura Store

from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import store.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('image', models.ImageField(blank=True, null=True, upload_to='categories/',
                    validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])])),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name_plural': 'Categories', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='subcategories', to='store.category')),
            ],
            options={'verbose_name_plural': 'SubCategories', 'ordering': ['name'],
                     'unique_together': {('category', 'slug')}},
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('description', models.TextField()),
                ('short_description', models.CharField(blank=True, max_length=300)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10,
                    validators=[django.core.validators.MinValueValidator(0)])),
                ('compare_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True,
                    validators=[django.core.validators.MinValueValidator(0)])),
                ('stock', models.PositiveIntegerField(default=0)),
                ('sku', models.CharField(blank=True, max_length=100, unique=True)),
                ('image', models.ImageField(upload_to=store.models.product_image_path,
                    validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])])),
                ('image2', models.ImageField(blank=True, null=True, upload_to=store.models.product_image_path,
                    validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])])),
                ('image3', models.ImageField(blank=True, null=True, upload_to=store.models.product_image_path,
                    validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])])),
                ('weight', models.CharField(blank=True, max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_new', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='products', to='store.category')),
                ('subcategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='products', to='store.subcategory')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=40, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1,
                    validators=[django.core.validators.MinValueValidator(1)])),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='items', to='store.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(blank=True, max_length=20, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'),
                    ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'),
                    ('cancelled', 'Cancelled'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('payment_method', models.CharField(choices=[('cod', 'Cash on Delivery'),
                    ('card', 'Credit/Debit Card'), ('paypal', 'PayPal')], default='cod', max_length=20)),
                ('payment_status', models.BooleanField(default=False)),
                ('full_name', models.CharField(max_length=150)),
                ('email', models.EmailField()),
                ('phone', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('zip_code', models.CharField(max_length=20)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('product_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField()),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='items', to='store.order')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                    to='store.product')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5)])),
                ('title', models.CharField(max_length=100)),
                ('comment', models.TextField(max_length=1000)),
                ('is_approved', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='reviews', to='store.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('product', 'user')}},
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField()),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField(max_length=2000)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
