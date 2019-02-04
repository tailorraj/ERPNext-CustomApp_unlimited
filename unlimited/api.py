from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint, cstr, add_days, getdate, get_datetime, get_time, validate_email_add, today, add_years, format_datetime


@frappe.whitelist(allow_guest=True)
def get_available_slots(date, employee):
  date = getdate(date)
  weekday = date.strftime("%A")

  available_slots = []
  employee_schedule_name = None
  employee_schedule = None
  employee_appointment_durations = None
  employee_holiday_name = None
  is_holiday = 'No'
  is_on_leave = 'No'
  has_employee_schedule = 'Yes'
  has_employee_time_per_appointment = 'Yes'
  is_employee_available = 'Yes'

  # if holiday return
  employee_holiday_name = frappe.db.get_value("Employee", employee, "holiday_list")
  if employee_holiday_name:
    employee_holidays = frappe.get_doc("Holiday List", employee_holiday_name)

    if employee_holidays:
      for t in employee_holidays.holidays:
        if t.holiday_date == date:
          is_holiday = 'Yes'

  # if employee on leave return
  leave_application_list = frappe.db.sql("""SELECT * FROM `tabLeave Application` WHERE `tabLeave Application`.status = 'Approved' AND `tabLeave Application`.employee = %s AND (%s BETWEEN `tabLeave Application`.from_date AND `tabLeave Application`.to_date)""" ,(cstr(employee), cstr(date)),as_dict = 1)

  if leave_application_list and len(leave_application_list) > 0:
    is_on_leave = 'Yes'

  # get barber's schedule
  employee_schedule_name = frappe.db.get_value("Employee", employee, "daily_schedule_list")
  if employee_schedule_name:
    employee_schedule = frappe.get_doc("Employee Schedule", employee_schedule_name)
    employee_appointment_durations = frappe.db.get_value("Employee", employee, "time_per_appointment")
  else:
    has_employee_schedule = 'No'

  if employee_schedule:
    for t in employee_schedule.time_slots:
      if weekday == t.day:
        available_slots.append(t)

  if not employee_appointment_durations:
    has_employee_time_per_appointment = 'No'

  # if employee not available return
  if not available_slots:
    is_employee_available = 'No'

  # get appointments on that day for employee
  appointments = frappe.get_all(
    "Tenant Order",
    filters={"employee": employee, "appointment_date": date},
    fields=["name", "appointment_time", "duration", "workflow_state"])

  return {
    "available_slots": available_slots,
    "appointments": appointments,
    "duration_of_service": employee_appointment_durations,
    "is_holiday": is_holiday,
    "is_on_leave":is_on_leave,
    "has_employee_schedule": has_employee_schedule,
    "has_employee_time_per_appointment": has_employee_time_per_appointment,
    "is_employee_available": is_employee_available
  }