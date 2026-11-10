
import registration
from registration import Student, Course, registration_decision, register_course


def test_dues_blocked_above_1000():
    student = Student(
        student_id="S101",
        outstanding_dues=1001
    )
    course = Course(
        code="CS101",
        credit_hours=3,
        capacity=5
    )

    result = registration_decision(student, course)

    assert result == "DUES_BLOCK"


def test_waitlisted_student_added_once(monkeypatch):
    student = Student(student_id="S102")
    course = Course(
        code="CS102",
        credit_hours=3,
        capacity=5
    )

    monkeypatch.setattr(
        registration,
        "registration_decision",
        lambda student, course: "WAITLISTED"
    )

    result = register_course(student, course)

    assert result == "WAITLISTED"
    assert "S102" in course.waitlist
    assert len(course.waitlist) == 1


def test_waitlisted_student_not_added_twice(monkeypatch):
    student = Student(student_id="S103")
    course = Course(
        code="CS103",
        credit_hours=3,
        capacity=5,
        waitlist=["S103"]
    )

    monkeypatch.setattr(
        registration,
        "registration_decision",
        lambda student, course: "WAITLISTED"
    )

    result = register_course(student, course)

    assert result == "WAITLISTED"
    assert course.waitlist == ["S103"]
