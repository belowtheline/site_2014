Data Schemata
=============

Person / People
---------------

* "last_name":  Last name/Surname/Family name of person.
* "first_name": First name/Given name of person.
* "party":      Party affiliation of person, use name of appropriate document in parties.
* "elected":    What the person is currently elected to. Use state for Senators, division for Reps.
* "term_start": Date person's term started, if elected. Use ISO format.
* "previous_terms": Previous elected positions this person has held. Format is a list of [position, start, end].
* "retiring":   Boolean, whether person is retiring at the next election.
* "expiring":   If a Senator, whether their term is due to expire.
* "website":    Official website of person. Don't use APH ministerial websites.
* "wikipedia":  Wikipedia URL for person.
