from django.test import TestCase
from django.urls import reverse
from books.models import Book
from users.models import CustomUser


class BooksTestCase(TestCase):
    def test_no_books(self):
        response = self.client.get(reverse("books:list"))
        self.assertContains(response, "No books found.")

    def test_book_list(self):
        book1 = Book.objects.create(title="book1", description="description1", isbn="124243")
        book2 = Book.objects.create(title="book2", description="description2", isbn="234555")
        book3 = Book.objects.create(title="book3", description="description3", isbn="555555")

        response = self.client.get(reverse("books:list") + "?page_size=2")

        books = Book.objects.all()

        for book in [book1, book2]:
            self.assertContains(response, book.title)
        self.assertNotContains(response, book3.title)
        response = self.client.get(reverse("books:list") + "?page=2&page_size=2")

        self.assertContains(response, book3.title)

    def test_detail_page(self):
        book = Book.objects.create(title="book3", description="description3", isbn="555555")
        response = self.client.get(reverse("books:detail", kwargs={"id": book.id}))

        self.assertContains(response, book.title)
        self.assertContains(response, book.description)

    def test_search_books(self):
        book1 = Book.objects.create(title="sport", description="description1", isbn="124243")
        book2 = Book.objects.create(title="reading", description="description2", isbn="234555")
        book3 = Book.objects.create(title="recitation", description="description3", isbn="555555")

        response = self.client.get(reverse("books:list") + "?q=sport")
        self.assertContains(response, book1.title)
        self.assertNotContains(response, book2.title)
        self.assertNotContains(response, book3.title)

        response = self.client.get(reverse("books:list") + "?q=reading")
        self.assertContains(response, book2.title)
        self.assertNotContains(response, book1.title)
        self.assertNotContains(response, book3.title)

        response = self.client.get(reverse("books:list") + "?q=recitation")
        self.assertContains(response, book3.title)
        self.assertNotContains(response, book1.title)
        self.assertNotContains(response, book2.title)


class BookReviewTestCase(TestCase):
    def test_add_review(self):
        book = Book.objects.create(title="book3", description="description3", isbn="555555")
        user = CustomUser.objects.create(
            username="wukhrat",
            first_name="shuhrat",
            last_name="ilhom",
            email="shuhrat@gmail.com"
        )
        user.set_password("somepass")
        user.save()

        self.client.login(username="wukhrat", password="somepass")

        self.client.post(reverse("books:reviews", kwargs={"id": book.id}), data={
            "stars_given": 3,
            "comment": 'a;lskdfj'
        })

        book_reviews = book.bookreview_set.all()

        self.assertEqual(book_reviews.count(), 1)
        self.assertEqual(book_reviews[0].stars_given, 3)
        self.assertEqual(book_reviews[0].comment, "a;lskdfj")
        self.assertEqual(book_reviews[0].book, book)
        self.assertEqual(book_reviews[0].user, user)



