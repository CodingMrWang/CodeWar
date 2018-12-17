# CodeWar
This is a Code War Django Web application which allows users to do coding competition in team

```
pip3 install -r requirements.txt
docker run -p 6379:6379 -d redis:2.8
python3 manage.py runserver
```

Basic description:

This is a code war game web application. User could form a team of four people to have a code competition or start an individual battle to practice.
In this project, web socket is used for room allocation and real-time chat. JQuery and AJAX is used for user state updating and code, result saving as well as updating. ACE library is used for code syntax highlight. MongoDB is used for questions and test cases store, redis is used for code and result saving, rds is used for user information store.


Functions:

Community

	1. Create a room
	2. Recive a invitation and accept or reject it
	3. Enter a room
	4. Edit your profile
	5. See ranking of users
	6. See your own profile

Room

	1. Press Start it to get prepared
	2. Switch to another team
	3. Exit the room
	4. If you are the room owner, you can set the room tobe private room or public room.

Battle

	1. Chat with your teammate
	2. See the question, score.
	3. Write codes to solve the question
	4. Go to your teammate's question and help him
	5. See your teammate's code by clicking see teammate code button
	6. Write test case and run with it
	7. Sumbit your code to see the result
  
  
