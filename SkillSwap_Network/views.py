"""
Responsible for defining the view functions or classes that handle the SkillSwap_Network application's logic for processing incoming web requests and returning responses.

The "views.py" acts as a "controller" layer. They recieve HTTP requests (e.g., from a user's browser), interact with the application's model (models.py) to retrieve
or manipulate data, and then render a response, often using templates.

Each function or class within this file typically corrersponds to a specific URL endpoint of the application. The mapping between URLs and views is defined in a
seperate "urls.py" file.

By examining the individual functions and classes within this file, you can undesrtand how the SkillSwap_Network application handles different user interactions and data
flows.
"""

import json
import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction, models
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from SkillSwap_Chat.models import ChatRoom, Participant, Message
from SkillSwap_Network.forms import (
    CustomSignUpForm,
    UserProfileCompletionForm,
    UserOfferedSkillForm,
    UserNeededSkillForm,
    UserOfferedSkillFormSet,
    UserNeededSkillFormSet,

)
from SkillSwap_Network.models import (
    CustomUser,
    AppRequirements,
    Skill,
    ProficiencyLevel,
    UserOfferedSkill,
    UserNeededSkill,
)


def splash_view(request):
    """
    The main landing page.
    """
    return render(request, "accounts/splash_page.html")


def login_view(request):
    """
    Handles user login.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Either a redirect to the homepage after successful login (POST) or the rendered login form (GET).
    """
    
    # When a user submits a login form, the request method is "POST"
    if request.method == "POST":
        # Create an instance of Django's built-in login form, populating it with the data the user submitted
        # The "request" method is for security reasons within the form
        form = AuthenticationForm(request, data=request.POST)

        # Check if the user's input in the form meets the form's requirements (e.g., required fields are filled)
        if form.is_valid():
            # "form.cleaned_data" is a dictionary containing the validated user input.
            # Retrieve the username
            username = form.cleaned_data.get("username")
            # Retrieve the password
            password = form.cleaned_data.get("password")
            # Try to find a user in the database (using the "AUTH_USER_MODEL" setting, which points to "CustomUser") that matches the provided username and password
            # If successful it return the user object, otherwise returns "None"
            user = authenticate(request, username=username, password=password)

            # Check if the user is authenticated ("authenticate()" returns a user object - meaning the credentials are correct)
            if user is not None:
                # Establish a session for that user, effectively loggin them in
                auth_login(request, user)
                # Display the user a success message on the next page
                messages.success(request, f"Logged in as {username}!")
                # Redirect the logged in user to web app's requirements page
                # Redirect with a query parameter indicating origin from auth
                return redirect(reverse("home") + "?from_auth=true")

            # Handle authentication failure
            else:
                messages.error(request, "Please provide a valid Username or Password!")

        # Handle invalid forms
        else:
            if form.errors and "__all__" not in form.errors:
                messages.error(request, "There were errors in your form, please check the fields below.")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
            else:
                messages.error(request, "Invalid Username or Password!")

    # Handle the GET request
    # When the request method is "GET" (i.e., when a user first visits a login page), create an empty "AuthenticationForm"
    else:
        form = AuthenticationForm()

    # "render()" - A Django shortcut
    # Its purpose is to take a template, combine it with some data (the context), and return an "HttpResponse" object with the rendered content
    # "request" - The first argument is the "HttpRequest" object that the view function received.
    # Django needs to this know about the currect request
    # {"form": form} - It is a Python dictionary, which is used to pass the data from the view to the template
    #  The value "form" is the instance of the "AuthenticationForm" which is created in the view (either an empty form or a form containing the submitted data)
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """
    Handles the user logout.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: A rendered logout form.
    """
    
    # Take the "HttpRequest" object as an argument
    # And then end the current user session, effectively logging the user out of the website
    auth_logout(request)
    # Display a meesage on the next page
    messages.info(request, "Logged Out Successfully!")
    # "return redirect(....)" - It returns a "HttpResponseRedirect" object, which tells the user's browser to navigate to a different URL
    return render(request, "accounts/logout.html")


