Myschedule 1.0.14
=================
Application updated to allow viewing of all courses.
# Update application.
# Updated schema.xml and synonyms.txt (copy to appropriate solr/conf, stop and restart solr, run update_index)

Myschedule 1.0.13
================
Application updated to allow sorting and to add filter by term.
# New setting in base.py - AVAILABLE_TERMS
# Updated schema.xml (copy to appropriate solr/conf and rebuild index after deploying application update).

Myschedule 1.0.12
=================
Application update only.

Myschedule 1.0.11
=================
Application update with one setting change (set SYSTEM_NOTIFICATION="").
- Explicitly defaults campus and delivery_method advanced search filter fields to "all".

Myschedule 1.0.10
=================
Application updates to add advanced search filter.
  # Copy updated schema.xml, solrconfig.xml, and synonyms.txt to solr conf folder.
  # Rebuild (not just update) solr indexes.
Settings updates to deep link to preferred sections page in webadvisor.
  # Updated settings S2W_DATATEL_URL AND S2W_SUCCESS_MESSAGE (see base.py for new values)

Myschedule 1.0.9
================
Application update and model update (to change book publisher from efolette to barnes and noble).
# Issue the following sql statements to increase size of book_link field:
    use myschedule;
    alter table myschedule_section modify column book_link varchar(510) not null;
# Deploy application update.
# Update course data.
# Update seat counts

Myschedule 1.0.8
================
Application update with one new setting, ALLOW_FEEDBACK (see base.py).

Myschedule 1.0.7
================
Application update only with two new settings, S2W_SUCCESS_MESSAGE and
SYSTEM_NOTIFICATION (see base.py).

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
