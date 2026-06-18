# ALL CODE IN THIS FILE IS AI-GENERATED
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

# https://github.com/evansd/uk-ceremonial-counties/blob/master/uk-ceremonial-counties.geojson
_GEOJSON_PATH = Path(__file__).resolve().parent / "client" / "uk-counties.geojson"


def _point_on_segment(lon: float, lat: float, start: list[float], end: list[float]) -> bool:
	start_lon, start_lat = start
	end_lon, end_lat = end

	cross = (lon - start_lon) * (end_lat - start_lat) - (lat - start_lat) * (end_lon - start_lon)
	if abs(cross) > 1e-12:
		return False

	return (
		min(start_lon, end_lon) - 1e-12 <= lon <= max(start_lon, end_lon) + 1e-12
		and min(start_lat, end_lat) - 1e-12 <= lat <= max(start_lat, end_lat) + 1e-12
	)


def _point_in_ring(lon: float, lat: float, ring: list[list[float]]) -> bool:
	if len(ring) < 3:
		return False

	inside = False
	previous = ring[-1]
	for current in ring:
		if _point_on_segment(lon, lat, previous, current):
			return True

		prev_lon, prev_lat = previous
		curr_lon, curr_lat = current
		intersects = ((curr_lat > lat) != (prev_lat > lat)) and (
			lon < (prev_lon - curr_lon) * (lat - curr_lat) / (prev_lat - curr_lat) + curr_lon
		)
		if intersects:
			inside = not inside

		previous = current

	return inside


def _point_in_polygon(lon: float, lat: float, polygon: list[list[list[float]]]) -> bool:
	if not polygon:
		return False

	if not _point_in_ring(lon, lat, polygon[0]):
		return False

	for hole in polygon[1:]:
		if _point_in_ring(lon, lat, hole):
			return False

	return True


def _segment_distance_sq(lon: float, lat: float, start: list[float], end: list[float]) -> float:
	lon_scale = math.cos(math.radians(lat))
	point_x = lon * lon_scale
	point_y = lat
	start_x = start[0] * lon_scale
	start_y = start[1]
	end_x = end[0] * lon_scale
	end_y = end[1]

	segment_dx = end_x - start_x
	segment_dy = end_y - start_y
	if segment_dx == 0 and segment_dy == 0:
		dx = point_x - start_x
		dy = point_y - start_y
		return dx * dx + dy * dy

	projection = ((point_x - start_x) * segment_dx + (point_y - start_y) * segment_dy) / (
		segment_dx * segment_dx + segment_dy * segment_dy
	)
	projection = max(0.0, min(1.0, projection))
	closest_x = start_x + projection * segment_dx
	closest_y = start_y + projection * segment_dy
	dx = point_x - closest_x
	dy = point_y - closest_y
	return dx * dx + dy * dy


def _ring_distance_sq(lon: float, lat: float, ring: list[list[float]]) -> float:
	if len(ring) < 2:
		return float("inf")

	minimum = float("inf")
	previous = ring[-1]
	for current in ring:
		minimum = min(minimum, _segment_distance_sq(lon, lat, previous, current))
		previous = current

	return minimum


def _polygon_distance_sq(lon: float, lat: float, polygon: list[list[list[float]]]) -> float:
	if not polygon:
		return float("inf")

	minimum = _ring_distance_sq(lon, lat, polygon[0])
	for ring in polygon[1:]:
		minimum = min(minimum, _ring_distance_sq(lon, lat, ring))

	return minimum


def _feature_distance_sq(lon: float, lat: float, feature: dict[str, object]) -> float:
	geometry = feature.get("geometry") or {}
	geometry_type = geometry.get("type")
	coordinates = geometry.get("coordinates") or []

	if geometry_type == "Polygon":
		return _polygon_distance_sq(lon, lat, coordinates)
	if geometry_type == "MultiPolygon":
		return min((_polygon_distance_sq(lon, lat, polygon) for polygon in coordinates), default=float("inf"))

	return float("inf")


@lru_cache(maxsize=1)
def _load_counties() -> list[dict[str, object]]:
	with _GEOJSON_PATH.open("r", encoding="utf-8") as file:
		data = json.load(file)
	return data["features"]


def _county_name(feature: dict[str, object]) -> str | None:
	properties = feature.get("properties") or {}
	county = properties.get("county")
	if county:
		return county
	return None


def get_county_from_coordinates(latitude: float, longitude: float) -> str | None:
	"""Return the ceremonial county containing the given UK latitude/longitude point.

	The lookup uses only the bundled ceremonial county GeoJSON.
	If the point does not fall cleanly inside a polygon, the nearest county is returned.
	"""

	lon = float(longitude)
	lat = float(latitude)
	nearest_county = None
	nearest_distance = float("inf")

	for feature in _load_counties():
		geometry = feature.get("geometry") or {}
		geometry_type = geometry.get("type")
		coordinates = geometry.get("coordinates") or []
		county_name = _county_name(feature)
		if not county_name:
			continue

		distance = _feature_distance_sq(lon, lat, feature)
		if distance < nearest_distance:
			nearest_distance = distance
			nearest_county = county_name

		if geometry_type == "Polygon":
			if _point_in_polygon(lon, lat, coordinates):
				return county_name
		elif geometry_type == "MultiPolygon":
			for polygon in coordinates:
				if _point_in_polygon(lon, lat, polygon):
					return county_name

	return nearest_county


if __name__ == "__main__":
	sample_latitude, sample_longitude =54.88531379987, -4.647844907173905
	print(get_county_from_coordinates(sample_latitude, sample_longitude))
