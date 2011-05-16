Myschedule 1.0.6
================
Application update only with one new setting, S2W_FAILURE_MESSAGE (see base.py).

myschedule 1.0.5
================
Application update only.

myschedule 1.0.4
================
Application update only.

myschedule 1.0.3
================
Application update only.

myschedule 1.0.2
================
Install application update.
Drop table myschedule_schedule and run syncdb.
Has the following settings updates:
 * Change value of CAS_REDIRECT_URL
 * Remove setting CAS_IGNORE_REFERER
 * Rename setting DOWNTIME_MESSAGE to S2W_DOWNTIME_MESSAGE

myschedule 1.0.1
=======================
 Application update only, but has the following settings updates:
 * Renamed setting KNOWNHOSTS to S2W_KNOWNHOSTS
 * Removed setting DATA_CREDENTIALS
 * Added settings:  AUTH_IP_FOR_COURSE_UPDATE,  AUTH_KEY_FOR_COURSE_UPDATE,
                    AUTH_IP_FOR_SEAT_UPDATE,  AUTH_KEY_FOR_SEAT_UPDATE,
                    S2W_UNAVAILABLE_BEGIN, S2W_UNAVAILABLE_END,
                    DOWNTIME_MESSAGE
 Dependent on version 1.0.1 of the scheduledata integration script.

myschedule 1.0.0
=======================
 * Initial release
