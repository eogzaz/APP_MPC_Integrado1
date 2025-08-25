import pandas as pd

#De fecha a día juliano
def Date_to_julian(d):
    # Handle pandas Timestamp object if passed
    if isinstance(d, pd.Timestamp):
        year = d.year
        month = d.month
        day_with_fraction = d.day + d.hour / 24.0 + d.minute / (24.0 * 60.0) + d.second / (24.0 * 60.0 * 60.0) + d.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0)
    # Handle 'YYYY-Mon-DD' string format
    elif isinstance(d, str) and '-' in d:
        date_obj = pd.to_datetime(d)
        year = date_obj.year
        month = date_obj.month
        day_with_fraction = date_obj.day + date_obj.hour / 24.0 + date_obj.minute / (24.0 * 60.0) + date_obj.second / (24.0 * 60.0 * 60.0) + date_obj.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0)
    else: # Assume original string format if not a Timestamp or 'YYYY-Mon-DD'
        year, month, day_with_fraction = d.split()
        year = int(year)
        month = int(month)
        day_with_fraction = float(day_with_fraction)

    day = int(day_with_fraction)
    fraction_of_day = day_with_fraction - day
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    jd = int(365.25 * (year + 4716)) \
       + int(30.6001 * (month + 1)) \
         + day + B - 1524.5 + fraction_of_day
    return jd

#Dia juliano sin sin fraccion de dia
def Date_to_julian_N(d):
  return int(Date_to_julian(d))+.5

#De día juliano a fecha
def julian_to_date(jd):
  jd = jd + 0.5 # Sumamos 0.5 para que el inicio del día sea a medianoche

  Z = int(jd)
  F = jd - Z

  alpha = int((Z - 1867216.25)/36524.25)
  A = Z + 1 + alpha - int(alpha/4)

  B = A + 1524
  C = int((B - 122.1)/365.25)
  D = int(365.25 * C)
  E = int((B - D)/30.6001)

  day = B - D - int(30.6001 * E) + F

  if E < 14:
    month = E - 1
  else:
    month = E - 13

  if month > 2:
    year = C - 4716
  else:
    year = C - 4715

  # Convertir el día con fracción a horas, minutos, segundos y microsegundos
  fraction_of_day = day - int(day)
  hour = int(fraction_of_day * 24)
  minute = int((fraction_of_day * 24 - hour) * 60)
  second = int(((fraction_of_day * 24 - hour) * 60 - minute) * 60)
  microsecond = int(((((fraction_of_day * 24 - hour) * 60 - minute) * 60 - second) * 1000000))

  return f'{year} {month} {int(day)}'
