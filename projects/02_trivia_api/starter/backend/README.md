# Full Stack Trivia API Backend

### Getting Started
- Base URL: Currently, this API is hosted locally at `http://127.0.0.1:5000/`, this URL is also set as proxy in frontend configuration. 
- Authentication: The API does not have Authentication keys. 

### Error Handling
Errors are returned as JSON objects as shown below:
```
{
    "success": False, 
    "error": 404,
    "message": "Resource Not Found"
}
```
The API can return four error types:
- 400: Bad Request
- 404: Resource Not Found
- 405: Method Not Allowed
- 422: Not Processable 

### Endpoints 
- GET /categories
- GET /questions
- GET /categories/{category_id}/questions
- POST /questions
- POST /quizzes
- DELETE /questions/{question_id}


#### GET /categories
- General:
    - Gets all categories from database ordered by their id. 
    - Request Arguments: None
    - Returns: json list of categories and their ids, success value, and total number of categories
- Sample: `curl http://127.0.0.1:5000/categories`

``` {
  "categories": [
    {
      "id": 0, 
      "type": "Science"
    }, 
    {
      "id": 1, 
      "type": "Art"
    }, 
    {
      "id": 2, 
      "type": "Geography"
    }, 
    {
      "id": 3, 
      "type": "History"
    }, 
    {
      "id": 4, 
      "type": "Entertainment"
    }, 
    {
      "id": 5, 
      "type": "Sports"
    }
  ], 
  "success": true, 
  "total_categories": 6
}
```

#### GET /questions
- General:
    - Gets all questions from database ordered by their id. 
    - Results are paginated in groups of 10. 
    - Request Arguments: None
    - Returns: json list of questions, success value, all categories, and total number of questions
- Sample: `curl http://127.0.0.1:5000/questions`

``` 
      {
  "categories": [
    "Science", 
    "Art", 
    "Geography", 
    "History", 
    "Entertainment", 
    "Sports"
  ], 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 4, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Tom Cruise", 
      "category": 4, 
      "difficulty": 4, 
      "id": 4, 
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    }, 
    {
      "answer": "Maya Angelou", 
      "category": 3, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {
      "answer": "Edward Scissorhands", 
      "category": 4, 
      "difficulty": 3, 
      "id": 6, 
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }, 
    {
      "answer": "Muhammad Ali", 
      "category": 3, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "Brazil", 
      "category": 5, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
    {
      "answer": "Uruguay", 
      "category": 5, 
      "difficulty": 4, 
      "id": 11, 
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }, 
    {
      "answer": "George Washington Carver", 
      "category": 3, 
      "difficulty": 2, 
      "id": 12, 
      "question": "Who invented Peanut Butter?"
    }, 
    {
      "answer": "Lake Victoria", 
      "category": 2, 
      "difficulty": 2, 
      "id": 13, 
      "question": "What is the largest lake in Africa?"
    }, 
    {
      "answer": "The Palace of Versailles", 
      "category": 2, 
      "difficulty": 3, 
      "id": 14, 
      "question": "In which royal palace would you find the Hall of Mirrors?"
    }
  ], 
  "success": true, 
  "total_questions": 20
}
```
#### GET /categories/{category_id}/questions
- General:
    - Gets all questions from a specific chosen category ordered by their id. 
    - Request Arguments: category_id
    - Returns: json list of questions, success value, current category, and total number of questions in that category
- Sample: `curl http://127.0.0.1:5000/categories/1/questions`

``` {
  "current_category": 1, 
  "questions": [
    {
      "answer": "Escher", 
      "category": 1, 
      "difficulty": 1, 
      "id": 16, 
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }, 
    {
      "answer": "Mona Lisa", 
      "category": 1, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }, 
    {
      "answer": "Jackson Pollock", 
      "category": 1, 
      "difficulty": 2, 
      "id": 19, 
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ], 
  "success": true, 
  "total_questions": 3
}
```


#### POST /questions
- General:
    - Creates a new question using the submitted question, answer, diffculty, and category.
    - Request Arguments: None
    - Returns the id of the created question, success value, total questions, and questions list.
- `curl http://127.0.0.1:5000/questions?page=2 -X POST -H "Content-Type: application/json" -d '{"question":"How many soccer players should each team have on the field at the start of each match?", "answer":"11", "diffculty":"1", "category":"5"}'`
```
{
  "questions": [
    {
      "answer": "11", 
      "category": 5, 
      "difficulty": 1, 
      "id": 31, 
      "question": "How many soccer players should each team have on the field at the start of each match?"
    }, 
  ],
  "created": 31,
  "success": true,
  "total_questions": 21
}
```

#### POST /quizzes
- General:
    - Retrieves category id and a list of previous questions id to create a randomized question in order to play the trivia game.
    - Request Arguments: None
    - Returns a question, success value, and current category.
- `curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"quiz_category": {"id": "5","type": "Sports"},"previous_questions": []}'`
```
{
  "question": [
    {
      "answer": "Brazil", 
      "category": 5, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
  ],
  "success": true,
  "current_category": 5
}
```

#### DELETE /questions/{question_id}
- General:
    - Deletes the question of the given ID if it exists. 
    - Request Arguments: question_id
    - Returns: the id of the question, success value, total questions, and questions list.
- `curl -X DELETE http://127.0.0.1:5000/questions/30`
```
{
  "deleted": 30,
  "questions": [
    {
      "answer": "Apollo 13",
      "category": 4,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    {
      "answer": "Tom Cruise",
      "category": 4,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    {
      "answer": "Maya Angelou",
      "category": 3,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 4,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    },
    {
      "answer": "Muhammad Ali",
      "category": 3,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    {
      "answer": "Brazil",
      "category": 5,
      "difficulty": 3,
      "id": 10,
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    },
    {
      "answer": "Uruguay",
      "category": 5,
      "difficulty": 4,
      "id": 11,
      "question": "Which country won the first ever soccer World Cup in 1930?"
    },
    {
      "answer": "George Washington Carver",
      "category": 3,
      "difficulty": 2,
      "id": 12,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Lake Victoria",
      "category": 2,
      "difficulty": 2,
      "id": 13,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "The Palace of Versailles",
      "category": 2,
      "difficulty": 3,
      "id": 14,
      "question": "In which royal palace would you find the Hall of Mirrors?"
    }
  ],
  "success": true,
  "total_questions": 20
}
```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```