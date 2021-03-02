# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar as cal
import pytz
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from babel.dates import format_datetime

from odoo import api, fields, models, _
from odoo.tools.misc import get_lang


class CalendarAppointmentType(models.Model):
    _inherit = "calendar.appointment.type"

    def _get_appointment_slots(self, timezone, employee=None):
        """ Fetch available slots to book an appointment
            :param timezone: timezone string e.g.: 'Europe/Brussels' or 'Etc/GMT+1'
            :param employee: if set will only check available slots for this employee
            :returns: list of dicts (1 per month) containing available slots per day per week.
                      complex structure used to simplify rendering of template
        """
        self.ensure_one()
        appt_tz = pytz.timezone(self.appointment_tz)
        requested_tz = pytz.timezone(timezone)
        first_day = requested_tz.fromutc(
            datetime.utcnow() + relativedelta(hours=self.min_schedule_hours))
        last_day = requested_tz.fromutc(
            datetime.utcnow() + relativedelta(days=self.max_schedule_days))

        # Compute available slots (ordered)
        slots = self._slots_generate(first_day.astimezone(appt_tz),
                                     last_day.astimezone(appt_tz), timezone)
        if not employee or employee in self.employee_ids:
            self._slots_available(slots, first_day.astimezone(pytz.UTC),
                                  last_day.astimezone(pytz.UTC), employee)

        # Compute calendar rendering and inject available slots
        today = requested_tz.fromutc(datetime.utcnow())
        start = today
        month_dates_calendar = cal.Calendar(0).monthdatescalendar
        months = []
        x_studio_busy_days_ids = self.x_studio_busy_days
        busy_dates = []
        for busy_days in x_studio_busy_days_ids:
            date_modified = busy_days.x_studio_start_date
            busy_dates.append(date_modified)
            while date_modified < busy_days.x_studio_end_date:
                date_modified += timedelta(days=1)
                busy_dates.append(date_modified)
        busy_dates = list(tuple(busy_dates))
        while (start.year, start.month) <= (last_day.year, last_day.month):
            dates = month_dates_calendar(start.year, start.month)
            for week_index, week in enumerate(dates):
                for day_index, day in enumerate(week):
                    mute_cls = weekend_cls = today_cls = None
                    today_slots = []
                    if day.weekday() in (cal.SUNDAY, cal.SATURDAY):
                        weekend_cls = 'o_weekend'
                    if day == today.date() and day.month == today.month:
                        today_cls = 'o_today'
                    if day.month != start.month:
                        mute_cls = 'text-muted o_mute_day'
                    else:
                        # slots are ordered, so check all unprocessed slots from until > day
                        while slots and (slots[0][timezone][0].date() <= day):
                            if (slots[0][timezone][0].date() == day) and \
                                    ('employee_id' in slots[0]) and \
                                    (day not in busy_dates):
                                today_slots.append({
                                    'employee_id': slots[0]['employee_id'].id,
                                    'datetime': slots[0][timezone][0].strftime('%Y-%m-%d %H:%M:%S'),
                                    'hours': slots[0][timezone][0].strftime('%H:%M')
                                })
                            slots.pop(0)
                    dates[week_index][day_index] = {
                        'day': day,
                        'slots': today_slots,
                        'mute_cls': mute_cls,
                        'weekend_cls': weekend_cls,
                        'today_cls': today_cls
                    }

            months.append({
                'month': format_datetime(start, 'MMMM Y',
                                         locale=get_lang(self.env).code),
                'weeks': dates
            })
            start = start + relativedelta(months=1)
        return months