def signup_view(request):
    """
    Handles user registration or sign up.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Either a redirect to the homepage after successful registration (POST) or the rendered sign up form (GET).
    """
    
    if request.method == "POST":
        form = CustomSignUpForm(request.POST)

        if form.is_valid():
            # Call the "save" method from the form
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created successfully.\nYou are now logged in!")
            # Redirect to the web app's requirements page after a successful sign up
            # Redirect with a query parameter indicating origin from auth
            return redirect(reverse("profile_completion") + "?from_auth=true")

    # Handle the initial GET request
    else:
        form = CustomSignUpForm()

    # Render the "signup.html" template, passing the form object to it so it can be displayed
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def post_login_view(request):
    """
    Handles the post-login flow for users, allowing them to complete or edit their profile information.

    This view manages the creation or update of a user's AppRequirements instance, which includes their bio and location.
    It distinguishes between a user completing their profile for the first time after authentication and a user editing their existing profile.

    Args:
        request(HttpRequest): The incoming HTTP request object.

    Returns:
        HttpResponse:
            - A redirect to the "add_skills" page if the profile is successfully updated and the user is coming from an authentication flow (signup/login).
            - A redirect to the "user_profile" page if the profile is successfully updated and the user is editing an existing profile.
            - A rendered "accounts/profile_completion.html" template with the UserProfileCompletionForm (either pre-poluated with the existing data or empty).
    """

    # Custom user instance
    user = request.user

    # Check if an "AppRequirements" object already exists for the current user
    existing_app_requirements = AppRequirements.objects.filter(user=user).first()
    # Set a boolean flag indicating if a profile already exists in the database
    is_existing_profile_in_db = existing_app_requirements is not None

    # Check for a query parameter "from_auth=true"
    # This parameter is added during the login or signup redirects, to differentiate between a new user completing their profile and an existing user editing it
    from_auth_flow = request.GET.get("from_auth") == "true"

    # This flag helps in deciding what message or context to show in the template
    # If a profile exists and the user is not coming from an authentication flow, it mena sthey are editing their profile
    is_editing_profile_for_template = is_existing_profile_in_db and not from_auth_flow

    # Get or create the AppRequirements instance for the current user (This is important because AppRequirements has a OneToOne relationship with CustomUser)
    app_requirements, created = AppRequirements.objects.get_or_create(user=user)

    if request.method == "POST":
        # Create a form instance from the POST data and bind it to the app_requirements instance
        form = UserProfileCompletionForm(request.POST,instance=existing_app_requirements)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            # Save the updated bio and location to the user
            profile.save()
            messages.success(request, "Your profile has been updated!")

            if is_editing_profile_for_template:
                # Set a session variable to indicate profile was just edited
                request.session["profile_edited_from_completion"] = True
                return redirect(reverse("user_profile"))
            else:
                return redirect("add_skills")
    else:
        # Pre-populate the form with existing user data
        form = UserProfileCompletionForm(instance=existing_app_requirements)

    context = {
        "form": form,
        "is_existing_profile": is_editing_profile_for_template,
    }

    return render(request, "accounts/profile_completion.html", context)


@login_required
def add_skills_view(request):
    """
    Handles the addition and editing of user's offered and needed skill.

    This view allows authenticated users to specify which skills they can offer and which skills they need.
    It uses Django formsets to manage multiple skill entries for both offered and needed skills.

    Args:
        request(HttpRequest): The incoming HTTP request object.

    Returns:
        HttpResponse:
            - A redirect to the "home" page if skills are successfully updated.
            - A rendered "accounts/add_skills.html" template with the UserOfferedSkillFormSet and UserNeededSkillFormSet (either pre-poluated with the existing data
              or empty for new entries).
    """
    
    # Get the current user instance
    user = request.user
    
    if request.method == "POST":
        # Pass the user instance to the parent formsets
        offered_skill_formset = UserOfferedSkillFormSet(request.POST, instance=user, prefix="offered_skills")
        needed_skill_formset = UserNeededSkillFormSet(request.POST, instance=user, prefix="needed_skills")

        # Check if both formsets are valid
        if offered_skill_formset.is_valid() and needed_skill_formset.is_valid():
            
            with transaction.atomic():
                # Save the offered skills
                offered_skill_formset.save()
                # Save the needed skills
                needed_skill_formset.save()

                messages.success(request, "Your skills have been updated successfully!")
                # Redirect the user to a different page
                return redirect("home")

        # Handle if formsets are not valid
        else:
            for form in offered_skill_formset:
                if form.errors:
                    messages.error(request, f"Offered skill error: {form.errors.as_text()}")
            for form in needed_skill_formset:
                if form.errors:
                    messages.error(request, f"Needed skill error: {form.errors.as_text()}")
        context = {
            "offered_skill_formset": offered_skill_formset,
            "needed_skill_formset": needed_skill_formset,
        }

        return render(request, "accounts/add_skills.html", context)
        
    # Handle the GET request
    else:
        # Pass the instance to populate with existing data
        offered_skill_formset = UserOfferedSkillFormSet(instance=user, prefix="offered_skills")
        needed_skill_formset = UserNeededSkillFormSet(instance=user, prefix="needed_skills")

    context = {
        "offered_skill_formset": offered_skill_formset,
        "needed_skill_formset": needed_skill_formset,
    }

    return render(request, "accounts/add_skills.html", context)


