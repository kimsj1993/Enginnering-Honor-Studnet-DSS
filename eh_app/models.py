# TODO: Field validation
# TODO: Verify cascade settings
# TODO: All relation fields cannot be null

# FIXME: refactor of all activity based items

from django.db import models
from .querysets import GPAStatusQueryset, SemesterQueryset

class _BaseTimestampModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class Activity(_BaseTimestampModel):
    # id autogenerated
    date = models.DateField(default=None, null=True)
    location = models.CharField(max_length=45, default=None, null=True)
    details = models.TextField(max_length=255, default=None, null=True)

    # Relations
    semester = models.ForeignKey('Semester', on_delete=None)
    requirement_satisfied = models.ForeignKey('Requirement', on_delete=None)

class Advisor(_BaseTimestampModel):
    uin = models.PositiveIntegerField(primary_key=True)
    first_name = models.CharField(max_length=45, default=None, null=True)
    last_name = models.CharField(max_length=45, default=None, null=True)
    middle_name = models.CharField(max_length=45, default=None, null=True)

    # Relations
    track = models.ForeignKey('Track', default=None, null=True, on_delete=None)

class Campus(_BaseTimestampModel):
    name = models.CharField(primary_key=True, max_length=45)

class College(_BaseTimestampModel):
    name = models.CharField(primary_key=True, max_length=2)

class Course(_BaseTimestampModel):
    class Meta:
        unique_together = (('number', 'title', 'department'),)

    # id autogen pk
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=45, default=None, null=True)
    credits = models.PositiveIntegerField()
    min_credits = models.PositiveIntegerField(default=None, null=True)
    max_credits = models.PositiveIntegerField(default=None, null=True)

    # Relations
    department = models.ForeignKey('Department', on_delete=None)

class Degree(_BaseTimestampModel):
    class Meta:
        unique_together = (('department', 'concentration'),)

    name = models.CharField(max_length=4, primary_key=True)
    concentration = models.CharField(max_length=16, default=None, null=True)

    # Relations
    department = models.ForeignKey('Department', on_delete=None)

class Department(_BaseTimestampModel):
    name = models.CharField(primary_key=True, max_length=7)
    activities_per_semester = models.DecimalField(max_digits=2, decimal_places=1)
    advising_per_semester = models.DecimalField(max_digits=2, decimal_places=1)

    # Relations
    activities = models.ManyToManyField('Activity', default=None)
    advisors = models.ManyToManyField('Advisor', default=None)
    track = models.ForeignKey('Track', default=None, null=True, on_delete=None)
    required_activities = models.ManyToManyField(
        'Activity',
        related_name='required_activities_set',
        default=None,
    )
    college = models.ForeignKey('College', on_delete=None)

    def activities_per_year(self): # pragma: no cover
        return self.activities_per_semester * 2

    def advising_per_year(self): # pragma: no cover
        return self.advising_per_semester * 2

class Exception(_BaseTimestampModel):
    type_of_leave = models.CharField(max_length=45, default=None, null=True, unique=True)
    leave_duration = models.CharField(max_length=10, default=None, null=True)

    # Relations
    semester = models.ForeignKey('Semester', on_delete=None)
    student = models.OneToOneField(
        'Student',
        on_delete=None,
        primary_key=True,
    )

class GPADeficiency(_BaseTimestampModel):
    value = models.CharField(primary_key=True, max_length=45)
    code = models.CharField(max_length=2)

class GPAStatus(_BaseTimestampModel):
    class Meta:
        unique_together = (('code', 'gpa'),)

    # id autogen
    code = models.CharField(max_length=2)
    gpa = models.DecimalField(max_digits=3, decimal_places=2)
    status = models.CharField(max_length=45)

    objects = GPAStatusQueryset.as_manager()

# TODO: Code as reqID, partial classes for inheriting object
class Requirement(_BaseTimestampModel):
    # id autogen
    code = models.CharField(max_length=15)
    description = models.TextField(max_length=255, default=None, null=True)

