"""URL configuration for the Users app."""

from rest_framework.routers import DefaultRouter

from users.views import ManageUserView

router = DefaultRouter()
router.register(r"users", ManageUserView, basename="users")

urlpatterns = router.urls
