from django.urls import path
from support.views import (
    PublicContactAPIView,
    TicketAPIView,
    TicketDetailAPIView,
    TicketReplyAPIView,
    TicketStatusAPIView
)

app_name = 'support'

urlpatterns = [
    path('api/support/contact/', PublicContactAPIView.as_view(), name='contact_api'),
    path('api/support/tickets/', TicketAPIView.as_view(), name='tickets_api'),
    path('api/support/tickets/<str:ticket_number>/', TicketDetailAPIView.as_view(), name='ticket_detail_api'),
    path('api/support/tickets/<str:ticket_number>/reply/', TicketReplyAPIView.as_view(), name='ticket_reply_api'),
    path('api/support/tickets/<str:ticket_number>/status/', TicketStatusAPIView.as_view(), name='ticket_status_api'),
]
