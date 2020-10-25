#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json , sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


db = SQLAlchemy(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(9999))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent= db.Column(db.Boolean)
    seeking_description= db.Column(db.String(1000))
    past_shows_count= db.Column(db.Integer, default=0)
    upcoming_shows_count= db.Column(db.Integer, default=0)
    genres = db.Column(db.String(120))
    show_venue = db.relationship('Shows',backref='venue',cascade="all, delete-orphan")
    
    def __repr__(self):
      return f"<Venue ID: {self.id}, Venue city: {self.city}>"


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(9999))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue= db.Column(db.Boolean)
    seeking_description= db.Column(db.String(1000))
    past_shows_count= db.Column(db.Integer, default=0)
    upcoming_shows_count= db.Column(db.Integer, default=0)
    show_artist = db.relationship('Shows',backref='artist',cascade="all, delete-orphan")

    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Shows(db.Model):
    __tablename__ = 'Shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id= db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id= db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time= db.Column(db.DateTime , nullable=False)
    upcoming= db.Column(db.Boolean)
    past= db.Column(db.Boolean)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  cities= Venue.query.distinct("city","state").all()
  
  data=[]
  jsondict={}

  for i in range(len(cities)):
    body={}
    VenueData= Venue.query.filter_by(city=cities[i].city, state=cities[i].state).all()
    body["city"] = cities[i].city
    body["state"] = cities[i].state
    body["venues"] = [{
       "id": VenueData[j].id,
       "name": VenueData[j].name,
       "num_upcoming_shows": VenueData[j].upcoming_shows_count
    }  for j in range(len(VenueData))]
    data.append(body)
  jsondict["data"]=data

  return render_template('pages/venues.html', areas=data )

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  IteamSearched= Venue.query.filter(Venue.name.ilike('%'+request.form.get('search_term')+'%'))
  
  response={
    "count": IteamSearched.count(),
    "data": [{
      "id": IteamSearched[i].id,
      "name": IteamSearched[i].name,
      "num_upcoming_shows": IteamSearched[i].upcoming_shows_count,
    } for i in range(IteamSearched.count())]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  VenueData= Venue.query.get(venue_id)
  upcomingShowsData= Shows.query.filter_by(venue_id=venue_id).filter_by(upcoming=True).join(Artist).join(Venue).all()
  upcomingbody={}
  upcomingData=[]
  if len(upcomingShowsData)>0:
    for i in range(len(upcomingShowsData)):
      body={}
      body["artist_id"]=upcomingShowsData[i].artist.id
      body["artist_name"]=upcomingShowsData[i].artist.name
      body["artist_image_link"]=upcomingShowsData[i].artist.image_link
      body["start_time"]=str(upcomingShowsData[i].start_time)
      upcomingData.append(body)
    upcomingbody["upcomingData"]= upcomingData 
  else:
    upcomingbody["upcomingData"]= [] 

  pastShowsData= Shows.query.filter_by(venue_id=venue_id).filter_by(past=True).join(Artist).join(Venue).all()
  pastbody={}
  pastData=[]
  if len(pastShowsData)>0:
    for i in range(len(pastShowsData)):
      body={}
      body["artist_id"]=pastShowsData[i].artist.id
      body["artist_name"]=pastShowsData[i].artist.name
      body["artist_image_link"]=pastShowsData[i].artist.image_link
      body["start_time"]=str(pastShowsData[i].start_time)
      pastData.append(body)
    pastbody["pastData"]= pastData 
  else:
    pastbody["pastData"]= []
  data={
    "id": VenueData.id,
    "name": VenueData.name,
    "genres": [VenueData.genres],
    "address": VenueData.address,
    "city": VenueData.city,
    "state": VenueData.state,
    "phone": VenueData.phone,
    "website": VenueData.website_link,
    "facebook_link": VenueData.facebook_link,
    "seeking_talent": VenueData.seeking_talent,
    "seeking_description":VenueData.seeking_description,
    "image_link": VenueData.image_link,
    "past_shows": pastbody["pastData"],
    "upcoming_shows": upcomingbody["upcomingData"],
    "past_shows_count": VenueData.past_shows_count,
    "upcoming_shows_count": VenueData.upcoming_shows_count,
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venueName = request.form['name']
        city= request.form["city"]
        state= request.form["state"]
        address= request.form["address"]
        phone= request.form["phone"]
        genres= request.form.getlist("genres")

        if(request.form["website_link"]):
          web= request.form["website_link"]
        else:
          web= None   
        
        if(request.form["facebook_link"]):
          fb= request.form["facebook_link"]
        else:
          fb= None     
        
        if(request.form["image_link"]):
          image= request.form["image_link"]
        else:
          image= None  
        
        try:
          if request.form["seeking_talent"]:
           seeking_talent= int(request.form["seeking_talent"])
          else:
           seeking_talent= 0
        except:
          seeking_talent= 0
        
        if(request.form["seeking_description"]):
          desc= request.form["seeking_description"]
        else:
          desc= None  
        
        insert = Venue(name=venueName, city=city, state=state, address=address, phone=phone, image_link=image, 
                      facebook_link=fb,website_link=web,seeking_talent=seeking_talent,seeking_description=desc, genres=genres)
        db.session().add(insert)
        db.session().commit()
    except:
        error = True
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    error=False
    try:
        venue = Venue.query.get(venue_id)
        for venue in venue.show_venue:
             db.session.delete(venue)
        VenueName= Venue.query.get(venue_id).name
        Venue.query.filter_by(id=venue_id).delete()
        db.session().commit()
    except:
      error=True
      flash('An error occurred. Venue ' + VenueName + ' could not be deleted.')
      db.session.rollback()  
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + VenueName + ' was successfully deleted!')    

    return redirect(url_for('pages/home.html'))

@app.route('/artist/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
    error=False
    try:
        artist = Artist.query.get(artist_id)
        for artist in artist.show_artist:
             db.session.delete(artist)
        ArtistName= Artist.query.get(artist_id).name
        Artist.query.filter_by(id=artist_id).delete()
        db.session().commit()
    except:
      error=True
      flash('An error occurred. Venue ' + ArtistName + ' could not be deleted.')
      db.session.rollback()  
    finally:
      db.session.close()
    if not error:
        flash('Artist ' + ArtistName + ' was successfully deleted!')    

    return redirect(url_for('pages/home.html'))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=Artist.query.order_by("id").all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  IteamSearched= Artist.query.filter(Artist.name.ilike('%'+request.form.get('search_term')+'%'))

  response={
    "count": IteamSearched.count(),
    "data": [{
      "id": IteamSearched[i].id,
      "name": IteamSearched[i].name,
      "num_upcoming_shows": IteamSearched[i].upcoming_shows_count,
    } for i in range(IteamSearched.count())]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artistData= Artist.query.get(artist_id)
  
  upcomingShowsData= Shows.query.filter_by(artist_id=artist_id).filter_by(upcoming=True).join(Artist).join(Venue).all()
  upcomingbody={}
  upcomingData=[]
  if len(upcomingShowsData)>0:
    for i in range(len(upcomingShowsData)):
      body={}
      body["venue_id"]=upcomingShowsData[i].venue.id
      body["venue_name"]=upcomingShowsData[i].venue.name
      body["venue_image_link"]=upcomingShowsData[i].venue.image_link
      body["start_time"]=str(upcomingShowsData[i].start_time)
      upcomingData.append(body)
    upcomingbody["upcomingData"]= upcomingData 
  else:
    upcomingbody["upcomingData"]= [] 

  pastShowsData= Shows.query.filter_by(artist_id=artist_id).filter_by(past=True).join(Artist).join(Venue).all()
  pastbody={}
  pastData=[]
  if len(pastShowsData)>0:
    for i in range(len(pastShowsData)):
      body={}
      body["artist_id"]=pastShowsData[i].artist.id
      body["artist_name"]=pastShowsData[i].artist.name
      body["venue_image_link"]=pastShowsData[i].artist.image_link
      body["start_time"]=str(pastShowsData[i].start_time)
      pastData.append(body)
    pastbody["pastData"]= pastData 
  else:
    pastbody["pastData"]= []
  data={
    "id": artistData.id,
    "name": artistData.name,
    "genres": [artistData.genres],
    "city": artistData.city,
    "state": artistData.state,
    "phone": artistData.phone,
    "website": artistData.website_link,
    "facebook_link": artistData.facebook_link,
    "seeking_venue": artistData.seeking_venue,
    "seeking_description": artistData.seeking_description,
    "image_link": artistData.image_link,
    "past_shows": pastbody["pastData"],
    "upcoming_shows": upcomingbody["upcomingData"],
    "past_shows_count": artistData.past_shows_count,
    "upcoming_shows_count": artistData.upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  ArtistData= Artist.query.get(artist_id)

  artist={
    "id": ArtistData.id,
    "name": ArtistData.name,
    "genres": [ArtistData.genres],
    "city": ArtistData.city,
    "state": ArtistData.state,
    "phone": ArtistData.phone,
    "website": ArtistData.website_link,
    "facebook_link": ArtistData.facebook_link,
    "seeking_venue": ArtistData.seeking_venue,
    "seeking_description": ArtistData.seeking_description,
    "image_link": ArtistData.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    ArtistData=Artist.query.get(artist_id)
    ArtistData.name = request.form['name']
    ArtistData.city= request.form["city"]
    ArtistData.state= request.form["state"]
    ArtistData.phone= request.form["phone"]
    ArtistData.genres= request.form.getlist("genres")

    if(request.form["website_link"]):
      ArtistData.website_link= request.form["website_link"]
    else:
      ArtistData.website_link= ""   
          
    if(request.form["facebook_link"]):
      ArtistData.facebook_link= request.form["facebook_link"]
    else:
      ArtistData.facebook_link= ""     
          
    if(request.form["image_link"]):
      ArtistData.image_link= request.form["image_link"]
    else:
      ArtistData.image_link= ""  
          
    try:
      if request.form["seeking_venue"]:
        ArtistData.seeking_venue= int(request.form["seeking_venue"])
      else:
        ArtistData.seeking_venue= 0
    except:
        ArtistData.seeking_venue= 0
          
    if(request.form["seeking_description"]):
      ArtistData.seeking_description= request.form["seeking_description"]
    else:
      ArtistData.seeking_description= ""    
    
    db.session().commit()     
  except:
        error = True
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
        db.session.rollback()
        print(sys.exc_info())
  finally:
        db.session.close()
  if not error:
        flash('Artist ' + request.form['name'] + ' was successfully edited!') 
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  data = Venue.query.get(venue_id)   
  venue={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "address": data.address,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website_link,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.seeking_talent,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    VenueData=Venue.query.get(venue_id)
    VenueData.name = request.form['name']
    VenueData.city= request.form["city"]
    VenueData.state= request.form["state"]
    VenueData.address= request.form["address"]
    VenueData.phone= request.form["phone"]
    VenueData.genres= request.form.getlist("genres")

    if(request.form["website_link"]):
      VenueData.website_link= request.form["website_link"]
    else:
      VenueData.website_link= ""   
          
    if(request.form["facebook_link"]):
      VenueData.facebook_link= request.form["facebook_link"]
    else:
      VenueData.facebook_link= ""     
          
    if(request.form["image_link"]):
      VenueData.image_link= request.form["image_link"]
    else:
      VenueData.image_link= ""  
          
    try:
      if request.form["seeking_talent"]:
        VenueData.seeking_talent= int(request.form["seeking_talent"])
      else:
        VenueData.seeking_talent= 0
    except:
        VenueData.seeking_talent= 0
          
    if(request.form["seeking_description"]):
      VenueData.seeking_description= request.form["seeking_description"]
    else:
      VenueData.seeking_description= ""    
    
    db.session().commit()     
  except:
        error = True
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
        db.session.rollback()
        print(sys.exc_info())
  finally:
        db.session.close()
  if not error:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')       
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        artistName = request.form['name']
        city= request.form["city"]
        state= request.form["state"]
        phone= request.form["phone"]
        genres= request.form.getlist("genres")

        if(request.form["website_link"]):
          web= request.form["website_link"]
        else:
          web= None   
        
        if(request.form["facebook_link"]):
          fb= request.form["facebook_link"]
        else:
          fb= None     
        
        if(request.form["image_link"]):
          image= request.form["image_link"]
        else:
          image= None  
        
        try:
          if request.form["seeking_venue"]:
           seeking_venue= int(request.form["seeking_venue"])
          else:
           seeking_venue= 0
        except:
           seeking_venue= 0
        
        if(request.form["seeking_description"]):
          desc= request.form["seeking_description"]
        else:
          desc= None  
        
        insert = Artist(name=artistName, city=city, state=state, phone=phone, image_link=image, 
                      facebook_link=fb,website_link=web,seeking_venue=seeking_venue,seeking_description=desc, genres=genres)
        db.session().add(insert)
        db.session().commit()
    except:
        error = True
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  allData= Shows.query.join(Artist).join(Venue).all()
  data=[]
  jsondict={}

  for i in  range(len(allData)):
    body={}
    body["venue_id"]= allData[i].venue.id
    body["venue_name"]= allData[i].venue.name
    body["artist_id"]= allData[i].artist.id
    body["artist_name"]= allData[i].artist.name
    body["artist_image_link"]= allData[i].artist.image_link
    body["start_time"]=str(allData[i].start_time)
    data.append(body)
  jsondict["data"]=data  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    now = datetime.datetime.now()
    
    try:
        ArtistID= request.form["artist_id"]
        VenueID = request.form['venue_id']
        startTime= request.form["start_time"]
  
        date_time_obj = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
        
        VenueData=Venue.query.get(VenueID)
        ArtistData=Artist.query.get(ArtistID)

        if(now > date_time_obj):
          past= True
          upcoming= False
          VenueData.past_shows_count = VenueData.past_shows_count+1
          ArtistData.past_shows_count = ArtistData.past_shows_count+1

        elif(now < date_time_obj):
          past= False
          upcoming= True  
          VenueData.upcoming_shows_count = VenueData.upcoming_shows_count+1
          ArtistData.upcoming_shows_count = ArtistData.upcoming_shows_count+1

        insert = Shows(venue_id=VenueID, artist_id=ArtistID,start_time=startTime,past=past,upcoming=upcoming)
        db.session().add(insert)
        db.session().commit()
    except:
        error = True
        flash('Show failed to be listed!')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash('Show was successfully listed!')
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
