from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, Product
from store.product_data import CATEGORIES


class Command(BaseCommand):
    help = "Seeds the database with 10 categories and 100 demo products (with matching placeholder images)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help="Delete all existing categories and products before seeding."
        )

    def handle(self, *args, **options):
        if options['reset']:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing categories and products."))

        product_id = 1
        categories_created = 0
        products_created = 0

        for cat_data in CATEGORIES:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'color': cat_data['color'],
                    'icon': cat_data['icon'],
                    'image': f"store/images/categories/{cat_data['slug']}.jpg",
                },
            )
            if created:
                categories_created += 1

            for product_tuple in cat_data['products']:
                name, price, discount_price, rating, is_featured, description = product_tuple
                slug = slugify(name)[:220]
                image_path = f"store/images/products/product_{product_id}.jpg"

                _, was_created = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'category': category,
                        'name': name,
                        'description': description,
                        'short_description': description[:120],
                        'image': image_path,
                        'price': price,
                        'discount_price': discount_price,
                        'rating': rating,
                        'is_featured': is_featured,
                        'stock': 50,
                    },
                )
                if was_created:
                    products_created += 1
                product_id += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. {categories_created} categories and {products_created} products created "
            f"(catalog defines {len(CATEGORIES)} categories / {product_id - 1} products total)."
        ))
