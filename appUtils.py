# import datetime and calendar modules
import datetime as dt
import calendar

def addMonths(inpDt, mnths):
  tmpMnth = inpDt.month - 1 + mnths

  # Add floor((input month - 1 + k)/12) to input year component to get result year component
  resYr = inpDt.year + tmpMnth // 12

  # Result month component would be (input month - 1 + k)%12 + 1
  resMnth = tmpMnth % 12 + 1

  # Result day component would be minimum of input date component and max date of the result month (For example we cant have day component as 30 in February month)
  # Maximum date in a month can be found using the calendar module monthrange function as shown below
  resDay = min(inpDt.day, calendar.monthrange(resYr,resMnth)[1])

  # construct result datetime with the components derived above
  resDt = dt.datetime(resYr, resMnth, resDay, inpDt.hour, inpDt.minute, inpDt.second, inpDt.microsecond)

  return resDt