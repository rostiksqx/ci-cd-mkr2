from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Image
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from datetime import date

# Create your tests here.

class GalleryViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test categories
        self.category1 = Category.objects.create(name='Nature')
        self.category2 = Category.objects.create(name='City')
        
        # Create test images
        test_image1 = SimpleUploadedFile(
            name='test_image1.jpg',
            content=b'',  # Empty content for test
            content_type='image/jpeg'
        )
        
        test_image2 = SimpleUploadedFile(
            name='test_image2.jpg',
            content=b'',  # Empty content for test
            content_type='image/jpeg'
        )
        
        self.image1 = Image.objects.create(
            title='Test Image 1',
            image=test_image1,
            created_date=date(2024, 1, 1),
            age_limit=18
        )
        self.image1.categories.add(self.category1)
        
        self.image2 = Image.objects.create(
            title='Test Image 2',
            image=test_image2,
            created_date=date(2024, 1, 2),
            age_limit=12
        )
        self.image2.categories.add(self.category2)

    def test_gallery_view_status_code(self):
        """Test gallery view returns 200 status code"""
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)

    def test_gallery_view_template(self):
        """Test gallery view uses correct template"""
        response = self.client.get(reverse('main'))
        self.assertTemplateUsed(response, 'gallery.html')

    def test_gallery_view_context(self):
        """Test gallery view returns correct context data"""
        response = self.client.get(reverse('main'))
        
        # Check if categories are in context
        self.assertIn('categories', response.context)
        self.assertEqual(len(response.context['categories']), 2)
        
        # Check if all categories are present
        category_names = [cat.name for cat in response.context['categories']]
        self.assertIn('Nature', category_names)
        self.assertIn('City', category_names)
        
        # Check if images are properly associated with categories
        for category in response.context['categories']:
            self.assertTrue(hasattr(category, 'image_set'))
            if category.name == 'Nature':
                self.assertEqual(len(category.image_set.all()), 1)
                self.assertEqual(category.image_set.first().title, 'Test Image 1')
            elif category.name == 'City':
                self.assertEqual(len(category.image_set.all()), 1)
                self.assertEqual(category.image_set.first().title, 'Test Image 2')

    def test_gallery_view_image_links(self):
        """Test gallery view contains correct links to image details"""
        response = self.client.get(reverse('main'))
        self.assertContains(response, f'href="{reverse("image_detail", args=[self.image1.id])}"')
        self.assertContains(response, f'href="{reverse("image_detail", args=[self.image2.id])}"')

    def test_image_detail_view_status_code(self):
        """Test image detail view returns 200 status code for existing image"""
        response = self.client.get(reverse('image_detail', args=[self.image1.id]))
        self.assertEqual(response.status_code, 200)

    def test_image_detail_view_404(self):
        """Test image detail view returns 404 for non-existent image"""
        response = self.client.get(reverse('image_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_image_detail_view_template(self):
        """Test image detail view uses correct template"""
        response = self.client.get(reverse('image_detail', args=[self.image1.id]))
        self.assertTemplateUsed(response, 'image_detail.html')

    def test_image_detail_view_context(self):
        """Test image detail view returns correct image data"""
        response = self.client.get(reverse('image_detail', args=[self.image1.id]))
        
        # Check if image is in context
        self.assertIn('image', response.context)
        
        # Check image data
        image = response.context['image']
        self.assertEqual(image.title, 'Test Image 1')
        self.assertEqual(image.created_date, date(2024, 1, 1))
        self.assertEqual(image.age_limit, 18)
        self.assertTrue(image.image)  # Check if image file exists
        
        # Check if image belongs to correct category
        self.assertEqual(image.categories.first().name, 'Nature')

    def test_image_detail_view_content(self):
        """Test image detail view displays correct content"""
        response = self.client.get(reverse('image_detail', args=[self.image1.id]))
        
        # Check if image title is displayed
        self.assertContains(response, 'Test Image 1')
        
        # Check if image URL is in the response
        self.assertContains(response, self.image1.image.url)

    def tearDown(self):
        # Clean up test files
        for image in Image.objects.all():
            if image.image:
                if os.path.isfile(image.image.path):
                    os.remove(image.image.path)
