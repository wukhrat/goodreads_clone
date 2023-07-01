from django.contrib.auth import get_user
from users.models import CustomUser
from django.test import TestCase
from django.urls import reverse


class RegistrationTestCase(TestCase):
    def test_user_account_is_created(self):
        self.client.post(reverse("users:register"),
                         data={
                             "username": "wukhrat",
                             "first_name": "wukhrat",
                             "last_name": "ilhom",
                             "email": "ilihomjonovsh@gmail.com",
                             "password": "1234"
                         })

        user = CustomUser.objects.get(username="wukhrat")

        self.assertEquals(user.first_name, "wukhrat")
        self.assertEquals(user.last_name, "ilhom")
        self.assertEquals(user.email, "ilihomjonovsh@gmail.com")
        self.assertNotEquals(user.password, "1234")
        self.assertTrue(user.check_password("1234"))

    def test_required_fields(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "first_name": "shuhrat",
                "email": "shuhrat@gamil.com"
            }
        )
        user_count = CustomUser.objects.count()
        self.assertEquals(user_count, 0)
        self.assertFormError(response, "form", "username", "This field is required.")
        self.assertFormError(response, "form", "password", "This field is required.")

    def test_invalid_email(self):
        response = self.client.post(reverse("users:register"),
                                    data={
                                        "username": "shuhrat",
                                        "first_name": "ilhom",
                                        "last_name": "wukhrat",
                                        "email": "invalid-email",
                                        "password": "1234"
                                    })
        user_count = CustomUser.objects.count()
        self.assertEquals(user_count, 0)
        self.assertFormError(response, "form", "email", "Enter a valid email address.")

    def test_unique_username(self):
        user = CustomUser.objects.create(username="shuhrat", first_name="ilhom")
        user.set_password("somepass")
        user.save()
        response = self.client.post(reverse("users:register"),
                                    data={
                                        "username": "shuhrat",
                                        "first_name": "ilhom",
                                        "last_name": "wukhrat",
                                        "email": "ilhomjonv@gmail.com",
                                        "password": "somepass"
                                    })
        user_count = CustomUser.objects.count()
        self.assertEqual(user_count, 1)
        self.assertFormError(response, "form", "username", "A user with that username already exists.")


class LoginTestCase(TestCase):
    def setUp(self) -> None:  # darsda none yoq edi
        self.db_user = CustomUser.objects.create(username="shuhrat", first_name="ilhom")
        self.db_user.set_password("somepass")
        self.db_user.save()

    def test_successful_login(self):
        self.client.post(
            reverse("users:login"),
            data={
                "username": "shuhrat",
                "password": "somepass"
            }
        )
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_wrong_credentials(self):
        self.client.post(
            reverse("users:login"),
            data={
                "username": "wrong username",
                "password": "somepass"
            }
        )
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        self.client.post(
            reverse("users:login"),
            data={
                "username": "shuhrat",
                "password": "wrong pass"
            }
        )
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_logout(self):
        self.client.login(username="shuhrat", password="somepass")
        self.client.get(reverse("users:logout"))

        user = get_user(self.client)

        self.assertFalse(user.is_authenticated)


class ProfileTestCase(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:login") + "?next=/users/profile/")

    def test_profile_details(self):
        user = CustomUser.objects.create(
            username="wukhrat",
            first_name="shuhrat",
            last_name="ilhom",
            email="shuhrat@gmail.com"
        )
        user.set_password("somepass")
        user.save()

        self.client.login(username="wukhrat", password="somepass")

        response = self.client.get(reverse("users:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.username)
        self.assertContains(response, user.first_name)
        self.assertContains(response, user.last_name)
        self.assertContains(response, user.email)

    def test_update_profile(self):
        user = CustomUser.objects.create(
            username="wukhrat",
            first_name="shuhrat",
            last_name="ilhom",
            email="shuhrat@gmail.com"
        )
        user.set_password("somepass")
        user.save()

        self.client.login(username="wukhrat", password="somepass")
        response = self.client.post(
            reverse("users:profile-edit"),
            data={
                "username": "wukhrat",
                "first_name": "shuhrat",
                "last_name": "salah",
                "email": "shuhrat1@gmail.com"
            }
        )

        # user = CustomUser.objects.get(pk=user.pk)        # bu ikkalasi teng pasdagi bilan
        user.refresh_from_db()

        self.assertEqual(user.last_name, "salah")
        self.assertEqual(user.email, "shuhrat1@gmail.com")
        self.assertEqual(response.url, reverse("users:profile"))

