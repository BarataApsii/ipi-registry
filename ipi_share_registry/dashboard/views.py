from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils import timezone

from shareholders.models import Shareholder, Director, Transaction

# -------------------------
# PERMISSION HELPERS
# -------------------------
def is_admin(user):
    """Only superusers or users in 'Admin' group"""
    return user.is_superuser or user.groups.filter(name='Admin').exists()

# -------------------------
# USER MANAGEMENT (ADMIN)
# -------------------------
@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all().order_by('username')
    groups = Group.objects.all()
    return render(request, 'dashboard/user_list.html', {'users': users, 'groups': groups})

@login_required
@user_passes_test(is_admin)
def user_add(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        group_name = request.POST.get("group")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("dashboard:user_add")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("dashboard:user_add")

        user = User.objects.create_user(username=username, password=password, is_staff=True)
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                messages.warning(request, "Selected group does not exist.")

        messages.success(request, "User created successfully.")
        return redirect("dashboard:user_list")

    groups = Group.objects.all()
    return render(request, "dashboard/user_add.html", {"groups": groups})

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    user = User.objects.get(id=user_id)
    groups = Group.objects.all()
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        group_name = request.POST.get("group")

        if username:
            user.username = username
        if password:
            user.set_password(password)

        user.groups.clear()
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                messages.warning(request, "Selected group does not exist.")

        user.save()
        messages.success(request, "User updated successfully.")
        return redirect("dashboard:user_list")

    return render(request, "dashboard/user_edit.html", {"user": user, "groups": groups})

# -------------------------
# DASHBOARD
# -------------------------
@login_required
def dashboard(request):
    # Totals
    total_shareholders = Shareholder.objects.count()
    total_directors = Director.objects.count()
    total_shares = Transaction.objects.aggregate(total=Sum('shares'))['total'] or 0

    # New shareholders (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_shareholders = Shareholder.objects.filter(created_at__gte=thirty_days_ago).count()

    # Recent transactions - only select the fields we need
    recent_transactions = Transaction.objects.select_related('shareholder').only(
        'id', 'created_at', 'transaction_type', 'shares', 'status', 'shareholder__full_name'
    ).order_by('-created_at')[:5]

    # Upcoming events demo
    upcoming_events = [
        {'title': 'Board Meeting', 'date': timezone.now(), 'time': '10:00 AM'},
        {'title': 'Shareholder Briefing', 'date': timezone.now(), 'time': '2:00 PM'},
    ]

    # Chart demo data
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    new_counts = [5,8,6,10,12,7,9,11,4,6,8,7]

    # Share distribution demo (can replace with DB queries later)
    share_distribution = {'common': 65, 'preferred': 25, 'other': 10}

    context = {
        'total_shareholders': total_shareholders,
        'total_directors': total_directors,
        'total_shares': total_shares,
        'new_shareholders': new_shareholders,
        'recent_transactions': recent_transactions,
        'upcoming_events': upcoming_events,
        'months': months,
        'new_counts': new_counts,
        'share_distribution': share_distribution,
    }
    return render(request, 'dashboard/dashboard.html', context)

# -------------------------
# SIDEBAR PAGES
# -------------------------
@login_required
def share_register(request):
    return render(request, 'dashboard/share_register.html')

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

def generate_shareholder_id():
    """Generate a unique shareholder ID in the format SH-YYYYMMDD-XXXXXX"""
    from datetime import datetime
    import random
    import string
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"SH-{date_str}-{random_str}"

@login_required
def shareholders_page(request):
    if request.method == 'POST':
        try:
            # Get form data
            full_name = request.POST.get('full_name')
            id_number = request.POST.get('id_number')
            use_custom_id = request.POST.get('use_custom_id') == 'on'
            
            # Generate ID if not using custom ID or if custom ID is empty
            if not use_custom_id or not id_number:
                id_number = generate_shareholder_id()
                # Ensure the generated ID is unique
                while Shareholder.objects.filter(id_number=id_number).exists():
                    id_number = generate_shareholder_id()

            # Get other fields
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            date_of_birth = request.POST.get('date_of_birth')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            city = request.POST.get('city')
            country = request.POST.get('country')
            postal_code = request.POST.get('postal_code')
            share_certificate_number = request.POST.get('share_certificate_number')
            notes = request.POST.get('notes')

            # Create new shareholder
            shareholder = Shareholder.objects.create(
                full_name=full_name,
                id_number=id_number,
                email=email,
                phone_number=phone_number,
                date_of_birth=date_of_birth if date_of_birth else None,
                gender=gender,
                address=address,
                city=city,
                country=country,
                postal_code=postal_code,
                share_certificate_number=share_certificate_number,
                notes=notes,
                created_by=request.user,
                date_joined=timezone.now().date(),
                is_active=True
            )
            
            # Handle file upload
            if 'photo' in request.FILES:
                shareholder.photo = request.FILES['photo']
                shareholder.save()
            
            messages.success(request, f'Shareholder added successfully! ID: {id_number}')
            return redirect('dashboard:shareholders')
            
        except Exception as e:
            messages.error(request, f'Error adding shareholder: {str(e)}')
    
    # GET request - show the list of shareholders
    shareholders = Shareholder.objects.all().order_by('full_name')
    return render(request, 'dashboard/shareholders.html', {
        'shareholders': shareholders,
        'auto_generated_id': generate_shareholder_id()
    })
    return render(request, 'dashboard/shareholders.html', {'shareholders': shareholders})

@login_required
def transaction_history(request):
    transactions = Transaction.objects.select_related('shareholder').order_by('-created_at')
    return render(request, 'dashboard/transaction_history.html', {'transactions': transactions})

@login_required
def directors_page(request):
    directors = Director.objects.all().order_by('full_name')
    return render(request, 'dashboard/directors.html', {'directors': directors})

@login_required
def settings_page(request):
    return render(request, 'dashboard/settings.html')

@login_required
def help_page(request):
    return render(request, 'dashboard/help.html')
