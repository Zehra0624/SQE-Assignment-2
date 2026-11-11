
import pytest

from registration import (
    Student,
    Course,
    check_credit_limit,
    prerequisites_satisfied,
    registration_decision,
    register_course,
    withdraw_course
)


# ============================================================
# A1. EQUIVALENCE CLASS PARTITIONING (ECP)
# ============================================================

# ECP-01: Valid current and course credits.

def test_ecp_valid_current_and_course_credits():
    assert check_credit_limit(10, 3) is True


# ECP-02 and ECP-03: Invalid current credits.

@pytest.mark.parametrize(
    "current",
    [-1, 19],
    ids=["ECP-02", "ECP-03"]
)
def test_ecp_invalid_current_credits(current):
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(current, 3)


# ECP-04: Valid course credits.

def test_ecp_valid_course_credits():
    assert check_credit_limit(5, 3) is True


# ECP-05 + BVA-07: Course credits = 0.

def test_ecp05_bva07_invalid_course_credits_zero():
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(5, 0)


# ECP-06 + BVA-11: Course credits = 5.

def test_ecp06_bva11_invalid_course_credits_five():
    with pytest.raises(ValueError, match="Invalid course credits"):
        check_credit_limit(5, 5)


# ECP-07 + BVA-24: No outstanding dues.

def test_ecp07_bva24_zero_dues():
    student = Student(student_id="S01", outstanding_dues=0)
    course = Course("CS201", 3, 30, 10)

    assert registration_decision(student, course) == "REGISTERED"


# ECP-08: Positive outstanding dues.

def test_ecp_positive_dues():
    student = Student(student_id="S01", outstanding_dues=500)
    course = Course("CS201", 3, 30, 10)

    assert registration_decision(student, course) == "DUES_BLOCK"


# ECP-09 + BVA-23: Negative outstanding dues.

def test_ecp09_bva23_negative_dues():
    student = Student(student_id="S01", outstanding_dues=-1)
    course = Course("CS201", 3, 30, 10)

    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(student, course)


# ECP-10: No prerequisites required.

def test_ecp_no_prerequisites():
    assert prerequisites_satisfied(set(), set()) is True


# ECP-11: All prerequisites completed.

def test_ecp_all_prerequisites_completed():
    completed = {"CS101", "MATH101"}
    required = {"CS101", "MATH101"}

    assert prerequisites_satisfied(completed, required) is True


# ECP-12: Only some prerequisites completed.

def test_ecp_some_prerequisites_completed():
    completed = {"CS101"}
    required = {"CS101", "MATH101"}

    assert prerequisites_satisfied(completed, required) is False


# ECP-13: No prerequisites completed.

def test_ecp_no_prerequisites_completed():
    completed = set()
    required = {"CS101", "MATH101"}

    assert prerequisites_satisfied(completed, required) is False


# ECP-14: Seats available.

def test_ecp_seats_available():
    student = Student(student_id="S01")
    course = Course("CS201", 3, 30, 20)

    assert registration_decision(student, course) == "REGISTERED"


# ECP-15 + BVA-18: Course is full.

def test_ecp15_bva18_course_full():
    student = Student(student_id="S01")
    course = Course("CS201", 3, 30, 30)

    assert registration_decision(student, course) == "WAITLISTED"


# ECP-16 + BVA-19: Enrollment exceeds capacity.

def test_ecp16_bva19_enrollment_exceeds_capacity():
    student = Student(student_id="S01")
    course = Course("CS201", 3, 30, 31)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


# ECP-17 + BVA-22: Zero capacity.

def test_ecp17_bva22_zero_capacity():
    student = Student(student_id="S01")
    course = Course("CS201", 3, 0, 0)

    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(student, course)


# ECP-18 + DT-02: Already registered.

def test_ecp18_dt02_already_registered():
    student = Student(
        student_id="S01",
        registered_courses={"CS201"}
    )
    course = Course("CS201", 3, 30, 10)

    assert registration_decision(student, course) == "ALREADY_REGISTERED"


# ECP-19: Not already registered.

def test_ecp_course_not_already_registered():
    student = Student(
        student_id="S01",
        registered_courses={"CS101"}
    )
    course = Course("CS102", 3, 30, 10)

    assert registration_decision(student, course) == "REGISTERED"


# ============================================================
# A2. BOUNDARY VALUE ANALYSIS (BVA)
# ============================================================

# BVA-01: Current credits below minimum.

def test_bva_current_credits_below_minimum():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(-1, 1)


# BVA-02 to BVA-05: Valid current credit boundaries.

@pytest.mark.parametrize(
    "current, expected",
    [
        (0, True),       # BVA-02
        (1, True),       # BVA-03
        (17, True),      # BVA-04
        (18, False)      # BVA-05: 18 + 1 exceeds the limit
    ],
    ids=["BVA-02", "BVA-03", "BVA-04", "BVA-05"]
)
def test_bva_valid_current_credit_boundaries(current, expected):
    assert check_credit_limit(current, 1) is expected


