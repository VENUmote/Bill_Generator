from django.urls import path
from . import views
from .views import edit_items
from .views import edit_invoice
from .views import download_invoice_pdf

urlpatterns = [
    path('', views.invoice_form, name='invoice_form'),
    path('invoice_list/', views.invoice_list, name='invoice_list'),
    path('invoice_detail/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('edit-items/<int:invoice_id>/', edit_items, name='edit_items'),
    path('invoice/edit/<int:invoice_id>/', edit_invoice, name='edit_invoice'),
    path('fetch-suppliers/', views.fetch_supplier_details, name='fetch_suppliers'),
    path('fetch-buyers/', views.fetch_buyer_details, name='fetch_buyers'),
    path('download-invoice/<int:invoice_id>/', download_invoice_pdf, name='download_invoice_pdf'),
    path('invoices/', views.invoice_list, name='invoice_list'),
]
