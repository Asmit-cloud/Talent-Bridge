"""
This module defines Django forms used within the SkillSwap_Network application.

Django form handles the task of creating HTML forms, validating user input, and processing that input into Python data structures(Defines how user input is collected
and validated).

Interaction with Templates:
    - Views often create instances of forms defined here and pass them to templates.
    - The templates then render these form objects into HTML forms that users interact with.
Data Handling in Views:
    - When users submit forms, views recieve this data and typically create a form instance with it.
    - The view then uses the form to validate the submitted data.

Intrgration with Models:
    - Django's "ModelForm" provides a way to automatically create forms based on the application's models.
    simplifying the process of creating forms for creating or updating database objects.

In essence:
Forms defined in this module act as a bridge between the user interface (templates), the application logic (views), and the data structure (models), ensuring clean
and validated data is handled within the Django application.
"""

from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from SkillSwap_Network.models import CustomUser, AppRequirements, Skill, ProficiencyLevel, UserOfferedSkill, UserNeededSkill


class CustomSignUpForm(forms.Form):
    """
    A custom form for user registration (Sign up).
    """
    
    username = forms.CharField(max_length=200, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean(self):
        """
        Performs form-wide cleaning and validation, specifically for the password fields.
        This method overrides the default "clean()" method to compare the "password" and "confirm_password" fields.
        
        This method is called by the form's "is_valid" method. It allows to perform validation that depends on multiple fields.

        Returns:
            dict: The cleaned data.

        Raises:
            ValidationError: If "password" and "confirm_password" fields do not match
        """

        # The following line calls the "clean()" method of the parent class "forms.Form"
        # The "cleaned_data" dictionary contains the valid form data submitted by the user
        # The "clean()" is a hook that you can override in a Django form to perform custom validation that spans multiple fields.
        cleaned_data = super().clean()
        # The following lines retrieve the values of the "password" and "confirm_password" fields
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check if both the password fields have values, and if they are not equal
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("The passwords do not match!")

        # Return the cleaned data
        return cleaned_data


    def save(self):
        """
        Creates a new user based on the validated data in the signup form.

        This method retrives the cleaned username and password from the form and uses them to create a new user account.

        Returns:
            CustomUser: The newly created user object.
        """
        
        # Retrieve the validated username and password from the form's "cleaned_data"
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        # Create a new user
        # Use the "create_user" method of "CustomUserManager" (accessed via "CustomUser.objects")
        # To create a new "CustomUser" instance with the provided username and password
        # And then return the newly created user object
        return CustomUser.objects.create_user(username, password)


class UserProfileCompletionForm(forms.ModelForm):
    """
    Form for users to complete their profile information.
    This form is linked to the "CustomUser" model, allowing for easy creation and modification of user profile data stored in the database.

    The form automatically handles validation based on "CustomUser" model's field definitions.

    Attributes:
        Meta (class): Inner class that provides metadata for the form, linking it to the "CustomUser" model and defining which fields to include and their widgets.
    """

    class Meta:
        model = AppRequirements
        fields = ("bio", "location")
        
        widgets = { # A dictionary used to customise the HTML widgets used for specific form fields
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": ""}),
            "location": forms.TextInput(attrs={"placeholder": "e.g., Hollywood, United States"}),
        }


class UserOfferedSkillForm(forms.ModelForm):
    """
    Form for users to add or edit skills they offer.

    This form is linked to the "UserOfferedSkill" model and allows users to specify a skill, their proficiency level in it, and an optoinal description.

    Attributes:
        Meta (class): Inner class that provides metadata for the form linking it to the "UserOfferedSkill" model and defining which fields to include and their widget.
    """

    class Meta:
        model = UserOfferedSkill
        fields = ["skill", "proficiency_level", "description"]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 2, "placeholder": "Optional: Add notes about the skill (e.g., specific technologies, projects)"}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes the "UserOfferedSkillForm" form.

        This overridden constructor customizes the querysets for the "skill" and "proficiency_level" fields to ensure they are ordered alphabetically and by their
        defined order, respectively.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        super().__init__(*args, **kwargs)
        # Order the skills alphabetically
        self.fields["skill"].queryset = Skill.objects.all().order_by("name")
        # Customize the empty label
        self.fields["skill"].empty_label = "--- Select a Skill ---"
        
        # Order proficiency levels as their defined order
        self.fields["proficiency_level"].queryset = ProficiencyLevel.objects.all().order_by("proficiency_level_order")
        # Customize the empty label
        self.fields["proficiency_level"].empty_label = "--- Select a Proficiency Level ---"


class UserNeededSkillForm(forms.ModelForm):
    class Meta:
        model = UserNeededSkill
        fields = ["skill", "proficiency_level", "description"]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 2, "placeholder": "Optional: Why do you need this skill? (e.g.,for a specific project)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order the skills alphabetically
        self.fields["skill"].queryset = Skill.objects.all().order_by("name")
        # Customize the empty label
        self.fields["skill"].empty_label = "--- Select a Skill ---"
        
        # Order proficiency levels as their defined order
        self.fields["proficiency_level"].queryset = ProficiencyLevel.objects.all().order_by("proficiency_level_order")
        # Customize the empty label
        self.fields["proficiency_level"].empty_label = "--- Desired Proficiency Level (Optional) ---"


# Create the formsets
UserOfferedSkillFormSet = inlineformset_factory(
    CustomUser,
    UserOfferedSkill,
    form=UserOfferedSkillForm,
    extra=1,
    can_delete=True,
)
UserNeededSkillFormSet = inlineformset_factory(
    CustomUser,
    UserNeededSkill,
    form=UserNeededSkillForm,
    extra=1,
    can_delete=True,
)