# BVA-06: Current credits above maximum.

def test_bva_current_credits_above_maximum():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(19, 1)


# BVA-08 to BVA-10: Valid course credit boundaries.

@pytest.mark.parametrize(
    "course_credits",
    [1, 2, 4],
    ids=["BVA-08", "BVA-09", "BVA-10"]
)
def test_bva_valid_course_credit_boundaries(course_credits):
    assert check_credit_limit(5, course_credits) is True


# BVA-12 to BVA-16: Combined credit limit boundaries.

@pytest.mark.parametrize(
    "current, new, expected",
    [
        (14, 4, True),     # BVA-12
        (15, 3, True),     # BVA-13
        (16, 3, False),    # BVA-14
        (17, 1, True),     # BVA-15
        (18, 1, False)     # BVA-16
    ],
    ids=["BVA-12", "BVA-13", "BVA-14", "BVA-15", "BVA-16"]
)
def test_bva_combined_credit_limit(current, new, expected):
    assert check_credit_limit(current, new) is expected


# BVA-17, BVA-20 and BVA-21: Other capacity boundaries.

@pytest.mark.parametrize(
    "capacity, enrolled, expected",
    [
        (30, 29, "REGISTERED"),    # BVA-17
        (1, 0, "REGISTERED"),      # BVA-20
        (1, 1, "WAITLISTED")       # BVA-21
    ],
    ids=["BVA-17", "BVA-20", "BVA-21"]
)
def test_bva_capacity_boundaries(capacity, enrolled, expected):
    student = Student(student_id="S01")
    course = Course("CS201", 3, capacity, enrolled)

    assert registration_decision(student, course) == expected


# BVA-25 + DT-01: Smallest positive dues.

def test_bva25_dt01_positive_dues():
    student = Student(student_id="S01", outstanding_dues=1)
    course = Course("CS201", 3, 30, 10)

    assert registration_decision(student, course) == "DUES_BLOCK"


# ============================================================
# A3. DECISION TABLE TESTING
# ============================================================

# DT-03: Prerequisites missing.

def test_dt_prerequisites_missing():
    student = Student(student_id="S01")
    course = Course(
        "CS201", 3, 30, 10,
        prerequisites={"CS101", "MATH101"}
    )

    assert registration_decision(student, course) == "PREREQUISITES_MISSING"


# DT-04: Credit limit exceeded.

def test_dt_credit_limit_exceeded():
    student = Student(student_id="S01", current_credits=16)
    course = Course("CS201", 3, 30, 10)

    assert registration_decision(student, course) == "CREDIT_LIMIT"


# DT-05: All conditions pass and seats are available.

def test_dt_registered():
    student = Student(student_id="S01", current_credits=10)
    course = Course("CS201", 3, 30, 10)

    assert registration_decision(student, course) == "REGISTERED"


# DT-06: All conditions pass but course is full.

def test_dt_waitlisted():
    student = Student(student_id="S01", current_credits=10)
    course = Course("CS201", 3, 30, 30)

    assert registration_decision(student, course) == "WAITLISTED"


# DT-07: Dues have priority over duplicate registration.

def test_dt_dues_priority_over_duplicate():
    student = Student(
        student_id="S01",
        outstanding_dues=1,
        registered_courses={"CS201"}
    )
    course = Course("CS201", 3, 30, 10)

    assert registration_decision(student, course) == "DUES_BLOCK"


# DT-08: Duplicate registration has priority over missing prerequisites.

def test_dt_duplicate_priority_over_prerequisites():
    student = Student(
        student_id="S01",
        registered_courses={"CS201"}
    )
    course = Course(
        "CS201", 3, 30, 10,
        prerequisites={"CS101"}
    )

    assert registration_decision(student, course) == "ALREADY_REGISTERED"


# DT-09: Missing prerequisites have priority over credit limit.

def test_dt_prerequisite_priority_over_credit_limit():
    student = Student(
        student_id="S01",
        current_credits=18
    )
    course = Course(
        "CS201", 3, 30, 10,
        prerequisites={"CS101"}
    )

    assert registration_decision(student, course) == "PREREQUISITES_MISSING"


# DT-10: Credit limit has priority over full course.

def test_dt_credit_limit_priority_over_full_course():
    student = Student(
        student_id="S01",
        current_credits=16
    )
    course = Course("CS201", 3, 30, 30)

    assert registration_decision(student, course) == "CREDIT_LIMIT"


# ============================================================
# A4. REGISTRATION STATE TESTING
# ============================================================

# ST-11: registration_decision must not change object state.

