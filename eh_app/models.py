# TODO: Python naming convention
# TODO: Field validation
# TODO: Verify cascade settings

# FIXME: how do requirements relate through activities attended?

# NOTE: Student status => Business logic (Should not be in db)

from django.db import models

# Create your models here.

class Semester(models.Model):
    # id autogenerated
    semester = models.CharField(max_length=16)
    academic_year = models.CharField(max_length=9)

    # Relations
    # Semester.Students autogenerated TODO: Check that this is actually generated and usable

# TODO: Ask Pauline
class Requirement(models.Model):
    # id autogen
    code = models.CharField(max_length=15)
    description = models.TextField(max_length=255)

class Activity(models.Model):
    # id autogenerated
    date = models.DateField()
    location = models.CharField(max_length=45)
    details = models.TextField(max_length=255)

    # Relations
    # Activity.departments autogenerated
    semester = models.ForeignKey(Semester, on_delete=None)
    requirement_satisfied = models.ForeignKey(Requirement, on_delete=None)

class TrackRequirements(models.Model):
    # id autogen
    per_sem = models.CharField(max_length=3, default=None)
    per_year = models.CharField(max_length=3, default=None)
    overall = models.CharField(max_length=3, default=None)
    description = models.TextField(max_length=255, default=None)

class Track(models.Model):
    id = models.CharField(primary_key=True, max_length=15)
    name = models.CharField(max_length=45)

    # Relations
    semester_started = models.ForeignKey(Semester, on_delete=None)
    requirements = models.ForeignKey(TrackRequirements, on_delete=None)

class Advisor(models.Model):
    uin = models.PositiveIntegerField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    middle_name = models.CharField(max_length=45)

    # Relations
    track = models.ForeignKey(Track, on_delete=None)

class Department(models.Model):
    name = models.CharField(primary_key=True, max_length=7)
    activities_per_semester = models.PositiveIntegerField()
    advising_per_semester = models.FloatField()

    # Relations
    # Department.Students autogenerated
    activities = models.ManyToManyField(Activity)
    advisors = models.ManyToManyField(Advisor)
    track = models.ForeignKey(Track, on_delete=None)
    # FIXME: Is the following necessary
    required_activities = models.ManyToManyField(
        Activity,
        related_name='required_activities',
        default=None,
    )

    def activities_per_year(self):
        return self.activities_per_semester * 2

    def advising_per_year(self):
        return self.advising_per_semester * 2

class Research(models.Model):
    class Meta:
        unique_together = (('requirement_satisfied', 'department'),)

    # id autogen
    program = models.CharField(max_length=10, default=None)
    details = models.TextField(max_length=255, default=None)

    # Relations
    requirement_satisfied = models.ForeignKey(Requirement, default=None, on_delete=None)
    advisor = models.ForeignKey(Advisor, default=None, on_delete=None)
    department = models.ForeignKey(Department, on_delete=None)

class Student(models.Model):
    uin = models.PositiveIntegerField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    middle_name = models.CharField(max_length=45)
    email = models.EmailField(max_length=45)
    gpa = models.FloatField()
    times_on_probation = models.PositiveIntegerField(default=0)
    times_dismissed = models.PositiveIntegerField(default=0)
    majors = models.CharField(max_length=45)

    # Relations
    departments = models.ForeignKey(Department, on_delete=None)
    start_semester = models.ForeignKey(Semester, on_delete=None)
    graduation_semester = models.ForeignKey(
        Semester,
        related_name='graduation_semester',
        on_delete=None,
    )
    activities_attended = models.ManyToManyField(Activity)

    graduated = models.BooleanField(default=False) # FIXME: Make function based on graduationsemester

class Exception(models.Model):
    class Meta:
        unique_together = (('semester', 'student'),)

    type_of_leave = models.CharField(max_length=45, unique=True)
    leave_duration = models.CharField(max_length=10, default=None)

    # Relations
    semester = models.ForeignKey(Semester, on_delete=None)
    student = models.OneToOneField(
        Student,
        on_delete=None,
        primary_key=True,
    )

class Teacher(models.Model):
    uin = models.PositiveIntegerField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    middle_name = models.CharField(max_length=45)

class Campus(models.Model):
    # id autogen
    name = models.CharField(max_length=45, unique=True)

class Course(models.Model):
    class Meta:
        unique_together = (('number', 'title'),)

    number = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=45, default=None)
    credits = models.PositiveIntegerField(default=None)
    min_credits = models.PositiveIntegerField(default=None)
    max_credits = models.PositiveIntegerField(default=None)
    # NOTE: Do we need min and max credits?

    # Relations
    department = models.ForeignKey(Department, on_delete=None)

class Section(models.Model):
    class Meta:
        unique_together = (('crn', 'semester'),)

    LEVEL_CHOICES = (
        ('L', 'Lower'),
        ('U', 'Upper'),
    )

    crn = models.PositiveIntegerField(primary_key=True)
    number = models.PositiveIntegerField()
    level = models.CharField(
        max_length=1,
        default=None,
        choices=LEVEL_CHOICES,
    )

    # Relations
    course = models.ForeignKey(Course, default=None, on_delete=None)
    teacher = models.ForeignKey(Teacher, default=None, on_delete=None)
    semester = models.ForeignKey(Semester, on_delete=None)
    campus = models.ForeignKey(Campus, default=None, on_delete=None)

# Essentially a history element
class StudentSectionEnrollment(models.Model):
    # id autogen
    grade = models.CharField(max_length=2, default=None)
    grading_mode = models.CharField(max_length=10, default=None)
    repeat = models.CharField(max_length=10, default=None)

    # Relations
    section = models.ForeignKey(
        Section,
        on_delete=None,
    )
    student = models.ForeignKey(Student, on_delete=None)
    semester = models.ForeignKey(Semester, on_delete=None)

    def credits(self):
        return self.section.course.credits;

# Essentially a history element
class StudentAdvisorMeeting(models.Model):
    # id autogen
    date = models.DateField(default=None)
    details = models.TextField(max_length=255, default=None)

    # Relations
    student = models.ForeignKey(
        Student,
        on_delete=None,
    )
    advisor = models.ForeignKey(Advisor, default=None, on_delete=None)
    requirement_satisfied = models.ForeignKey(Requirement, on_delete=None)
    semester = models.ForeignKey(Semester, on_delete=None)

# Essentially a history element
class StudentTrackEnrollment(models.Model):
    # id autogen

    # Relations
    student = models.ForeignKey(
        Student,
        on_delete=None,
    )
    track = models.ForeignKey(Track, on_delete=None)
    semester_enrolled = models.ForeignKey(
        Semester,
        default=None,
        on_delete=None
    )
    campus = models.ForeignKey(Campus, default=None, on_delete=None)
