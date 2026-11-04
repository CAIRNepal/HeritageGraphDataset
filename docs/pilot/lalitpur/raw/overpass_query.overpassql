/* OSM heritage features inside Lalitpur District (relation 4583253, admin_level 6, wikidata Q1108338).
   Features: any historic=*, any heritage=*, amenity=place_of_worship, building=temple|shrine|stupa.
   Output: tags and a centre point for ways and relations; then the district boundary geometry (used to filter
   Wikidata items and DANAM monuments to the same area). */
[out:json][timeout:180];
area(id:3604583253)->.lal;
(
  nwr["historic"](area.lal);
  nwr["heritage"](area.lal);
  nwr["amenity"="place_of_worship"](area.lal);
  nwr["building"~"^(temple|shrine|stupa)$"](area.lal);
);
out center tags;
rel(4583253);
out geom;
