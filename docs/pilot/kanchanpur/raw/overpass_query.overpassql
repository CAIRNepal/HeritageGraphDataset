/* OSM heritage features inside Kanchanpur District (relation 4586286, admin_level 6, wikidata Q28981).
   Same tags as the Lalitpur pilot: any historic=*, any heritage=*, amenity=place_of_worship,
   building=temple|shrine|stupa. Output: tags and a centre point for ways and relations; then the district
   boundary geometry (used to filter Wikidata items and DANAM monuments to the same area). */
[out:json][timeout:180];
area(id:3604586286)->.d;
(
  nwr["historic"](area.d);
  nwr["heritage"](area.d);
  nwr["amenity"="place_of_worship"](area.d);
  nwr["building"~"^(temple|shrine|stupa)$"](area.d);
);
out center tags;
rel(4586286);
out geom;
