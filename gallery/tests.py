from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Image
from django.core.files.uploadedfile import SimpleUploadedFile
import os

# Create your tests here.

class GalleryViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test categories
        self.category1 = Category.objects.create(name='Nature')
        self.category2 = Category.objects.create(name='City')
        
        # Create test image
        test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # Empty content for test
            content_type='image/jpeg'
        )
        
        self.image = Image.objects.create(
            title='Test Image',
            image=test_image,
            created_date='2024-01-01',
            age_limit=18
        )
        self.image.categories.add(self.category1)

    def test_gallery_view(self):
        """Test gallery view returns correct context and template"""
        response = self.client.get(reverse('main'))
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check template used
        self.assertTemplateUsed(response, 'gallery.html')
        
        # Check context data
        self.assertIn('categories', response.context)
        self.assertEqual(len(response.context['categories']), 2)
        
        # Check if our test category is in the response
        category_names = [cat.name for cat in response.context['categories']]
        self.assertIn('Nature', category_names)
        self.assertIn('City', category_names)

    def test_image_detail_view(self):
        """Test image detail view returns correct image"""
        response = self.client.get(reverse('image_detail', args=[self.image.id]))
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check template used
        self.assertTemplateUsed(response, 'image_detail.html')
        
        # Check context data
        self.assertIn('image', response.context)
        self.assertEqual(response.context['image'].title, 'Test Image')
        
    def test_image_detail_view_404(self):
        """Test image detail view returns 404 for non-existent image"""
        response = self.client.get(reverse('image_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        # Clean up test files
        for image in Image.objects.all():
            if image.image:
                if os.path.isfile(image.image.path):
                    os.remove(image.image.path)
