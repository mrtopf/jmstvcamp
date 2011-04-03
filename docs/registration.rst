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

Special conditions
------------------

 * The attendance list is full and the user is formerly not attending but now wants to attend
    1. The edit screen shows already that the list is full
    2. After changing the user is put onto the waiting list
    3. The user gets a flash message telling him, that he now is on the waiting
       list
 * The attendance list is full and a user changes state from "yes" to "no" or
   "maybe".
    1. The user is removed from the list and put onto the other list
    2. A user from the waiting list is selected and put onto the attendance
       list
    3. An email is sent to the user telling him that he now is attending




A user forgot the link to the manage page
=========================================

 1. The user clicks the forgotten-link
 2. The user enters his email address
 3. The system sends another mail

If the user enters a wrong email address then it will be said so and another attempt can be made.



