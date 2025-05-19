import unittest

from ..entity import EntityCQImpl

from .user import User, Login, Password, WrongPasswordError
from .login import LoginDoesNotMeetRequirementsError
from .password import PasswordDoesNotMeetRequirementsError

from .implementation.commands.register_user import RegisterUserCommand
from .implementation.queries.is_registered import IsUserRegisteredQuery

from ...usecase.service.user import crypt_context

class RegisterUserCommandImpl(RegisterUserCommand):
    def __init__(self, all_users):
        self.all_users = all_users

    def __call__(self, login, hashed_password):
        self.all_users[login] = hashed_password

class IsUserRegisteredQueryImpl(IsUserRegisteredQuery):
    def __init__(self, all_users):
        self.all_users = all_users

    def __call__(self, login):
        return login in self.all_users

def get_test_impl(all_users):
    impl = EntityCQImpl({
        RegisterUserCommand: RegisterUserCommandImpl(all_users),
        IsUserRegisteredQuery: IsUserRegisteredQueryImpl(all_users)
    })
    return impl

class TestCase(unittest.TestCase):
    all_users = dict()

    def test_login_correct(self):
        Login("abcd123ABCD___")

    def test_login_wrong1(self):
        def sub():
            Login("@&!(@EDdDdd112d)")
        self.assertRaises(LoginDoesNotMeetRequirementsError, sub)

    def test_login_wrong2(self):
        def sub():
            Login("ab")
        self.assertRaises(LoginDoesNotMeetRequirementsError, sub)

    def test_login_wrong3(self):
        def sub():
            Login("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.assertRaises(LoginDoesNotMeetRequirementsError, sub)

    def test_password_correct(self):
        Password("128DxaDwwW__")

    def test_password_wrong1(self):
        def sub():
            Password("2*@@9137@")
        self.assertRaises(PasswordDoesNotMeetRequirementsError, sub)

    def test_password_wrong2(self):
        def sub():
            Password("bc")
        self.assertRaises(PasswordDoesNotMeetRequirementsError, sub)

    def test_password_wrong3(self):
        def sub():
            Password("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        self.assertRaises(PasswordDoesNotMeetRequirementsError, sub)

    def test_create(self):
        impl = get_test_impl(self.__class__.all_users)
        user = User.create(None, impl, Login("ABCD"), Password("112233"), crypt_context)
        self.assertNotEqual(user, None)

    def test_verify_password_correct(self):
        impl = get_test_impl(self.__class__.all_users)

        password = "ddOD_dwdu9d2"

        user = User.create(None, impl, Login("DwdDWd2"), Password(password), crypt_context)
        user.log_in(password)

    def test_verify_password_wrong(self):
        impl = get_test_impl(self.__class__.all_users)

        user = User.create(None, impl, Login("DwdDWd2"), Password("ddOD_dwdu9d2"), crypt_context)

        def sub():
            nonlocal user
            user.log_in("ddadqwdqdw")

        self.assertRaises(WrongPasswordError, sub)