from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import Userpreference


def search_expenses(request):
    if request.method == 'POST':
        search_str=json.loads(request.body).get('searchText')
        
        expenses=Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user) 
            
        data = expenses.values()
        
        return JsonResponse(list(data), safe=False)    
            
# Create your views here.
@login_required(login_url="/authentication/login")
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator=Paginator(expenses, 2)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    currency=Userpreference.objects.get_or_create(user=request.user).currency

    context = {
        "expenses": expenses,
        "page_obj": page_obj,
        # "currency": currency,
    }
    return render(request, "expenses/index.html", context)


@login_required(login_url="/authentication/login")
def add_expense(request):
    categories = Category.objects.all()
    context = {"categories": categories, "values": request.POST}
    if request.method == "GET":
        return render(request, "expenses/add_expense.html", context)

    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "expenses/add_expense.html", context)

        description = request.POST["description"]
        date = request.POST["expense_date"]
        category = request.POST["category"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, "expenses/add_expense.html", context)

        Expense.objects.create(
            owner=request.user,
            amount=amount,
            category=category,
            date=date,
            description=description,
        )

        messages.success(request, "Expenses saved successfully")

        return redirect("expenses")

@login_required(login_url="/authentication/login")
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        "expense": expense,
        "values": expense,
        'categories':categories
    }

    if request.method == "GET":
        return render(request, "expenses/edit_expense.html", context)

    if request.method == "POST":
        amount = request.POST["amount"]

        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "expenses/edit_expense.html", context)

        description = request.POST["description"]
        date = request.POST["expense_date"]
        category = request.POST["category"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, "expenses/edit_expense.html", context)

        expense.owner=request.user
        expense.amount=amount
        expense.category=category
        expense.date=date
        expense.description=description
        
        expense.save()

        messages.success(request, "Expenses updated successfully")

    return redirect("expenses")

@login_required(login_url="/authentication/login")
def expense_delete(request, id):
    expense=Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense removed")
    return redirect("expenses")

