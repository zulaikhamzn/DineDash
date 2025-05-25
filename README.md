# DineDash

DineDash is a restaurant reservation and food delivery service. It allows restaurants to post their menus and hours online. Customers can then order their food to be delivered to their locations. Customers can also attempt to reserve a seat at a restaurant at a specific date and time (assuming said restaurant is open at that time), and then restaurant staff can either confirm said reservation (assigning it to a table in the process) or cancel it. Delivery contractors can pick up prepared food from restaurants and then deliver it to customers, and said customers will receive real-time updates concerning their orders.

DineDash was created as part of my capstone project (i.e. final project) for my master's degree in computer science at Pace University. It was written in HTML, CSS, JavaScript, and Python using the Django web framework, and HTMX was used to implement real-time updates. I collaborated with nine other students to develop the specifications for the database and features, most of which you can find in the ["Final Project Presentation" directory](Final%20Project%20Presentation/). After said specifications were approved, I then followed them (to a certain extent) when writing the actual code for the application. In the process, I learned about the Agile methodology, the Scrum framework, and how to construct, test, and deploy applications that meet the customers' needs.

Please note that DineDash was written so that it could be easily set up and tested. As a result of this, several parts of the application were not written for real-world scenarios. For example, the Django secret key is not hidden, and the credit/debit card information that the user provides when placing an order is not actually processed. Also, several commits in the Git history don't change any actual code, but are instead intended to trigger certain Jenkins actions. The messages for those commits will usually contain something like "This commit is meant to trigger a notification."

## Recoded Demonstrations

I recorded demonstrations for the three sprints that took place during this course. You can find them in the ["Demonstrations" directory](Demonstrations/)

## Installation

If you want to run DineDash locally on your computer, clone this repository and run the following commands inside the newly created directory. They will install the required packages (first command), perform database migrations (second command), and start the Django development server (third command). You will need Python 3.13 to be installed.

```
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

If you want the application to send out emails when the status of a reservation has changed, then set the following environment variables before starting the server:

* USE_SMTP_FOR_EMAIL=True
* EMAIL_HOST=<your SMTP email host>
* EMAIL_PORT=<your SMTP email port>
* EMAIL_HOST_USER=<your SMTP user>
* EMAIL_HOST_PASSWORD=<your SMTP password>
* EMAIL_USE_TLS=<False if you don't want to use TLS. Default is True.>
* EMAIL_TIMEOUT=<Timeout (in seconds) for sending emails. Default is 2.>

These variables can be set in your shell or in a file inside the cloned repository called ".env". If you don't set USE_SMTP_FOR_EMAIL to True, then all notifications related to reservations will be printed to the console.