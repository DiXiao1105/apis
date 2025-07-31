from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password123@localhost:5432/triptrove'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    trips = db.relationship('Trip', backref='user', lazy=True)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(200))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    travelers = db.Column(db.Integer)
    notes = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    items = db.relationship('ItineraryItem', backref='trip', lazy=True)
    comments = db.relationship('Comment', backref='trip', lazy=True)

class ItineraryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(300))
    date = db.Column(db.String(50))
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    trip_id = db.Column(db.Integer)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    content = db.Column(db.String(500))
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))


# User APIs

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(name=data['name'], email=data['email'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{ "id": u.id, "name": u.name, "email": u.email } for u in users])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"id": user.id, "name": user.name, "email": user.email})

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    user = User.query.get_or_404(user_id)
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({"message": "User updated"})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})


# Trip APIs

@app.route('/trips', methods=['POST'])
def create_trip():
    data = request.json
    trip = Trip(**data)
    db.session.add(trip)
    db.session.commit()
    return jsonify({"id": trip.id}), 201

@app.route('/trips', methods=['GET'])
def get_trips():
    trips = Trip.query.all()
    return jsonify([{
        "id": t.id, "destination": t.destination,
        "start_date": t.start_date, "end_date": t.end_date,
        "travelers": t.travelers, "notes": t.notes, "user_id": t.user_id
    } for t in trips])

@app.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    t = Trip.query.get_or_404(trip_id)
    return jsonify({
        "id": t.id, "destination": t.destination,
        "start_date": t.start_date, "end_date": t.end_date,
        "travelers": t.travelers, "notes": t.notes, "user_id": t.user_id
    })

@app.route('/trips/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    data = request.json
    t = Trip.query.get_or_404(trip_id)
    for field in ['destination', 'start_date', 'end_date', 'travelers', 'notes', 'user_id']:
        if field in data:
            setattr(t, field, data[field])
    db.session.commit()
    return jsonify({"message": "Trip updated"})

@app.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    t = Trip.query.get_or_404(trip_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": "Trip deleted"})


# Itinerary APIs

@app.route('/trips/<int:trip_id>/items', methods=['POST'])
def add_itinerary_item(trip_id):
    data = request.json
    item = ItineraryItem(trip_id=trip_id, **data)
    db.session.add(item)
    db.session.commit()
    return jsonify({"id": item.id}), 201

@app.route('/trips/<int:trip_id>/items', methods=['GET'])
def get_itinerary_items(trip_id):
    items = ItineraryItem.query.filter_by(trip_id=trip_id).all()
    return jsonify([{ "id": i.id, "title": i.title, "description": i.description, "date": i.date } for i in items])

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    item = ItineraryItem.query.get_or_404(item_id)
    for field in ['title', 'description', 'date']:
        if field in data:
            setattr(item, field, data[field])
    db.session.commit()
    return jsonify({"message": "Item updated"})

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = ItineraryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"})


# Favorites APIs

@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    fav = Favorite(**data)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"id": fav.id}), 201

@app.route('/favorites/<int:user_id>', methods=['GET'])
def get_favorites(user_id):
    favs = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([{ "id": f.id, "trip_id": f.trip_id } for f in favs])

@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    fav = Favorite.query.get_or_404(favorite_id)
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite deleted"})


# Comments APIs

@app.route('/comments', methods=['POST'])
def add_comment():
    data = request.json
    c = Comment(**data)
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id}), 201

@app.route('/comments/<int:trip_id>', methods=['GET'])
def get_comments(trip_id):
    comments = Comment.query.filter_by(trip_id=trip_id).all()
    return jsonify([{ "id": c.id, "user_name": c.user_name, "content": c.content } for c in comments])

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    c = Comment.query.get_or_404(comment_id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Comment deleted"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