def test_registration_decision_does_not_change_state():
    student = Student(
        student_id="S01",
        current_credits=6
    )
    course = Course("CS201", 3, 30, 10)

    original_credits = student.current_credits
    original_registered = student.registered_courses.copy()
    original_enrolled = course.enrolled
    original_waitlist = course.waitlist.copy()

    registration_decision(student, course)

    assert student.current_credits == original_credits
    assert student.registered_courses == original_registered
    assert course.enrolled == original_enrolled
    assert course.waitlist == original_waitlist


# ST-12: Full-course registration_decision must not change object state.

def test_registration_decision_full_course_does_not_change_state():
    student = Student(
        student_id="S01",
        current_credits=6
    )
    course = Course("CS201", 3, 30, 30)

    original_credits = student.current_credits
    original_registered = student.registered_courses.copy()
    original_enrolled = course.enrolled
    original_waitlist = course.waitlist.copy()

    result = registration_decision(student, course)

    assert result == "WAITLISTED"
    assert student.current_credits == original_credits
    assert student.registered_courses == original_registered
    assert course.enrolled == original_enrolled
    assert course.waitlist == original_waitlist


# ST-01, ST-02 and ST-03: Successful registration changes state.

def test_successful_registration_changes_state():
    student = Student(student_id="S01")
    course = Course("CS201", 3, 30, 10)

    result = register_course(student, course)

    assert result == "REGISTERED"
    assert "CS201" in student.registered_courses
    assert student.current_credits == 3
    assert course.enrolled == 11


# ST-04, ST-05 and ST-06: Waitlisted student is added without registration.

def test_waitlisted_student_added_to_waitlist():
    student = Student(student_id="S01")
    course = Course("CS201", 3, 30, 30)

    result = register_course(student, course)

    assert result == "WAITLISTED"
    assert "S01" in course.waitlist
    assert student.current_credits == 0
    assert student.registered_courses == set()
    assert course.enrolled == 30


# ST-07: Duplicate waitlist entry is not added.

def test_waitlisted_student_not_added_twice():
    student = Student(student_id="S01")
    course = Course(
        "CS201", 3, 30, 30,
        waitlist=["S01"]
    )

    result = register_course(student, course)

    assert result == "WAITLISTED"
    assert course.waitlist.count("S01") == 1


# ST-08, ST-09 and ST-10: Unsuccessful registration does not change state.

@pytest.mark.parametrize(
    "reason",
    ["dues", "duplicate", "prerequisite", "credit"],
    ids=[
        "ST-08-dues",
        "extra-duplicate",
        "ST-09-prerequisite",
        "ST-10-credit"
    ]
)
def test_unsuccessful_registration_does_not_change_state(reason):
    student = Student(
        student_id="S01",
        current_credits=16
    )

    course = Course(
        "CS201",
        3,
        30,
        10,
        prerequisites={"CS101"}
    )

    if reason == "dues":
        student.outstanding_dues = 1

    elif reason == "duplicate":
        student.registered_courses.add("CS201")

    elif reason == "prerequisite":
        student.completed_courses = set()

    elif reason == "credit":
        student.completed_courses = {"CS101"}

    original_credits = student.current_credits
    original_registered = student.registered_courses.copy()
    original_enrolled = course.enrolled
    original_waitlist = course.waitlist.copy()

    register_course(student, course)

    assert student.current_credits == original_credits
    assert student.registered_courses == original_registered
    assert course.enrolled == original_enrolled
    assert course.waitlist == original_waitlist


# ============================================================
# A5. WITHDRAWAL STATE TESTING
# ============================================================

# WD-01, WD-02, WD-03 and WD-04: Successful withdrawal.

def test_withdraw_registered_course():
    student = Student(
        student_id="S01",
        current_credits=3,
        registered_courses={"CS201"}
    )

    course = Course("CS201", 3, 30, 10)

    result = withdraw_course(student, course)

    assert result is True
    assert "CS201" not in student.registered_courses
    assert student.current_credits == 0
    assert course.enrolled == 9


# WD-05 and WD-06: Withdrawal when course is not registered.

def test_withdraw_unregistered_course():
    student = Student(
        student_id="S01",
        current_credits=6,
        registered_courses={"CS101"}
    )

    course = Course("CS201", 3, 30, 10)

    original_credits = student.current_credits
    original_registered = student.registered_courses.copy()
    original_enrolled = course.enrolled

    result = withdraw_course(student, course)

    assert result is False
    assert student.current_credits == original_credits
    assert student.registered_courses == original_registered
    assert course.enrolled == original_enrolled


# ============================================================
# ADDITIONAL VALIDATION TESTS
# ============================================================

# Invalid dues must be checked before invalid capacity.

def test_invalid_dues_checked_before_invalid_capacity():
    student = Student(student_id="S01", outstanding_dues=-1)
    course = Course("CS201", 3, 0, 0)

    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(student, course)


# Current credits must be checked before course credits.

def test_current_credits_validation_priority():
    with pytest.raises(ValueError, match="Invalid current credits"):
        check_credit_limit(-1, 5)
