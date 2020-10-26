import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from  sqlalchemy.sql.expression import func, select

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request,selection):
  page=request.args.get('page',1,type=int)
  start= (page-1) * QUESTIONS_PER_PAGE
  end= start + QUESTIONS_PER_PAGE
  formatted_selection=[question.format() for question in selection]
  return formatted_selection[start:end]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  @app.route('/categories')
  def show_all_categories():
    categories= Category.query.order_by(Category.id).all()
    formatted_categories=[category.format() for category in categories]
    
    if len(formatted_categories) == 0:
      abort(404)

    return jsonify({
      'success':True,
      'categories': formatted_categories,
      'total_categories':len(formatted_categories)
    })  

  @app.route('/questions')
  def show_questions():
    questions= Question.query.join(Category).order_by(Question.id).all()
    formatted_questions=paginate_questions(request,questions)
    formatted_categories=[category.type for category in questions[0].category_backref.query.all()]

    if len(formatted_questions) == 0:
      abort(404)

    return jsonify({
      'success':True,
      'questions': formatted_questions,
      'total_questions':len(questions),
      'categories': formatted_categories
    })  

  @app.route('/questions/<int:question_id>',methods=["DELETE"])
  def delete_questions(question_id):

    try:
      question=Question.query.filter_by(id=question_id).one_or_none()

      if(question is None):
        abort(404)

      question.delete()
      questions= Question.query.order_by(Question.id).all()
      formatted_questions= paginate_questions(request,questions)
      return jsonify({
      'success':True,
      'deleted':question.id,
      'questions': formatted_questions,
      'total_questions':len(questions)
     })
    except:
        abort(400)  
     
  @app.route('/questions',methods=["POST"])
  def add_question():
    
    body= request.get_json()
    question= body.get("question",None)
    answer= body.get("answer",None)
    difficulty= body.get("difficulty",None)
    category= body.get("category",None)
    search= body.get("searchTerm",None)
    try:

      if search:
        questionQuery= Question.query.filter(Question.question.ilike('%'+search+'%'))
        formatted_questions= paginate_questions(request,questionQuery)

        return jsonify({
        'success':True,
        'questions': formatted_questions,
        'total_questions':questionQuery.count()
        })
      else:  
        questionQuery=Question(question=question,answer=answer,difficulty=difficulty,category=category)
        questionQuery.insert()
        questions= Question.query.order_by(Question.id).all()
        formatted_questions= paginate_questions(request,questions)
        return jsonify({
        'success':True,
        'created':questionQuery.id,
        'questions': formatted_questions,
        'total_questions':len(questions)
      })
    except:
        abort(422)  

  @app.route('/categories/<int:category_id>/questions')
  def show_category_question(category_id):
    questions= Question.query.order_by(Question.id).filter_by(category=category_id).all()
    formatted_questions= paginate_questions(request,questions)
    
    if len(formatted_questions) == 0:
      abort(404)

    return jsonify({
      'success':True,
      'questions': formatted_questions,
      'total_questions': len(formatted_questions),
      'current_category': category_id
    })  

  @app.route('/quizzes',methods=["POST"])
  def play_quiz():
    body=request.get_json()
    category=body.get("quiz_category",None)
    previousQuestions=body.get("previous_questions",None)

    if(category):
      if int(category["id"]) > -1:  
        question= Question.query.filter(~Question.id.in_(previousQuestions)).filter_by(category=category['id']).order_by(func.random()).first() 
      else:
        question= Question.query.filter(~Question.id.in_(previousQuestions)).order_by(func.random()).first()

      if(question):
        formatted_question= question.format()
      else:
        formatted_question=None
        
    return jsonify({
      'success':True,
      'question': formatted_question,
      'current_category': category['id']
    })  

  @app.errorhandler(404)
  def not_found_404(error):
    return jsonify({
      "success":False,
      "message":"Resource Not Found",
      "error":404
    }),404

  @app.errorhandler(400)
  def bad_request_400(error):
        return jsonify({
            'success':False,
            'error': 400,
            'message': "Bad Request"
        }),400  
  @app.errorhandler(405)
  def not_allowed(error):
        return jsonify({
            'success':False,
            'error': 405,
            'message': "Method Not Allowed"
        }),405  

  @app.errorhandler(422)
  def unproccessable_422(error):
    return ({
     'success':False,
     'error':422,
     'Message':"unprocessable"
    }),422           
  return app

    