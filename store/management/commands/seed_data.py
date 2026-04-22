"""
Management command: python manage.py seed_data
Seeds all categories, subcategories, and sample products for Vantura.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, SubCategory, Product
from decimal import Decimal


CATEGORY_DATA = {
    'Health & Supplements': {
        'icon': '[H&S]',
        'description': 'Premium health supplements for energy, muscle building, recovery, and wellness.',
        'subs': [
            'Energy', 'Fat Burner', 'Herbal Formula', 'Magnesium',
            'Muscle Builder', 'Pre Workout', 'Protein', 'Recovery', 'Snacks',
        ]
    },
    'Pet Care': {
        'icon': '[PET]',
        'description': 'Everything your pet needs to thrive.',
        'subs': ['Pet Convincer']
    },
    'Home & Outdoor': {
        'icon': '[HOME]',
        'description': 'Quality products for your home and outdoor adventures.',
        'subs': [
            'Fishing Accessories', 'Furniture', 'Hozon',
            'Kitchen', 'Lightening', 'Sonars',
        ]
    },
    'Beauty & Personal Care': {
        'icon': '[BEAUTY]',
        'description': 'Professional beauty and personal care products.',
        'subs': [
            'Bloodline Blacks', 'Conditioner', 'Ink Sets', 'Keratin',
            'Shampoo', 'Tattoo Ink', 'UV Blacklight Colors',
        ]
    },
    'Tools': {
        'icon': '[TOOLS]',
        'description': 'Professional-grade tools for every job.',
        'subs': [
            'Chemical Injector', 'Deburring Tool', 'Filters', 'Flow Switch',
            'Ladder Level', 'Spray Gun', 'Trimmer', 'Unloaders',
        ]
    },
    'Toys': {
        'icon': '[TOYS]',
        'description': 'Collectibles, anime merch, and fun toys for all ages.',
        'subs': [
            'Cards', 'Dragon Ball Z', 'Full Metal Alchemist',
            'Key Ring', 'Naruto', 'One Piece', 'Plush Toys', 'Sonic',
        ]
    },
}

SAMPLE_PRODUCTS = [
    # Health & Supplements
    {
        'name': 'WheyMax Pro Protein 5lbs',
        'sku': 'HS-WHEY-001',
        'category': 'Health & Supplements', 'subcategory': 'Protein',
        'price': '49.99', 'compare_price': '64.99',
        'description': 'Premium whey protein isolate with 25g protein per serving. Supports muscle growth and recovery. Available in Chocolate Fudge, Vanilla Ice Cream, and Strawberry.',
        'short_description': '25g protein per serving. Banned substance tested.',
        'stock': 85, 'weight': '5 lbs', 'is_featured': True, 'is_new': True,
    },
    {
        'name': 'Pre-Surge Extreme Pre-Workout',
        'sku': 'HS-PRE-002',
        'category': 'Health & Supplements', 'subcategory': 'Pre Workout',
        'price': '39.99', 'compare_price': '54.99',
        'description': 'Explosive energy and focus formula. Contains 200mg caffeine, beta-alanine, and citrulline malate for unreal pumps and performance.',
        'short_description': 'Energy, pump, and focus in every scoop.',
        'stock': 60, 'weight': '300g', 'is_featured': True,
    },
    {
        'name': 'MagRelax Magnesium Glycinate',
        'sku': 'HS-MAG-003',
        'category': 'Health & Supplements', 'subcategory': 'Magnesium',
        'price': '24.99',
        'description': 'High-absorption magnesium glycinate for deep sleep, muscle recovery, and stress relief. 400mg elemental magnesium per serving.',
        'short_description': 'Sleep better, recover faster.',
        'stock': 120, 'is_new': True,
    },
    {
        'name': 'ThermoFire Fat Burner',
        'sku': 'HS-FAT-004',
        'category': 'Health & Supplements', 'subcategory': 'Fat Burner',
        'price': '34.99', 'compare_price': '44.99',
        'description': 'Thermogenic fat burning formula with green tea extract, L-carnitine, and CLA. Boosts metabolism and energy naturally.',
        'short_description': 'Accelerate your fat loss journey.',
        'stock': 75, 'is_featured': True,
    },
    {
        'name': 'Recovery Rush BCAA+',
        'sku': 'HS-REC-005',
        'category': 'Health & Supplements', 'subcategory': 'Recovery',
        'price': '29.99',
        'description': '2:1:1 BCAA ratio with added glutamine and electrolytes. Reduces muscle soreness and accelerates recovery.',
        'stock': 90,
    },
    {
        'name': 'HerbalVit Immunity Blend',
        'sku': 'HS-HERB-006',
        'category': 'Health & Supplements', 'subcategory': 'Herbal Formula',
        'price': '19.99',
        'description': 'Powerful blend of elderberry, echinacea, ashwagandha, and zinc. Supports immune function and reduces stress.',
        'stock': 110, 'is_new': True,
    },
    # Pet Care
    {
        'name': 'PetSafe Training Spray',
        'sku': 'PC-SPRAY-001',
        'category': 'Pet Care', 'subcategory': 'Pet Convincer',
        'price': '15.99',
        'description': 'Natural citronella spray for gentle pet training. Safe for dogs and cats. Deters unwanted behavior without harm.',
        'short_description': 'Humane, effective pet training aid.',
        'stock': 55, 'is_new': True,
    },
    # Home & Outdoor
    {
        'name': 'ProAngler Fishing Rod Set',
        'sku': 'HO-FISH-001',
        'category': 'Home & Outdoor', 'subcategory': 'Fishing Accessories',
        'price': '89.99', 'compare_price': '119.99',
        'description': 'Complete fishing starter set: 7ft carbon fiber rod, spinning reel, 150m line, and tackle box. Perfect for beginners and enthusiasts.',
        'stock': 35, 'is_featured': True,
    },
    {
        'name': 'Nordic Ergonomic Office Chair',
        'sku': 'HO-FURN-002',
        'category': 'Home & Outdoor', 'subcategory': 'Furniture',
        'price': '249.99', 'compare_price': '349.99',
        'description': 'Scandinavian-designed ergonomic chair with lumbar support, adjustable armrests, and breathable mesh back. Supports up to 300lbs.',
        'stock': 20, 'is_featured': True, 'is_new': True,
    },
    {
        'name': 'Hozon Brass Siphon Mixer',
        'sku': 'HO-HOZ-003',
        'category': 'Home & Outdoor', 'subcategory': 'Hozon',
        'price': '32.99',
        'description': 'Heavy-duty brass Hozon siphon mixer for applying fertilizers and pesticides through hose. 1:16 dilution ratio.',
        'stock': 45,
    },
    {
        'name': 'Ultra LED Strip Lights 10m',
        'sku': 'HO-LIGHT-004',
        'category': 'Home & Outdoor', 'subcategory': 'Lightening',
        'price': '27.99',
        'description': 'Smart RGB LED strip lights with app control, 16 million colors, music sync, and timer. Waterproof for indoor/outdoor use.',
        'short_description': 'Transform any space with 16M colors.',
        'stock': 150, 'is_new': True,
    },
    # Beauty & Personal Care
    {
        'name': 'Keratin Smoothing Treatment 500ml',
        'sku': 'BC-KER-001',
        'category': 'Beauty & Personal Care', 'subcategory': 'Keratin',
        'price': '44.99', 'compare_price': '59.99',
        'description': 'Professional Brazilian keratin treatment. Eliminates frizz, adds shine, and smooths hair for up to 3 months. Formaldehyde-free.',
        'short_description': 'Salon-quality smooth hair at home.',
        'stock': 65, 'is_featured': True,
    },
    {
        'name': 'Bloodline Premium Black Ink 30ml',
        'sku': 'BC-INK-002',
        'category': 'Beauty & Personal Care', 'subcategory': 'Bloodline Blacks',
        'price': '18.99',
        'description': 'Ultra-black, high-concentration tattoo ink. Vegan, sterilized, and EU regulation compliant. Perfect for bold lines and solid fills.',
        'stock': 200, 'is_new': True,
    },
    {
        'name': 'UV Blacklight Tattoo Ink Set 8pcs',
        'sku': 'BC-UV-003',
        'category': 'Beauty & Personal Care', 'subcategory': 'UV Blacklight Colors',
        'price': '54.99',
        'description': 'Set of 8 UV-reactive tattoo inks. Invisible in daylight, glows brilliantly under blacklight. Vegan and skin-safe certified.',
        'short_description': '8-color UV ink set — invisible by day, glowing by night.',
        'stock': 40, 'is_featured': True,
    },
    # Tools
    {
        'name': 'AirMax HVLP Spray Gun',
        'sku': 'TL-SPRAY-001',
        'category': 'Tools', 'subcategory': 'Spray Gun',
        'price': '74.99', 'compare_price': '99.99',
        'description': 'Professional HVLP spray gun with 1.4mm nozzle, 600cc gravity cup, and adjustable fan/flow control. Ideal for automotive and furniture finishing.',
        'stock': 30, 'is_featured': True,
    },
    {
        'name': 'DeburMaster Pro Rotary Tool',
        'sku': 'TL-DEB-002',
        'category': 'Tools', 'subcategory': 'Deburring Tool',
        'price': '22.99',
        'description': 'Heavy-duty deburring tool with 10 interchangeable blades. Removes burrs from metal, plastic, and wood. Ergonomic grip handle.',
        'stock': 80, 'is_new': True,
    },
    {
        'name': 'Smart Flow Switch 1-inch',
        'sku': 'TL-FLOW-003',
        'category': 'Tools', 'subcategory': 'Flow Switch',
        'price': '38.99',
        'description': 'Electronic flow switch for water and fluid systems. Adjustable flow rate trigger, IP65 waterproof, 110-240V AC compatible.',
        'stock': 50,
    },
    # Toys
    {
        'name': 'Goku Ultra Instinct Figure 30cm',
        'sku': 'TY-DBZ-001',
        'category': 'Toys', 'subcategory': 'Dragon Ball Z',
        'price': '34.99', 'compare_price': '44.99',
        'description': 'Highly detailed Goku Ultra Instinct articulated figure. 30cm tall with 16 points of articulation. Includes Kamehameha effect parts.',
        'short_description': 'Premium 30cm DBZ figure with accessories.',
        'stock': 55, 'is_featured': True, 'is_new': True,
    },
    {
        'name': 'Naruto Akatsuki Cloak Plush 45cm',
        'sku': 'TY-NAR-002',
        'category': 'Toys', 'subcategory': 'Naruto',
        'price': '27.99',
        'description': 'Super soft Naruto plush in full Akatsuki cloak. 45cm tall. Machine washable. Officially licensed design.',
        'stock': 70, 'is_new': True,
    },
    {
        'name': 'One Piece Straw Hat Crew Card Set',
        'sku': 'TY-OP-003',
        'category': 'Toys', 'subcategory': 'Cards',
        'price': '14.99',
        'description': '54-card premium quality playing card set featuring the full Straw Hat crew. Plastic-coated for durability. Collector\'s tin included.',
        'stock': 200, 'is_featured': True,
    },
    {
        'name': 'Edward Elric Automail Arm Replica',
        'sku': 'TY-FMA-004',
        'category': 'Toys', 'subcategory': 'Full Metal Alchemist',
        'price': '42.99',
        'description': 'High-quality resin replica of Edward Elric\'s automail arm. 25cm long, fully detailed. Display stand included.',
        'stock': 25,
    },
    {
        'name': 'Sonic the Hedgehog Speed Ring Keychain',
        'sku': 'TY-SON-005',
        'category': 'Toys', 'subcategory': 'Key Ring',
        'price': '8.99',
        'description': 'Die-cast metal Sonic ring keychain. Gold finish. 4cm diameter. Perfect for fans and collectors.',
        'stock': 300, 'is_new': True,
    },
]


class Command(BaseCommand):
    help = 'Seed Vantura database with categories, subcategories, and sample products'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Delete existing data before seeding')
        parser.add_argument('--admin', action='store_true', help='Also create a superuser admin/admin123')

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Flushing existing data...')
            Product.objects.all().delete()
            SubCategory.objects.all().delete()
            Category.objects.all().delete()

        self.stdout.write(self.style.MIGRATE_HEADING('\n--- Seeding Vantura database ---\n'))

        # Create categories and subcategories
        cat_map = {}
        sub_map = {}
        for cat_name, data in CATEGORY_DATA.items():
            cat, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    'icon': data['icon'],
                    'description': data['description'],
                    'is_active': True,
                }
            )
            cat_map[cat_name] = cat
            action = 'Created' if created else 'Found'
            self.stdout.write(f"  {data['icon']}  {action} category: {cat_name}")

            for sub_name in data['subs']:
                sub, s_created = SubCategory.objects.get_or_create(
                    category=cat,
                    name=sub_name,
                    defaults={'is_active': True}
                )
                sub_map[(cat_name, sub_name)] = sub

        self.stdout.write(f'\n  OK: {Category.objects.count()} categories, {SubCategory.objects.count()} subcategories\n')

        # Create sample products
        created_count = 0
        for p in SAMPLE_PRODUCTS:
            cat = cat_map.get(p['category'])
            sub = sub_map.get((p['category'], p.get('subcategory')))
            if not cat:
                continue

            product, created = Product.objects.get_or_create(
                sku=p['sku'],
                defaults={
                    'name': p['name'],
                    'category': cat,
                    'subcategory': sub,
                    'description': p['description'],
                    'short_description': p.get('short_description', ''),
                    'price': Decimal(p['price']),
                    'compare_price': Decimal(p['compare_price']) if p.get('compare_price') else None,
                    'stock': p.get('stock', 50),
                    'weight': p.get('weight', ''),
                    'is_active': True,
                    'is_featured': p.get('is_featured', False),
                    'is_new': p.get('is_new', False),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"  [PRODUCT] {p['name']}")

        self.stdout.write(f'\n  OK: {created_count} new products created\n')

        # Create admin user
        if options['admin']:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@vantura.com', 'admin123')
                self.stdout.write(self.style.SUCCESS('  ADMIN created: admin / admin123'))
            else:
                self.stdout.write('  Admin user already exists')

        self.stdout.write(self.style.SUCCESS('\n--- Seeding complete! Vantura is ready ---\n'))
        self.stdout.write('  Run: python manage.py runserver')
        self.stdout.write('  Admin: http://localhost:8000/admin/')
        self.stdout.write('  Store: http://localhost:8000/\n')
