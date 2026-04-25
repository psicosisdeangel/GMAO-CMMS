"""Unit tests for UsersService."""

import pytest

from apps.users.exceptions import DuplicateUsernameError, UserNotFoundError
from apps.users.services.users_service import UsersService


@pytest.fixture
def supervisor(db):
    from apps.users.models import User

    return User.objects.create_user(
        username="svc_supervisor",
        password="pass",
        nombre_completo="Supervisor",
        rol="SUPERVISOR",
    )


@pytest.fixture
def valid_create_data():
    return {
        "username": "tecnico01",
        "password": "SecurePass123",
        "email": "tecnico01@plant.com",
        "nombre_completo": "Técnico Uno",
        "rol": "TECNICO",
    }


class TestUsersServiceCreate:
    @pytest.mark.django_db
    def test_create_user_success(self, valid_create_data, supervisor):
        user = UsersService.create_user(data=valid_create_data, actor=supervisor)
        assert user.username == "tecnico01"
        assert user.rol == "TECNICO"
        # Password must be hashed, not stored plain
        assert user.password != "SecurePass123"

    @pytest.mark.django_db
    def test_create_user_duplicate_username_raises(self, valid_create_data, supervisor):
        UsersService.create_user(data=valid_create_data, actor=supervisor)
        with pytest.raises(DuplicateUsernameError):
            UsersService.create_user(data=valid_create_data, actor=supervisor)


class TestUsersServiceGet:
    @pytest.mark.django_db
    def test_get_user_not_found_raises(self):
        with pytest.raises(UserNotFoundError):
            UsersService.get_user(user_id=99999)

    @pytest.mark.django_db
    def test_get_user_success(self, valid_create_data, supervisor):
        created = UsersService.create_user(data=valid_create_data, actor=supervisor)
        found = UsersService.get_user(user_id=created.id)
        assert found.id == created.id


class TestUsersServiceDeactivate:
    @pytest.mark.django_db
    def test_deactivate_user(self, valid_create_data, supervisor):
        user = UsersService.create_user(data=valid_create_data, actor=supervisor)
        deactivated = UsersService.deactivate_user(user_id=user.id, actor=supervisor)
        assert deactivated.is_active is False

    @pytest.mark.django_db
    def test_deactivate_nonexistent_raises(self, supervisor):
        with pytest.raises(UserNotFoundError):
            UsersService.deactivate_user(user_id=99999, actor=supervisor)


class TestUsersServiceUpdate:
    @pytest.mark.django_db
    def test_update_user_success(self, valid_create_data, supervisor):
        user = UsersService.create_user(data=valid_create_data, actor=supervisor)
        updated = UsersService.update_user(
            user_id=user.id,
            data={"nombre_completo": "Nombre Nuevo"},
            actor=supervisor,
        )
        assert updated.nombre_completo == "Nombre Nuevo"

    @pytest.mark.django_db
    def test_update_user_not_found_raises(self, supervisor):
        with pytest.raises(UserNotFoundError):
            UsersService.update_user(user_id=99999, data={"nombre_completo": "X"}, actor=supervisor)


class TestUsersServiceList:
    @pytest.mark.django_db
    def test_list_users_returns_all(self, valid_create_data, supervisor):
        UsersService.create_user(data=valid_create_data, actor=supervisor)
        users = list(UsersService.list_users())
        assert len(users) >= 1