class Research(_BaseTimestampModel):
    # id autogen
    program = models.CharField(max_length=10, default=None, null=True)
    details = models.TextField(max_length=255, default=None, null=True)

    # Relations
    requirement_satisfied = models.ForeignKey('Requirement', default=None, null=True, on_delete=None)
    advisor = models.ForeignKey('Advisor', default=None, null=True, on_delete=None)
    department = models.ForeignKey('Department', on_delete=None)

class Section(_BaseTimestampModel):
    class Meta:
        unique_together = (('crn', 'semester'),)

    LEVEL_CHOICES = (
        ('L', 'Lower'),
        ('U', 'Upper'),
    )

    crn = models.PositiveIntegerField(primary_key=True)
    number = models.PositiveIntegerField(default=None, null=True)
    level = models.CharField(
        max_length=1,
        choices=LEVEL_CHOICES,
    )

    # Relations
    course = models.ForeignKey('Course', on_delete=None)
    teacher = models.ForeignKey('Teacher', default=None, null=True, on_delete=None)
    semester = models.ForeignKey('Semester', on_delete=None)
    campus = models.ForeignKey('Campus', default=None, null=True, on_delete=None)

class Semester(_BaseTimestampModel):
    id = models.PositiveIntegerField(primary_key=True)
    semester = models.CharField(max_length=16, default=None, null=True)
    academic_year = models.CharField(max_length=9, default=None, null=True)
    current = models.BooleanField(default=False)

    # Relations
    successor = models.OneToOneField(
        'self',
        related_name='predecessor',
        default=None,
        null=True,
        on_delete=None
    )

    objects = SemesterQueryset.as_manager()

    def current_semester(self):
        return self.successor == None and self.predecessor != None

    def past_semester(self):
        return self.successor != None

    # TODO: Creating a new current semester should trigger calculation of status elements for the newly elapsed semester

class Student(_BaseTimestampModel):
    uin = models.PositiveIntegerField(primary_key=True)

    first_name = models.CharField(max_length=45, default=None, null=True)
    last_name = models.CharField(max_length=45, default=None, null=True)
    middle_name = models.CharField(max_length=45, default=None, null=True)
    email = models.EmailField(max_length=45, default=None, null=True)

    times_on_probation = models.PositiveIntegerField(default=0)
    times_dismissed = models.PositiveIntegerField(default=0)

    degree_candidate = models.BooleanField(default=False)
    # TODO: Should also be set true on turn of semester
    graduated = models.BooleanField(default=False)

    # Relations
    majors = models.ManyToManyField('Degree', related_name='majors_set', default=None)
    minors = models.ManyToManyField('Degree', related_name='minors_set', default=None)
    start_semester = models.ForeignKey('Semester', default=None, null=True, on_delete=None)
    graduation_semester = models.ForeignKey(
        'Semester',
        related_name='graduating_set',
        default=None,
        null=True,
        on_delete=None,
    )
    activities_attended = models.ManyToManyField('Activity', default=None)

    # Taken from all previous semesters
    # From student semester status set.last
    def cumulative_gpa(self):
        previous_status = self.semester_statuses_set.last()
        return float(previous_status.overall_gpa)

    def first_year_grace(self):
        current_sem = Semester.objects.get_current()

        temp = self.start_semester
        for i in range(3):
            if temp.id == current_sem.id:
                return True
            elif temp.successor:
                temp = temp.successor
            else:
                raise IndexError('Student has not started or semester chain has not been preserved')

        return False

    def status_gpa_alone(self):
        last_status = self.semester_statuses_set.last()

        if not last_status:
            return 'n/a'

        deficiency_value_prefix = 'Y-' if self.first_year_grace() else 'N-'

        deficiency = GPADeficiency.objects.get(
            value=deficiency_value_prefix + last_status.previous_status
        )

        return GPAStatus.objects.get_status(
            deficiency.code,
            float(last_status.overall_gpa),
        ).status

# Essentially a history element
class StudentAdvisorMeeting(_BaseTimestampModel):
    # id autogen
    date = models.DateField(default=None, null=True)
    details = models.TextField(max_length=255, default=None, null=True)

    # Relations
    student = models.ForeignKey('Student', on_delete=None)
    advisor = models.ForeignKey('Advisor', default=None, null=True, on_delete=None)
    requirement_satisfied = models.ForeignKey('Requirement', on_delete=None)
    semester = models.ForeignKey('Semester', on_delete=None)

