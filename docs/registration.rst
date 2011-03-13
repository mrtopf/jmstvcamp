============
Registration
============

The registration knows the following stories:

A user registers with the site
==============================

 1. The user enters name and email address and clicks a button to attend, maybe attend or just be informed
 2. The system stores this in a database and send a confirmation message
 3. The user confirms the message and the user is counted
 4. The systems send another welcome message, telling the user the link to manage his account

The following things can go wrong:

 * If the user does not confirm the message because he loses the mail then another attempt of registering will send the mail again


A user changes the attendance state
===================================

 1. The user clicks the link from the mail for changing the state
 2. The system shows a screen with the following options:
    * Attend
    * Maybe attend
    * just be informed
    * delete account
 3. The user makes a choice and the system does the corresponding action

A user forgot the link to the manage page
=========================================

 1. The user clicks the forgotten-link
 2. The user enters his email address
 3. The system sends another mail

If the user enters a wrong email address then it will be said so and another attempt can be made.



