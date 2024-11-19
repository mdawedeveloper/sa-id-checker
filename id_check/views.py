import requests
from django.shortcuts import render, redirect
from .models import IDInfo, PublicHoliday,SearchLog
from django.db.models import Count
from .forms import IDForm
from datetime import datetime
from django.utils.timezone import now

# Calendarific API key
API_KEY = "4w7vO81O0VeLpvMqijl3e1lpU4sGuIGb"

def home(request):
    form = IDForm()
    result = None
    chart_data = []

    if request.method == "POST":
        form = IDForm(request.POST)
        if form.is_valid():
            id_number = request.POST.get("id_number", "").strip()
            # Extracting Date of Birth, Gender, and Citizenship
            date_of_birth = datetime.strptime(id_number[:6], "%y%m%d").date()
            gender = "Female" if int(id_number[6:10]) < 5000 else "Male"
            is_sa_citizen = id_number[10] == "0"

            # Save or Updating ID Info
            id_info, created = IDInfo.objects.get_or_create(
                id_number=id_number,
                defaults={
                    'date_of_birth': date_of_birth,
                    'gender': gender,
                    'is_sa_citizen': is_sa_citizen,
                }
            )
            if not created:
                # Increment the search count if this ID number already exists
                id_info.search_count += 1
                id_info.save()

            # Log the search event
            SearchLog.objects.create(id_info=id_info)

            # Fetch Public Holidays from Calendarific API
            url = f"https://calendarific.com/api/v2/holidays?api_key={API_KEY}&country=ZA&year={date_of_birth.year}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                holidays = response.json().get('response', {}).get('holidays', [])
                
                for holiday in holidays:
                    from dateutil.parser import parse

                    holiday_date = parse(holiday['date']['iso']).date()

                    if holiday_date == date_of_birth:
                        # Creating a PublicHoliday record if the date matches
                        PublicHoliday.objects.get_or_create(
                            id_info=id_info,
                            name=holiday['name'],
                            description=holiday.get('description', ''),
                            date=holiday_date,
                            type=holiday['type'][0],
                        )
            except requests.exceptions.RequestException as e:
                # Handling API request errors (e.g., network issues, invalid API key)
                print(f"Error fetching holidays: {e}")
                form.add_error(None, "Could not fetch public holidays at the moment.")
                return render(request, "id_check/home.html", {"form": form, "result": None})

            # Retrieving Results
            result = {
                "id_info": id_info,
                "holidays": id_info.holidays.all(), 
            }

            # Preparing chart data
            search_logs = (
                SearchLog.objects.filter(id_info=id_info)
                .values("search_date")
                .annotate(count=Count("id"))
                .order_by("search_date")
            )
            chart_data = [
                {"date": entry["search_date"].strftime("%Y-%m-%d"), "count": entry["count"]}
                for entry in search_logs
            ]

    return render(request, "id_check/home.html", {"form": form, "result": result, "chart_data": chart_data})


