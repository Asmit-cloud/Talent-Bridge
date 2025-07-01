"""
Defines the data models for the SkillSwap_Network application.

The models (Python classes) represent the structure of the data stored in the application's database.

For example:

    class ModelOne(models.Model):
        name = models.CharField(max_length=100)
        description = models.TextField()

        def __str__(self):
            return self.name
     
Each class typically corresponds to a database table.
"name" - this is the attribute of the model. In the corresponding daatbase table, this will become the name of a column.
"models.CharField" - this specifies the type of data the column will hold.
"max_length=100" - this argument for 'CharField' defines the maximum length allowed for strings in this 'name' column in the database.

"def __str__(self):" - when the built-in 'str()' function is called on an instace of the 'ModelOne', the method is executed.
"return self.name" - 'self.name' refers to the value of the 'name' attribute (which corresponds to the 'name' column in the database) of the specific 'Modelone'
instance.
That means when asking for a string representation of a 'ModelOne' object, this line will return the value stored in its 'name' field.

For example while creating in a new entry in the "ModelOne" using Django shell:

    from SkillSwap_Network import ModelOne

    my_first_object = ModelOne(name="Product A", description="This is the first product.")
    my_second_object = ModelOne(name="Product A", description="This is the second product.")

    print(my_first_object)
    print(my_second_object)

In this scenario:
   - "my_first_object" is an object, a specific instance of the "Modelone" class. It has its own particular values for 'name' and 'description'.
   - "my_second_object" this is another distinct object, also an instance of the 'ModelOne' class, but with different values for its attributes.

Now, when the Python interpreter will encounter "print(my_first_object)", it will need to figure out how to represent "my_first_object" as a string. And thats when
the "__str__" method of the 'ModelOne' class will be called on that specific object.

Because the "__str__" method is defined to "return self.name" the output would be:
Product A
Product B

By examining the classes in this file, you can understand the structure and  relationships of the data managed by the SkillSwap_Network application.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# --------------------
# CUSTOM USER MODELS
# --------------------


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for the CustomUser model.
    Provides methods for creating regular users and superusers.

    The "CustomUserManager" is the 'manager' specifically designed to work with and manage instances of the "CustomUser" model.
    The "CustomUserManager" provides the methods for creating, retrieving, and performing other database-level operations on "CustomUser" objects.
    """

    def create_user(self, username, password, **extra_fields):
        """
        Creates and saves a 'User' with the given username and password.

        Args:
            username (str): The username for the new user.
            password (str): The password for the new user.
            **extra_fields: Additional fields to be set on the 'User' model.

        Returns:
            CustomUser: The newly created 'user' object.

        Raises:
            ValueError: If the username and password are not provided.
        """

        if not username and not password:
            raise ValueError("Kindly provide a Username and Password!")
        elif not username:
            raise ValueError("Please provide a Username!")
        elif not password:
            raise ValueError("Please provide a Password!")
        
        # Create a new user instance with the given username
        user = self.model (username=username, **extra_fields)
        # Securely set the password
        user.set_password(password)
        # Save the user object to the database
        user.save(using=self._db)
        
        # Return the neewly created user
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Creates and saves a 'SuperUser' with the given username and password.

        Args:
            username (str): The username for the new SuperUser.
            password (str): The password for the new SuperUser.
            **extra_fields: Additional fields to be set on the 'User' model.

        Returns:
            CustomUser: The newly created 'superuser' object.

        Raises:
            ValueError: If the 'is_staff' and 'is_superuser' are not provided.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("A SuperUser must have 'is_staff' set to 'True'!")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("A SuperUser must have 'is_superuser' set to 'True'!")
        if extra_fields.get("is_active") is not True:
            raise ValueError("A SuperUser must have 'is_active' set to 'True'!")

        # Call the "create_user" method with the provided username, password, and extra fields to create and return the new superuser
        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    This is the custom user model (CustomUser) inheriting from AbstractBaseUser.
    Defines the core user attributes like username, activity status, staff/superuser status, and join date.

    Defines the structure and behaviour of the custom user model (CustomUser) in the database.
    "class CustomUser(AbstractBaseUser)" - It specifies the fields the user will have (beyond the basic ones provided by "AbstractBaseUser").
                                         - It represents the user entity itself in the application's data layer.

    The CustomUser model works in conjunction with the CustomUserManager.
    If CustomUserManager is like a factory manager - it knows how to build (create_user, create_superuser) the product, then CustomUser is the blueprint for the
    product (the user object) - it defines what the product looks like, what parts it has (the fields), and how it generally works.
    In essence:
        The "UserManager" knows how to create users.
        The AbstractBaseUser (and the CustomUser inhereting from it) defines what a user is.
    You need both because you need a definition of what a user is (the model) and a mechanism to create and manage instances of that user (the manager).
    The CustomUserManager is then typically linked to the CustomUser model by setting the objects attribute in CustomUser ("objects = CustomUserManager()").
    """

    username = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True) # Useful for deactivating accounts instead of deleting them
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    # "auto_now_add=True" - ensures that recording of the date and time only happens when the object is first created
    date_joined = models.DateTimeField(auto_now_add=True)

    # Tell Django which field in the "CustomerUser" model should be treated as the unique indentifier for login
    USERNAME_FIELD = "username"

    # A list of field names that are required to create a superuser using the 'createsuperuser' management command
    # As of now it is empty, which means it will prompt only for username and password
    REQUIRED_FIELDS = []

    # Tell Django to use "CustomUserManager" for managing instances of the "CustomerUser" model
    # Without this, Django would not know how to create users using the custom logic
    objects = CustomUserManager()

    def __str__(self):
        """
        Returns the string representation of the "CustomUser".
        """
        
        return self.username


# ------------------------
# APP REQUIREMENT MODEL
# ------------------------


class AppRequirements(models.Model):
    """
    Represents additional profile information for a CustomUser.

    Attributes:
        user (OneToOneField): A one-to-one link to the CustomUser instance this profile information belongs to.
        bio (TextField): An optional text field for a short biography or description of the user. Can be blank.
        location (CharField): A character field to store the user's geographical location.
    """

    # 'related_name="...."' allows to access the "AppRequirements" object from a "CustomUser" instance using "user.app_requirements"
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="app_requirements")
    
    bio = models.TextField(blank=True, default="")
    location = models.CharField(max_length=200)

    # Printing an instance of AppRequirements will return a descriptive string indicating which user's app requirements it is
    def __str__(self):
        return f"App requirements for {self.user.username}"


# -------------------
# USER SKILL MODELS
# -------------------


class Skill(models.Model):
    """
    Represents a skill that users can offer or need within the SkillSwap Network.
    
    Attributes:
        name (str): The unique name of the skill (e.g., "Graphic Design", "3D Modelling").
        description (str): An optional detailed description of the skill.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ProficiencyLevel(models.Model):
    """
    Defines different levels of proficiency for skills (e.g., "Beginner", "Intermediate", "Expert").
    
    These levels help categorize a user's ability in a particular skill.

    Arguments:
        name (str): The unique name of the proficienccy level.
        description (str): An optional detailed description of what this proficiency level entails.
        proficiency_level_order (int): An integer indicating the display order of proficiency levels, ensuring logical sorting.
    """

    name = models.CharField(max_length=70, unique=True)
    description = models.TextField(blank=True)
    proficiency_level_order = models.IntegerField(unique=True)

    class Meta:
        """
        Meta options for the ProficiencyLevel model.
        """

        # The following line tells Django that:
        # Whenever you query "ProficiencyLevel.objects.all()", it should by default return the results ordered by the "proficiency_level_order" field
        # This ensures that the levels are always presented logically
        ordering = ["proficiency_level_order"]

    def __str__(self):
        return self.name


