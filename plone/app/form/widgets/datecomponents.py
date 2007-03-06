from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import getUtility

from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from DateTime.DateTime import DateTimeError
from Products.CMFCore.interfaces import IPropertiesTool
from Products.Five.browser import BrowserView

from interfaces import IDateComponents

CEILING=DateTime(9999, 0)
FLOOR=DateTime(1970, 0)
PLONE_CEILING=DateTime(2021,0) # 2020-12-31


def english_month_names():
    names={}
    for x in range(1,13):
        faux=DateTime(2004, x, 1)
        names[x]=faux.Month()
    return names

ENGLISH_MONTH_NAMES=english_month_names()

class DateComponents(BrowserView):
    """A view that provides some helper methods useful in date widgets.
    """

    implements(IDateComponents)

    def result(self, date=None,
               use_ampm=False,
               starting_year=None,
               ending_year=None,
               future_years=None,
               minute_step=5):
        """Returns a dict with date information.
        """

        ptool = getUtility(IPropertiesTool)
        site_props = ptool.site_properties

        # Get the date format from the locale
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')

        locale = portal_state.locale()
        dates = portal_state.locale().dates

        timepattern = dates.getFormatter('time').getPattern()
        if 'a' in timepattern:
             use_ampm = True
        month_names = dates.getFormatter('date').calendar.months

        # 'id' is what shows up.  December for month 12. 
        # 'value' is the value for the form.
        # 'selected' is whether or not it is selected.

        default=0
        years=[]
        days=[]
        months=[]
        hours=[]
        minutes=[]
        ampm=[]
        now=DateTime()

        # This debacle is because the date that is usually passed in ends with GMT
        # and of course DateTime is too stupid to handle it.  So we strip it off.

        if isinstance(date, basestring):
            date=date.strip()
            if not date:
                date=None
            elif date.split(' ')[-1].startswith('GMT'):
                date=' '.join(date.split(' ')[:-1])

        if date is None:
            date=now
            default=1
        elif not isinstance(date, DateTime):
            try:
                date=DateTime(date)
            except (TypeError, DateTimeError):
                date=now
                default=1

        # Anything above PLONE_CEILING should be PLONE_CEILING
        if date.greaterThan(PLONE_CEILING):
            date = PLONE_CEILING

        # Get portal year range
        if starting_year is None:
            min_year = site_props.getProperty('calendar_starting_year', 1999)
        else:
            min_year = starting_year
        if ending_year is None:
            if future_years is None:
                max_year = site_props.getProperty('calendar_future_years_available', 5) + now.year()
            else:
                max_year = future_years + now.year()
        else:
            max_year = ending_year

        year=int(date.strftime('%Y'))

        if min_year != max_year:
            years.append({'id': '--', 'value': '0000', 'selected': None})

        for x in range(min_year, max_year+1):
            d={'id': x, 'value': x, 'selected': None}
            if x==year:
                d['selected']=1
            years.append(d)

        month=int(date.strftime('%m'))

        if default:
            months.append({'id': '--', 'value': '00', 'selected': 1, 'title': '--'})
        else:
            months.append({'id': '--', 'value': '00', 'selected': None, 'title': '--'})

        for x in range(1, 13):
            d={'id': ENGLISH_MONTH_NAMES[x], 'value': '%02d' % x, 'selected': None}
            if x==month and not default:
                d['selected']=1
            d['title']=month_names[x][0]
            months.append(d)

        day=int(date.strftime('%d'))

        if default:
            days.append({'id': '--', 'value': '00', 'selected': 1})
        else:
            days.append({'id': '--', 'value': '00', 'selected': None})

        for x in range(1, 32):
            d={'id': x, 'value': '%02d' % x, 'selected': None}
            if x==day and not default:
                d['selected']=1
            days.append(d)

        if use_ampm:
            hours_range=[12]+range(1,12)
            hour_default='12'
            hour=int(date.strftime('%I'))
        else:
            hours_range=range(0,24)
            hour_default='00'
            hour=int(date.strftime('%H'))

        if default:
            hours.append({'id': '--', 'value': hour_default, 'selected': 1})
        else:
            hours.append({'id': '--', 'value': hour_default, 'selected': None})

        for x in hours_range:
            d={'id': '%02d' % x, 'value': '%02d' % x, 'selected': None }
            if x==hour and not default:
                d['selected']=1
            hours.append(d)

        minute=int(date.strftime('%M'))

        if default:
            minutes.append({'id': '--', 'value': '00', 'selected': 1})
        else:
            minutes.append({'id': '--', 'value': '00', 'selected': None})

        for x in range(0, 60, minute_step):
            d={'id': '%02d' % x, 'value': '%02d' % x, 'selected': None}
            if (x==minute or minute < x < minute+minute_step) and not default:
                d['selected']=1
            minutes.append(d)

        if use_ampm:
            p=date.strftime('%p')

            if default:
                ampm.append({'id': '--', 'value': 'AM', 'selected': 1})
            else:
                ampm.append({'id': '--', 'value': 'AM', 'selected': None})

            for x in ('AM', 'PM'):
                d={'id': x, 'value': x, 'selected': None}
                if x==p and not default:
                    d['selected']=1
                ampm.append(d)

        return {'years': years, 'months': months, 'days': days,
                'hours': hours, 'minutes': minutes, 'ampm': ampm}
