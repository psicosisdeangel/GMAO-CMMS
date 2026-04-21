"""Tests for UsersRepository — runs against the test DB."""

import pytest

from apps.users.repositories.users_repository import UsersRepository


@pytest.mark.django_db
class TestUsersRepository:
    def test_create_and_get_by_username(self):
        user = UsersRepository.create(
            username="repo_user",
            password="pass123",
            email="repo@test.com",
            nombre_completo="Repo User",
            rol="TECNICO",
        )
        found = UsersRepository.get_by_username("repo_user")
        assert found is not None
        assert found.id == user.id

    def test_get_by_id_missing(self):
        assert UsersRepository.get_by_id(99999) is None

    def test_exists_by_username(self):
        UsersRepository.create(
            username="exists_user",
            password="pass123",
            email="",
            nombre_completo="Exists",
            rol="SUPERVISOR",
        )
        assert UsersRepository.exists_by_username("exists_user") is True
        assert UsersRepository.exists_by_username("ghost") is False

    def test_update(self):
        user = UsersRepository.create(
            username="upd_user",
            password="pass123",
            email="old@test.com",
            nombre_completo="Old Name",
            rol="TECNICO",
        )
        updated = UsersRepository.update(user, {"email": "new@test.com"})
        assert updated.email == "new@test.com"
