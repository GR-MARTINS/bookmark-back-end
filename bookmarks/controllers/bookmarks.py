import validators
from flask import (
    Blueprint,
    request,
    jsonify
)
from flasgger import swag_from
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)
from bookmarks.constants import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_406_NOT_ACCEPTABLE
)

from bookmarks.ext.sqlalchemy import db
from bookmarks.models.tables.bookmarks import Bookmark
from bookmarks.models.tables.visits import Visit
from bookmarks.controllers.stats import (
    monthly_stats,
    weekly_stats,
    last_days_stats
)

bookmarks = Blueprint("bookmaks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.post('/')
@jwt_required()
@swag_from('../docs/bookmarks/create.yaml')
def create():
    current_user = get_jwt_identity()

    if request.method == 'POST':

        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'error': 'Enter a valid URL! example: "http://www.yoursite.com"'
            }), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exists'
            }), HTTP_400_BAD_REQUEST

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'create_at': bookmark.create_at,
            'updated_at': bookmark.updated_at
        }), HTTP_201_CREATED


@bookmarks.get('/')
@bookmarks.get('/<int:id>')
@jwt_required()
def get(id=None):

    current_user = get_jwt_identity()

    if id:

        bookmark = Bookmark.query.filter_by(
            user_id=current_user,
            id=id
        ).first()

        if not bookmark:

            return jsonify({
                'message': 'Item not found'
            }), HTTP_406_NOT_ACCEPTABLE

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'create_at': bookmark.create_at,
            'updated_at': bookmark.updated_at
        }), HTTP_200_OK

    else:

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        bookmarks = Bookmark.query.filter_by(
            user_id=current_user
        ).order_by(Bookmark.id).paginate(page=page, per_page=per_page)

        data = []

        for bookmark in bookmarks.items:

            data.append({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visit': bookmark.visits,
                'body': bookmark.body,
                'create_at': bookmark.create_at,
                'updated_at': bookmark.updated_at
            })

        meta = {
            'page': bookmarks.page,
            'pages': bookmarks.pages,
            'total_count': bookmarks.total,
            'prev_page': bookmarks.prev_num,
            'next_page': bookmarks.next_num,
            'has_next': bookmarks.has_next,
            'has_prev': bookmarks.has_prev
        }

        return jsonify({
            'data': data, 'meta': meta
        }), HTTP_200_OK


@bookmarks.put('/<int:id>')
@jwt_required()
def update(id):

    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(
        user_id=current_user,
        id=id
    ).first()

    if not bookmark:
        return jsonify({
            'message': 'Item not found'
        }), HTTP_406_NOT_ACCEPTABLE

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
            'error': 'Enter a valid URL'
        }), HTTP_400_BAD_REQUEST

    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'create_at': bookmark.create_at,
        'updated_at': bookmark.updated_at
    }), HTTP_200_OK


@bookmarks.delete('/<int:id>')
@jwt_required()
def delete(id):

    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(
        user_id=current_user,
        id=id
    ).first()

    if not bookmark:
        return jsonify({
            'message': 'Item not found'
        }), HTTP_406_NOT_ACCEPTABLE

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@bookmarks.get('/stats')
@jwt_required()
@swag_from('../docs/bookmarks/stats.yaml')
def get_all_stats():
    current_user = get_jwt_identity()
    data = []
    items = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        visits = Visit.query.filter_by(bookmark_id=item.id).all()
        visit_data = []
        for visit in visits:
            visit_data.append(visit.visiting_hours)
        new_link = {
            'total_clicks': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url,
            'visits': visit_data
        }
        data.append(new_link)

    return jsonify({
        'data': data
    }), HTTP_200_OK


@bookmarks.get('/stats/<id>')
def get_one_stats(id=None):
    months_data, months_label = monthly_stats(5, id)
    weeks_data, weeks_label = weekly_stats(id)
    last_7_days_data, last_7_days_label = last_days_stats(7, id)
    last_30_days_data, last_30_days_label = last_days_stats(30, id)
    return jsonify(
        {
            "monthly_stats": {
                "data": months_data,
                "label": months_label
            },
            "weekly_stats": {
                "data": weeks_data,
                "label": weeks_label
            },
            "last_7_days": {
                "data": last_7_days_data,
                "label": last_7_days_label
            },
            "last_30_days": {
                "data": last_30_days_data,
                "label": last_30_days_label
            },
        }
    ), HTTP_200_OK