def get_skills_api(request):
    """
    Retrieves a list of available skills from the database and returns them as JSON.

    This API endpoint is designed to provide skill data, typically for front-end components like dropdowns.
    It fetches all Skill objects, orders them by name, and formats them into a list of dictionaries with "value" (skill ID) and "label" (skill name) keys.

    Args:
        request(HttpRequest): The incoming HTTP request object.

    Returns:
        JSONResponse: A JSON response containing a list of skill dictioanries or an error  message if an issue occurs.
    """

    json_file_path = os.path.join(os.path.dirname(__file__), "data", "skills.json")

    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            skills_data = json.load(f)

        skills_data = Skill.objects.all().order_by("name")
        formatted_skills = []
        for skill in skills_data:
            formatted_skills.append({
                "value": skill.id,
                "label": skill.name
            })

        return JsonResponse(formatted_skills, safe=False)

    except FileNotFoundError:
        return JsonResponse({"error": "skills data file not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format in 'skills.json'"}, status=500)
    except Exception as e:
        return JsonResponse({"error": "An unexpected error occurred while fetching skills: {str(e)}"}, status=500)


def get_proficiency_levels_api(request):
    """
    Retrieves a list of available proficiency_levels from the database and returns them as JSON.

    This API endpoint is designed to provide proficiency level data, typically for front-end components like dropdowns.
    It fetches all ProficiencyLevel objects, orders them by a defined order ("proficiency_level_order"), and formats them into a list of dictionaries with "value"
    (level ID) and "label" (level name) keys.

    Args:
        request(HttpRequest): The incoming HTTP request object.

    Returns:
        JSONResponse: A JSON response containing a list of proficiency level dictioanries or an error  message if an issue occurs.
    """

    json_file_path = os.path.join(os.path.dirname(__file__), "data", "proficiency_levels.json")

    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            proficiency_data = json.load(f)

        proficiency_data = ProficiencyLevel.objects.all().order_by("proficiency_level_order")
        formatted_levels = []
        for level in proficiency_data:
            formatted_levels.append({
                "value": level.id,
                "label": level.name
            })

        return JsonResponse(formatted_levels, safe=False)

    except FileNotFoundError:
        return JsonResponse({"error": "Proficiency levels data file not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format in 'proficiency_levels.json'"}, status=500)
    except Exception as e:
        return JsonResponse({"error": "An unexpected error occurred while fetching proficiency levels: {str(e)}"}, status=500)


@login_required
def homepage_view(request):
    """
    Renders the main homepage for the authenticated users.

    This view serves as the primary landing page after a user successfully logs in.
    It also ensures that any previously stored session data related to "last_skill_list_context" is cleared upon loading the homepage, providing a fresh Browse
    experience.

    Args:
        request(HttpRequest): The incoming HTTP request object.

    Returns:
        HttpResponse: Renders the "homepage/home.html" template, passing the current user object to the template context.
    """

    # Check if the data associated with the key "last_skill_list_context" exists in the user's session
    if "last_skill_list_context" in request.session:
        # Delete the "last_skill_list_context" if found
        del request.session["last_skill_list_context"]
        
    return render(request, "homepage/home.html", {"user": request.user})


