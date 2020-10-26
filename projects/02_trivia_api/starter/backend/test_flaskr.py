import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', '123','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_questions_pagination(self):
       """Test Pagination of questions """
       res=self.client().get('/questions')
       data= json.loads(res.data)
       self.assertEqual(res.status_code,200)
       self.assertEqual(data["success"],True)
       self.assertTrue(data["total_questions"])
       self.assertTrue(data["categories"])
       self.assertTrue(data["questions"])

    def test_book_pagination_404(self):
       """Test Failed Pagination """
       res=self.client().get('/questions/?page=1000')
       data= json.loads(res.data)
       self.assertEqual(res.status_code,404)
       self.assertEqual(data["success"],False)
       self.assertTrue(data["message"])
       self.assertTrue(data["error"])
    
    def test_delete_question(self):
       """Test Successful Delete of questions """
       res=self.client().delete('/questions/50')
       question=Question.query.filter_by(id=50).one_or_none()

       data= json.loads(res.data)
       self.assertEqual(res.status_code,200)
       self.assertEqual(data["success"],True)
       self.assertTrue(data["total_questions"])
       self.assertTrue(data["deleted"])
       self.assertTrue(data["questions"])
       self.assertEqual(question,None)

    def test_delete_question_400(self):
       """Test Failed Delete """
       res=self.client().delete('/questions/1000')
       data= json.loads(res.data)
       self.assertEqual(res.status_code,400)
       self.assertEqual(data["success"],False)
       self.assertTrue(data["message"])
       self.assertTrue(data["error"])

    def test_insert_question(self):
       """Test Successful Insert of questions """
       res=self.client().post('/questions',json={'question':'Are Yodu?','answer':'Yes I AM','difficulty':'5','category':'1'})

       data= json.loads(res.data)
       self.assertEqual(res.status_code,200)
       self.assertEqual(data["success"],True)
       self.assertTrue(data["total_questions"])
       self.assertTrue(data["created"])
       self.assertTrue(data["questions"])

    def test_insert_question_405(self):
       """Test Failed Insert """
       res=self.client().post('/questions/24234234',json={'question':'Are You?','answer':'Yes I AM','difficulty':'5','category':'1'})
       data= json.loads(res.data)
       self.assertEqual(res.status_code,405)
       self.assertEqual(data["success"],False)
       self.assertTrue(data["message"])
       self.assertTrue(data["error"])

    def test_search_question_existing(self):
       """Test Searching Existing Question """
       res=self.client().post('/questions',json={'searchTerm':'What'})
       data= json.loads(res.data)

       self.assertEqual(res.status_code,200)
       self.assertEqual(data["success"],True)
       self.assertTrue(data["questions"])
       self.assertTrue(data["total_questions"] > 0)

    def test_search_question_not_existing(self):
       """Test Searching Non Existing Question """
       res=self.client().post('/questions',json={'searchTerm':'ALPACTIDO'})
       data= json.loads(res.data)

       self.assertEqual(res.status_code,200)
       self.assertEqual(data["success"],True)
       self.assertEqual(data["questions"],[])
       self.assertEqual(data["total_questions"] , 0 )

    def test_get_questions_category(self):
       """Test Getting question by their category (Success) """
       res=self.client().get('/categories/1/questions')
       data= json.loads(res.data)

       self.assertEqual(res.status_code,200)
       self.assertEqual(data["success"],True)
       self.assertTrue(data["questions"])
       self.assertTrue(data["total_questions"])
       self.assertTrue(data["current_category"])

    def test_get_questions_category_404(self):
       """Test Getting question by their category (Fail) """
       res=self.client().get('/categories/132312/questions')
       data= json.loads(res.data)
      
       self.assertEqual(res.status_code,404)
       self.assertEqual(data["success"],False)
       self.assertTrue(data["message"])
       self.assertTrue(data["error"])

    def test_play_quiz(self):
       """Test Play Quiz"""
       res=self.client().post('/quizzes',json={'quiz_category':{'id':'1','type':'Art'},'previous_questions':[11,10,13]})
       data= json.loads(res.data)
     
       self.assertEqual(res.status_code,200)
       self.assertEqual(data["success"],True)
       self.assertTrue(data["question"])
       self.assertTrue(data["current_category"])
                   

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()