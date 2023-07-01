from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from books.models import Book, BookReview
from users.models import CustomUser


class BookReviewAPITestCase(APITestCase):
    def setUp(self) -> None:  # darsda none yoq edi
        self.user = CustomUser.objects.create(username="shuhrat", first_name="ilhom")
        self.user.set_password("somepass")
        self.user.save()
        self.client.login(username="shuhrat", password="somepass")

    def test_book_review_detail(self):
        book = Book.objects.create(title="book3", description="description3", isbn="555555")
        br = BookReview.objects.create(book=book, user=self.user, stars_given=5, comment="good book")

        response = self.client.get(reverse('api:review-detail', kwargs={"id": br.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], br.id)
        self.assertEqual(response.data['stars_given'], 5)
        self.assertEqual(response.data['comment'], "good book")
        self.assertEqual(response.data['book']['id'], br.book.id)
        self.assertEqual(response.data['book']['title'], "book3")
        self.assertEqual(response.data['book']['description'], "description3")
        self.assertEqual(response.data['book']['isbn'], "555555")
        self.assertEqual(response.data['user']['id'], self.user.id)
        self.assertEqual(response.data['user']['first_name'], 'ilhom')
        self.assertEqual(response.data['user']['username'], "shuhrat")

    def test_delete_review(self):
        book = Book.objects.create(title="book3", description="description3", isbn="555555")
        br = BookReview.objects.create(book=book, user=self.user, stars_given=5, comment="good book")

        response = self.client.delete(reverse('api:review-detail', kwargs={"id": br.id}))
        self.assertEqual(response.status_code, 204)
        self.assertFalse((BookReview.objects.filter(id=br.id).exists()))

    def test_patch_review(self):
        book = Book.objects.create(title="book3", description="description3", isbn="555555")
        br = BookReview.objects.create(book=book, user=self.user, stars_given=5, comment="good book")

        response = self.client.patch(reverse('api:review-detail', kwargs={"id": br.id}), data={"stars_given": 4})

        br.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(br.stars_given, 4)

    def test_put_review(self):
        book = Book.objects.create(title="book3", description="description3", isbn="555555")
        br = BookReview.objects.create(book=book, user=self.user, stars_given=5, comment="good book")

        response = self.client.put(reverse('api:review-detail', kwargs={"id": br.id}),
                                   data={"stars_given": 4, "comment": "norm book", "user_id": self.user.id,
                                         'book_id': book.id})
        br.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(br.stars_given, 4)
        self.assertEqual(br.comment, "norm book")


    def test_create_review(self):
        book = Book.objects.create(title="book3", description="description3", isbn="555555")
        data = {
            "stars_given": 2,
            "comment": "bad book",
            "user_id": self.user.id,
            "book_id": book.id
        }

        response = self.client.post(reverse("api:review-list"), data=data)
        br = BookReview.objects.get(book=book)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(br.stars_given, 2)
        self.assertEqual(br.comment, 'bad book')


    def test_book_review_list(self):
        user_two = CustomUser.objects.create(username="shuhrat2", first_name="ilhom2")
        book = Book.objects.create(title="book3", description="description3", isbn="555555")
        br = BookReview.objects.create(book=book, user=self.user, stars_given=5, comment="good book")
        br_two = BookReview.objects.create(book=book, user=user_two, stars_given=3, comment="not good book")

        response = self.client.get(reverse("api:review-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['count'], 2)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)

        self.assertEqual(response.data['results'][0]['id'], br_two.id)
        self.assertEqual(response.data['results'][0]['stars_given'], br_two.stars_given)
        self.assertEqual(response.data['results'][0]['comment'], br_two.comment)
        self.assertEqual(response.data['results'][1]['id'], br.id)
        self.assertEqual(response.data['results'][1]['stars_given'], br.stars_given)
        self.assertEqual(response.data['results'][1]['comment'], br.comment)