class UserOfferedSkill(models.Model):
    """
    Links a CustomUser to a Skill they are offering, along with their proficiency level in that skill.

    This model captures the skills a user possesses and is willing to share and teach.

    Attributes:
        user (ForeignKey): A link to the CustomUser offering the skill.
        skill (ForeignKey): A link to the Skill being offered.
        proficiency_level (ForeignKey): A link to the ProficiencyLevel of the offered skill.
        description (str): Specific notes about how the user offers this skill.
        created_at (datetime): Timestamp when the skill offering was added.
        updated_at (datetime): Timestamp when the skill offering was last updated.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="offered_skills")
    skill = models.ForeignKey("Skill", on_delete=models.CASCADE)
    proficiency_level = models.ForeignKey("ProficiencyLevel", on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "skill")

    def __str__(self):
        return f"{self.user.username} offers {self.skill.name} ({self.proficiency_level.name})"


class UserNeededSkill(models.Model):
    """
    Links a CustomUser to a Skill they need or want to learn, optionally specifying a desired proficiency level in that skill.

    This model captures the skills a user is looking to acquire.

    Attributes:
        user (ForeignKey): A link to the CustomUser needing the skill.
        skill (ForeignKey): A link to the Skill being needed.
        proficiency_level (ForeignKey): A link to the ProficiencyLevel of the needed skill.
        description (str): Specific notes about why the user needs this skill.
        created_at (datetime): Timestamp when the skill in need was added.
        updated_at (datetime): Timestamp when the skill in need was last updated.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="needed_skills")
    skill = models.ForeignKey("Skill", on_delete=models.CASCADE)
    # "on_delete=models.SET_NULL" - (hereinafter mentioned)
    #   This is useful when you want to retain the "UserNeededSkill" record even if the associated "ProficiencyLevel" is removed
    #   But you no longer want a specific proficiency level linked
    proficiency_level = models.ForeignKey("ProficiencyLevel", on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "skill")

    def __str__(self):
        level_str = f"({self.proficiency_level.name})" if self.proficiency_level else ""
        return f"{self.user.username} needs {self.skill.name}{level_str}"
