from django.test import TestCase
from django.urls import reverse

from books.models import Book, BookReview
from users.models import CustomUser


class HomePageTestCase(TestCase):
    def test_paginated_list(self):
        book = Book.objects.create(title="sport", description="description1", isbn="124243")

        user = CustomUser.objects.create(
            username="wukhrat",
            first_name="shuhrat",
            last_name="ilhom",
            email="shuhrat@gmail.com"
        )
        user.set_password("somepass")
        user.save()

        review1 = BookReview.objects.create(book=book, user=user, stars_given=3, comment="good book")
        review2 = BookReview.objects.create(book=book, user=user, stars_given=4, comment="eha")
        review3 = BookReview.objects.create(book=book, user=user, stars_given=2, comment="boladi")

        response = self.client.get(reverse("home_page") + "?page_size=2")

        self.assertContains(response, review3.comment)
        self.assertContains(response, review2.comment)
        self.assertNotContains(response, review1.comment)

