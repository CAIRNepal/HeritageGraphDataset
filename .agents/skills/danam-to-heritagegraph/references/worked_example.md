# Worked example (Jogeśvara Mandira, SKH0510)

Two events and one object extracted from the English description. Note the citations copied exactly into `sources`,
`evidence_text` copied verbatim from `description_en`, era labels as written, and blank cells where the text is silent.
The DANAM page declares 18 events / 14 objects for this monument; the prose supports only some of them.

## events.csv
```csv
resource_id,monument_name,event_index,event_name,event_description,date_bce_ce,period,year_ss_ns_vs,nepali_month,paksha,tithi,sources,ontology_class,evidence_text,extraction_method,confidence
0077a8d9,Jogeśvara Mandira (before 608 CE),0,Dismantling of the two-tiered temple to build a śikhara-style temple,King Bhūpālendra Malla had the two-tiered temple dismantled and a door installed for constructing a śikhara-style (granthakūṭa) temple.,1689 CE,Malla,NS 809,Phālguna,Śukla,13,"(T. Siṃha1136, p. 15, folio 23A)",DestructionEvent,"On the 13th of the bright fortnight of Phālguna in 1689 CE (NS 809), King Bhūpālendra Malla got the two-tiered Temple dismantled and got a door installed for constructing aśikhara-style (granthakūṭa) temple (T. Siṃha1136, p. 15, folio 23A).",llm_from_description,high
0077a8d9,Jogeśvara Mandira (before 608 CE),1,Offering finial to rebuilt two-storied temple,The temple was rebuilt as a two-tiered temple and a finial was installed.,1727 CE,Malla,NS 847,Phālguna,Śukla,3,"(T. Siṃha1136, p. 28, folio 46A)",Production,"A few years later, the temple was again rebuilt as a two-tiered Temple and a finial was installed on the 3rd of the bright fortnight of Phālguna in 1727 CE (NS 847) (T. Siṃha1136, p. 28, folio 46A).",llm_from_description,high
```

## objects.csv
```csv
resource_id,monument_name,object_index,object_id,object_name,object_type,object_material,object_location,date_bce_ce,date_vs_ns,ontology_class,evidence_text,extraction_method,confidence
0077a8d9,Jogeśvara Mandira (before 608 CE),0,SKH0510-003,Toraṇa,Toraṇa,,,,,ArchitecturalElement,The toraṇa (SKH0510-003) was gilded.,llm_from_description,medium
```