# Essentially a history element
class StudentResearch(_BaseTimestampModel):
    # id autogen
    course_credit = models.PositiveIntegerField(default=None, null=True)
    paper_published = models.CharField(max_length=2, default=None, null=True)
    conference_attended = models.CharField(max_length=2, default=None, null=True)
    presentation = models.CharField(max_length=2, default=None, null=True)
    details = models.TextField(max_length=255, default=None, null=True)

    # Relations
    student = models.ForeignKey('Student', on_delete=None)
    research = models.ForeignKey('Research', on_delete=None)
    semester = models.ForeignKey(
        'Semester',
        default=None,
        null=True,
        on_delete=None,
    )
    # requirement can be reached through research.requirement

# Essentially a history element
class StudentSectionEnrollment(_BaseTimestampModel):
    # id autogen
    grade = models.CharField(max_length=2, default=None, null=True)
    grading_mode = models.CharField(max_length=10, default=None, null=True) # s/u
    repeat = models.CharField(max_length=10, default=None, null=True)

    # Relations
    section = models.ForeignKey('Section', on_delete=None)
    student = models.ForeignKey('Student', on_delete=None)

    def semester(self):
        return self.section.semester

    def credits(self):
        return self.section.course.credits

# Finalized for each student on the turn of a semester
# History element to track eh status by semester
# All null fields and overalls will be finalized when the semester is changed
class StudentSemesterStatus(_BaseTimestampModel):
    class Meta:
        unique_together = (('semester', 'predecessor'),)

    # id autogen
    # Performance of this semester alone
    hours_attempted = models.PositiveIntegerField()
    hours_earned = models.PositiveIntegerField(default=0)
    hours_passed = models.PositiveIntegerField(default=0)
    quality_points = models.PositiveIntegerField(default=0)
    semester_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    # Based off of previous semesters, doesn't include fields above unless finalized == true
    # TODO: Signal on finalized to do computation
    # Initially just a pull from the previous semester status
    finalized = models.BooleanField(default=False)
    overall_hours_attempted = models.PositiveIntegerField(default=0)
    overall_hours_earned = models.PositiveIntegerField(default=0)
    overall_hours_passed = models.PositiveIntegerField(default=0)
    overall_quality_points = models.PositiveIntegerField(default=0)
    overall_gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    status = models.CharField(max_length=20, default='n/a') # Requires filling in at end of semester
    previous_status = models.CharField(max_length=20, default='Good Standing')

    # Relations
    student = models.ForeignKey(
        'Student',
        related_name='semester_statuses_set',
        on_delete=None,
    )
    semester = models.ForeignKey('Semester', on_delete=None)
    predecessor = models.OneToOneField(
        'self',
        related_name='successor',
        default=None,
        null=True,
        on_delete=None
    )

# Essentially a history element
class StudentTrackEnrollment(_BaseTimestampModel):
    # id autogen

    # Relations
    student = models.ForeignKey('Student', on_delete=None)
    track = models.ForeignKey('Track', on_delete=None)
    semester = models.ForeignKey('Semester', on_delete=None)
    campus = models.ForeignKey('Campus', default=None, null=True, on_delete=None)

class Teacher(_BaseTimestampModel):
    uin = models.PositiveIntegerField(primary_key=True)
    first_name = models.CharField(max_length=45, default=None, null=True)
    last_name = models.CharField(max_length=45, default=None, null=True)
    middle_name = models.CharField(max_length=45, default=None, null=True)

class Track(_BaseTimestampModel):
    id = models.CharField(primary_key=True, max_length=15)
    name = models.CharField(max_length=45)

    # Relations
    semester_started = models.ForeignKey('Semester', default=None, null=True, on_delete=None)
    requirements = models.ForeignKey('TrackRequirements', default=None, null=True, on_delete=None)

class TrackRequirements(_BaseTimestampModel):
    # id autogen
    per_sem = models.DecimalField(max_digits=2, decimal_places=1)
    description = models.TextField(max_length=255, default=None, null=True)

    def per_year(self): # pragma: no cover
        return self.per_sem * 2

    def overall(self): # pragma: no cover
        return self.per_year() * 2
