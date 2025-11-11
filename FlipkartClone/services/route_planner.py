import os
import json
import logging
from google import genai
from google.genai import types
from models import db, RoutePlan, RoutePlanStop
from services.geolocation import haversine_distance

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    client = genai.Client(api_key="AIzaSyCEJt7be1KEqyLsOLQHiXmTJF36DaaOKfY")
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    client = None


def optimize_shopping_route(user_id,
                            origin_lat,
                            origin_lng,
                            shopping_list,
                            destination_lat=None,
                            destination_lng=None):
    """
    Optimize shopping route using Gemini API
    shopping_list: list of dicts with {seller, product, distance_km}
    Returns optimized route plan
    """
    if not client:
        logger.error("Gemini client not initialized")
        return None

    if not shopping_list:
        return None

    request_data = {
        'origin': {
            'lat': origin_lat,
            'lng': origin_lng
        },
        'destination': {
            'lat': destination_lat,
            'lng': destination_lng
        } if destination_lat else None,
        'stops': []
    }

    for item in shopping_list:
        request_data['stops'].append({
            'seller_id':
            item['seller'].user_id,
            'seller_name':
            item['seller'].shop_name or item['seller'].full_name,
            'product_name':
            item['product'].name,
            'product_id':
            item['product'].product_id,
            'location': {
                'lat': item['seller'].shop_latitude,
                'lng': item['seller'].shop_longitude
            },
            'distance_from_origin':
            item['distance_km']
        })

    prompt = f"""You are a route optimization assistant. Given a shopping list with multiple store locations, 
optimize the route to minimize total travel distance.

Origin: ({origin_lat}, {origin_lng})
{f"Destination: ({destination_lat}, {destination_lng})" if destination_lat else "Return to origin"}

Shopping Stops:
{json.dumps(request_data['stops'], indent=2)}

Please provide an optimized route order that minimizes total travel distance. Consider:
1. Proximity to each other
2. Logical path from origin to destination
3. Avoiding backtracking

Respond with a JSON array of stop indices in the optimal order. For example: [2, 0, 3, 1]
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"))

        optimized_order = json.loads(response.text)

        route_plan = RoutePlan(user_id=user_id,
                               origin_lat=origin_lat,
                               origin_lng=origin_lng,
                               destination_lat=destination_lat,
                               destination_lng=destination_lng,
                               gemini_request=json.dumps(request_data),
                               gemini_response=response.text,
                               status='active')
        db.session.add(route_plan)
        db.session.flush()

        for order_idx, stop_idx in enumerate(optimized_order):
            if isinstance(stop_idx,
                          int) and 0 <= stop_idx < len(shopping_list):
                item = shopping_list[stop_idx]
                stop = RoutePlanStop(route_plan_id=route_plan.id,
                                     seller_id=item['seller'].user_id,
                                     product_id=item['product'].product_id,
                                     stop_order=order_idx + 1,
                                     shop_lat=item['seller'].shop_latitude,
                                     shop_lng=item['seller'].shop_longitude)
                db.session.add(stop)

        db.session.commit()

        return {
            'route_plan_id':
            route_plan.id,
            'optimized_order':
            optimized_order,
            'stops': [
                shopping_list[i] for i in optimized_order
                if isinstance(i, int) and 0 <= i < len(shopping_list)
            ]
        }

    except Exception as e:
        logger.error(f"Route optimization failed: {e}")
        db.session.rollback()
        return fallback_route_optimization(user_id, origin_lat, origin_lng,
                                           shopping_list, destination_lat,
                                           destination_lng)


def fallback_route_optimization(user_id,
                                origin_lat,
                                origin_lng,
                                shopping_list,
                                destination_lat=None,
                                destination_lng=None):
    """Simple nearest-neighbor route optimization when Gemini fails"""
    if not shopping_list:
        return None

    remaining = shopping_list.copy()
    optimized = []
    current_lat, current_lng = origin_lat, origin_lng

    while remaining:
        nearest = min(
            remaining,
            key=lambda x: haversine_distance(current_lat, current_lng, x[
                'seller'].shop_latitude, x['seller'].shop_longitude))
        optimized.append(nearest)
        remaining.remove(nearest)
        current_lat = nearest['seller'].shop_latitude
        current_lng = nearest['seller'].shop_longitude

    return {
        'route_plan_id': None,
        'optimized_order': list(range(len(optimized))),
        'stops': optimized,
        'fallback': True
    }


def get_route_plan(route_plan_id):
    """Retrieve a route plan with its stops"""
    route_plan = RoutePlan.query.get(route_plan_id)
    if not route_plan:
        return None

    stops = RoutePlanStop.query.filter_by(
        route_plan_id=route_plan_id).order_by(RoutePlanStop.stop_order).all()

    return {'route_plan': route_plan, 'stops': stops}
