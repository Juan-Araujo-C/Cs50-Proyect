# Cs50-Proyect
Web server that locates natural disasters around the world
#### Video Demo: https://www.youtube.com/watch?v=_pzFCakm9V8
#### Description:
The implemented system comprises a Flask-based web server that makes real-time requests to the NASA API known as The Earth Observatory Natural Event Tracker (EONET). This API provides information about natural disasters worldwide in JSON format.

The web interface begins with a login section where users can authenticate. If a user does not have an existing account, there is a registration option. During this process, a valid email address and a password that meets certain requirements, such as a minimum length of 8 characters, at least one uppercase letter, and at least one number, are requested.

Once authenticated, the web presents two main sections:

Map: This segment visualizes a world map with markers highlighting events in different geographical regions.

History: Here, all events provided by the API are presented in a textual format, allowing users to review detailed information.

Additionally, there is a "Change Password" section where users can modify their passwords. Specific requirements are set for the new password, such as a minimum length of 8 characters, at least one uppercase letter, and at least one digit.

Finally, a "Logout" section is included, allowing users to end their current session, ensuring the security and privacy of user information.