@login_required
def browse_skills_view(request):
    """
    Renders a page for browsing through the available skills, categorized by wheather they are offered or needed.
    
    This view fetches all skills from the database and presents them to the user.
    It allows the users to switch betweeen viewing skills that are "offered" by a user and skills that are "needed" by users, controlled by a "type" query parameter.

    Args:
        request(HttpRequest): The incoming HTTP request object, which may contain a "type" query parameter.

    Returns:
        HttpResponse: Renders the "homepage/browse_skills.html" template, passing the list of all skills and the current skill type (offered or needed) to the
                      template context.
    """

    # Fetch all "Skill" objects from the database
    all_skills = Skill.objects.all().order_by("name")

    # Check for a query parameter in the URL
    # If the "type" parameter is present, its value (offered or needed) is assigned to the skill type
    # If type parameter is NOT present in the URL, it defaults to "offered"
    skill_type = request.GET.get("type", "offered")

    # Pagination
    skills_per_page = 30
    paginator = Paginator(all_skills, skills_per_page)

    page_number = request.GET.get("page")
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results
        page_obj = paginator.page(paginator.num_pages)

    context = {
        "all_skills": page_obj,
        "current_skill_type": skill_type,
    }

    return render(request, "homepage/browse_skills.html", context)


@login_required
def skill_users_list_view(request, skill_id, skill_type):
    """
    Displays a list of users associated with a specific skill, categorized by wheather they offer or need that skill.

    This view retrieves a particular skill based on "skill_id" and then filters users who either offer or need this skill, based on "skill_type".
    It also stores the context of the current skill list on the session for potential redirection back to this list from a user's profile.

    Args:
        request(HttpRequest): The incoming HTTP request object.
        skill_id (int): The ID of the skill to filter users by.
        skill_type (str): The type of skill relationship to display users for ("offerd" or "needed").

    Returns:
        HttpResponse:
            - Renders the "homepage/skill_users_list.html" template, passing the skill, skill type, list of users with the skill, and a dynamic page title to the
              template context.
            - Redirects to "browse_skils" with an error message if an invalid skill type is specified.
    """

    # Retrieve the specific skill
    skill = get_object_or_404(Skill, id=skill_id)
    
    # Initialize the variables
    # An empty list to the users ("UserOfferedSkill" or "UserNeededSkill" objects) that match the criteria
    users_with_skill = []
    # An empty string to store the dynamic title for the page
    current_page_title = ""

    # Filter users based on "skill_type"
    
    if skill_type == "offered":
        # Query the "UserOfferedSkill" model, filter for the records where the "skill" field matches the "skill" object retrieved earlier
        # Order the results by the username of the associated user
        users_with_skill = UserOfferedSkill.objects.filter(skill=skill).order_by("user__username")
        current_page_title = f"Users Offering {skill.name}"
        
    elif skill_type == "needed":
        users_with_skill = UserNeededSkill.objects.filter(skill=skill).order_by("user__username")
        current_page_title = f"Users Needing {skill.name}"
        
    else:
        messages.error(request, "Invalid skill type specified.")
        return redirect("browse_skills")

    # Store "last_skill_list_context" in session
    # The following line stores the "skill_id" and "skill_type" of the currently viewed list in the user's session
    request.session["last_skill_list_context"] = {
        "skill_id": skill_id,
        "skill_type": skill_type,
    }

    context = {
        "skill": skill,
        "skill_type": skill_type,
        "users_with_skill": users_with_skill,
        "current_page_title": current_page_title,
    }

    return render(request, "homepage/skill_users_list.html", context)


