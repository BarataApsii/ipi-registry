from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.db.models import Sum

from shareholders.models import Shareholder, Director, Transaction

@login_required
def dashboard(request):
    total_shareholders = Shareholder.objects.count()
    total_directors = Director.objects.count()
    total_shares = Transaction.objects.aggregate(total=Sum('shares'))['total'] or 0

    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_shareholders = Shareholder.objects.filter(created_at__gte=thirty_days_ago).count()

    recent_transactions = Transaction.objects.select_related('shareholder').order_by('-created_at')[:5]

    upcoming_events = [
        {'title': 'Board Meeting', 'date': datetime.now(), 'time': '10:00 AM'},
        {'title': 'Shareholder Call', 'date': datetime.now(), 'time': '2:00 PM'},
    ]

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    new_counts = [5, 8, 6, 10, 12, 7, 9, 11, 4, 6, 8, 7]

    common_shares = 65
    preferred_shares = 25
    other_shares = 10

    context = {
        'total_shareholders': total_shareholders,
        'total_directors': total_directors,
        'total_shares': total_shares,
        'new_shareholders': new_shareholders,
        'recent_transactions': recent_transactions,
        'upcoming_events': upcoming_events,
        'months': months,
        'new_counts': new_counts,
        'common_shares': common_shares,
        'preferred_shares': preferred_shares,
        'other_shares': other_shares,
    }

    return render(request, 'dashboard/dashboard.html', context)

@login_required
def share_register(request):
    return render(request, 'dashboard/share_register.html')

@login_required
def shareholders_page(request):
    shareholders = Shareholder.objects.all()
    return render(request, 'dashboard/shareholders.html', {'shareholders': shareholders})

@login_required
def transaction_history(request):
    transactions = Transaction.objects.select_related('shareholder').all()
    return render(request, 'dashboard/transaction_history.html', {'transactions': transactions})

@login_required
def directors_page(request):
    directors = Director.objects.all()
    return render(request, 'dashboard/directors.html', {'directors': directors})

@login_required
def settings_page(request):
    return render(request, 'dashboard/settings.html')

@login_required
def help_page(request):
    return render(request, 'dashboard/help.html')
