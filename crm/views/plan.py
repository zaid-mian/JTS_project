# crm/views/plan.py
from django.shortcuts import render, redirect

# 1. Plan Selection View
# Triggered when user selects a specific plan.
# Initiates checkout or subscription setup, then redirects to signup/login.
#
# def select_plan_view(request, plan_id):
#     # Store the selected plan ID in the session for redirection after signup/login
#     # request.session['selected_plan_id'] = plan_id
#     # return redirect('crm:signup_or_login')
#     pass
