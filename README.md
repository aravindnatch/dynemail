# Dynamic Email
A web application that allows users to modify emails after they have been sent. This project was built with Python using Flask. Test out a version of this project at https://aravindnatch.me/dynemail/

## How it Works
Traditionally, changing the text of your email after you have sent it is not allowed. As loading scripts inside of emails is considered malicious, there is not a straightforward way to achieve message editing. This application leverages email's image loading to serve a dynamic image to the recipient. This image's text can then be later changed or even deleted from this website's CDN, subseqeuntly rendering the changes to the email as well.
