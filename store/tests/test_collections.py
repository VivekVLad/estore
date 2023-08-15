from rest_framework import status
import pytest

@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self,api_client):
        # AAA (Arrange,Act,Assert)
        #Arrange

        #Act
        response = api_client.post('/collections/',{'title':'a'})

        #Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_40(self,api_client):
        api_client.force_authenticate(user={})
        
        response = api_client.post('/collections/',{'title':'a'})
        
        assert response.status_code == status.HTTP_403_FORBIDDEN