@login_required
def user_profile_view(request):
    """
    Displays the profile page of the currently logged in user.

    This view gathers and present a comprehensive information about the user, including their basic profile details (bio, location from AppRequirements), and lists all
    skills they offer and skills they need.
    It also checks for a "last_skill_list_context" in the sessoin to potentially offer a "return to list" link.

    Args:
        request(HttpRequest): The incoming HTTP request object.

    Returns:
        HttpResponse: Renders the "accounts/user_profile.html" template, passing the user object, AppRequirements, offered skills, needed skills, and an optional
                      "last_skill_list_context" to the template.
    """

    user = request.user

    # Create or retrieve the AppRequirements object associated with the current user
    app_requirements, created = AppRequirements.objects.get_or_create(user=user)

    # Query the "UserOfferedSkill" model to fetch all skills that the currect user has explicitly marked as offering
    offered_skills = UserOfferedSkill.objects.filter(user=user)
    # Query the "UserNeededSkill" model to fetch all skills that the currect user has explicitly marked as needing
    needed_skills = UserNeededSkill.objects.filter(user=user)

    # Check for the session variable set after profile completion page
    show_home_button = request.session.pop("profile_edited_from_completion", False)
    
    context = {
        "user": user,
        "app_requirements": app_requirements,
        "offered_skills": offered_skills,
        "needed_skills": needed_skills,
        "show_home_button": show_home_button,
    }

    # Handle the 'return to last skill list' logic
    # Retrieve the "last_skill_list_context" dictionary from the user session
    last_skill_list_context = request.session.get("last_skill_list_context")
    
    if last_skill_list_context:
        try:
            # Try to fetch the "Skill" object corresponding to the "skill_id" stored in the session context
            Skill.objects.get(id=last_skill_list_context["skill_id"])
            # If the "Skill" exists, "last_skill_list_context" is added to the "context" dictionary
            context["last_skill_list_info"] = last_skill_list_context
            
        except Skill.DoesNotExist:
            del request.session["last_skill_list_context"]

    return render(request, "accounts/user_profile.html", context)


@login_required
def public_user_profile_view(request, user_id):
    """
    Displays the public profile page for a specific user, different from the current user.

    This view retrieves a target user based on their ID and presents their publicly avaialable profile information, including their AppRequirements details and lists
    of skills they offer and need.
    It prevents a user from viewing their own public profile (redirecting to their private one) and also checks for a "last_skill_list_context" in the session for
    navigation purposes.

    Args:
        request(HttpRequest): The incoming HTTP request object.
        skill_id (int): The ID of the target user whoswe public profile is to be displayed.

    Returns:
        HttpResponse:
            - A redirect to the "user_profile" view if the 'user_id' matches the currently logged-in user.
            - Renders the "accounts/public_user_profile.html" template, passing the target user, AppRequirements, offered skills, needed skills, the current logged-in
              users, and optional "last_skill_list_context" to the template.
    """

    # Retrieve a CustomUser object from the database using the "user_id" passed in the URL
    target_user = get_object_or_404(CustomUser, id=user_id)

    if request.user == target_user:
        return redirect("user_profile")

    app_requirements, created = AppRequirements.objects.get_or_create(user=target_user)

    offered_skills = UserOfferedSkill.objects.filter(user=target_user).order_by("skill__name")
    needed_skills = UserNeededSkill.objects.filter(user=target_user).order_by("skill__name")

    context = {
        "target_user": target_user,
        "app_requirements": app_requirements,
        "offered_skills": offered_skills,
        "needed_skills": needed_skills,
        "current_logged_in_user": request.user,
    }

    last_skill_list_context = request.session.get("last_skill_list_context")
    if last_skill_list_context:
        try:
            Skill.objects.get(id=last_skill_list_context["skill_id"])
            context["last_skill_list_info"] = last_skill_list_context
        except Skill.DoesNotExist:
            del request.session["last_skill_list_context"]

    return render(request, "accounts/public_user_profile.html", context)


@login_required
def start_chat_with_user(request, target_user_id):
    """
    Handles initiating a chat between a current logged in user and a target user.
    It finds an existing 1-to-1 chat room or creates a new one, then redirects the user to the specific chat room's view.
    """

    current_user = request.user
    target_user = get_object_or_404(CustomUser, id=target_user_id)

    # Prevent a user from chatting with themselves
    if current_user == target_user:
        messages.warning(request, "You cannot chat with yourself.")
        return redirect("user_profile")
    
    # Try to find an existing chat rooms between these two users
    chat_room = ChatRoom.objects.annotate(
        num_participants = models.Count("participants")
    ).filter(
        num_participants=2,
        participants__user=current_user
    ).filter(
        participants__user=target_user
    ).first()

    if not chat_room:
        # If no chat room exists, create a new one
        chat_room = ChatRoom.objects.create()
        # Add both users as participants
        Participant.objects.create(user=current_user, chatroom=chat_room)
        Participant.objects.create(user=target_user, chatroom=chat_room)
        messages.success(request, f"New chat started with {target_user.username}!")
    else:
        messages.info(request, f"Resuming chat with {target_user.username}.")

    # Redirect to the chat room view
    return redirect("SkillSwap_Chat:chat_room_view", chat_room_id=chat_room.id)
