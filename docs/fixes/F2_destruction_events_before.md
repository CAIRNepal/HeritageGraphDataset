# F2: the 695 events typed crm:E6_Destruction (before the fix)

All 5,098 events are typed by `classify_event` in build_kg.py (DANAM's export has no event class). The rules are tried in order: consecration, enshrinement, then **destruction**: the event name or description contains a word starting with `dismantl|collaps|burnt|burn|demolish|destroy|earthquake|flood|fire|damage`. An event lands here when none of the earlier rules matched. Grouped by the first destruction keyword found in the text. 'Renov.' = the text also has a renovation word (renovat, restor, rebuil, reconstruct, repair, refurbish, reinstall, replac). 'In name' = the keyword is in the event name.

| Keyword | Events | Also renovation | Keyword in name |
|---|---:|---:|---:|
| damage | 285 | 140 | 136 |
| earthquake | 152 | 119 | 48 |
| collaps | 112 | 64 | 54 |
| dismantl | 68 | 59 | 5 |
| fire | 43 | 13 | 5 |
| demolish | 19 | 15 | 4 |
| destroy | 13 | 9 | 1 |
| flood | 2 | 0 | 1 |
| burn | 1 | 0 | 0 |
| **all** | **695** | **419** | **254** |

## `damage` (285)

| # | Event name | Renov. | Words matched | Event |
|---:|---|:-:|---|---|
| 1 | Agreement between China and Nepal | yes | damaged, earthquake | 02f204ae_6 |
| 2 | Agreement between China and Nepal | yes | damaged, earthquake | f2fd559b_3 |
| 3 | Construction of Caitya | yes | damaged | a0a959a5_0 |
| 4 | Construction of Jitāpura Gaṃcā | yes | damage | 57c22b4c_0 |
| 5 | Construction of Thaṃthu Durbar | yes | damaged | b7024813_0 |
| 6 | Damage by earthquake | yes | collapsed, damage, earthquake, earthquakes | 0826415c_7 |
| 7 | Damage by earthquake | yes | collapsed, damage, earthquake, earthquakes | 0d443923_0 |
| 8 | Damage by earthquake | yes | collapsed, damage, earthquake | 20787244_4 |
| 9 | Damage by earthquake | yes | collapse, damage, damaged, earthquake, earthquakes | 27fefdad_7 |
| 10 | Damage by earthquake | yes | damage, earthquake, earthquakes | 5ae13e80_2 |
| 11 | Damage by earthquake | yes | collapse, damage, earthquake | 61056d43_10 |
| 12 | Damage by earthquake | yes | damage, earthquake, earthquakes | 7a82b1a5_0 |
| 13 | Damage by earthquake | yes | damage, damaged, demolished, earthquake | 89c37d61_10 |
| 14 | Damage by earthquake | yes | damage, damaged, earthquake | 89c9360f_9 |
| 15 | Damage by earthquake | yes | damage, earthquake, earthquakes | 8b2107e2_1 |
| 16 | Damage by earthquake | yes | damage, destroyed, earthquake, earthquakes | 8f639858_6 |
| 17 | Damage by earthquake | yes | damage, damaged, earthquake | 989f4dde_3 |
| 18 | Damage by earthquake | yes | collapse, damage, damaged, earthquake | 9d5039d0_5 |
| 19 | Damage by earthquake | yes | damage, damaged, earthquake, earthquakes | bee5d202_1 |
| 20 | Damage by earthquake | yes | damage, damaged, earthquake, earthquakes | c0754b90_3 |
| 21 | Damage by earthquake | yes | damage, destroyed, earthquake, earthquakes | d8892589_0 |
| 22 | Damage by earthquake | yes | damage, earthquake, earthquakes | e77be04f_9 |
| 23 | Damage by earthquake | yes | collapse, damage, earthquake, earthquakes | f5fd9fa9_0 |
| 24 | Damage caused by earthquakes | yes | damage, earthquakes | c82f05dc_1 |
| 25 | Damage caused by the 1934 CE earthquake and rebuilding | yes | collapse, damage, earthquake, earthquakes | 28cc6491_1 |
| 26 | Damage during the 1934 CE earthquakes and repair | yes | damage, damaged, earthquakes | 4b3adb40_1 |
| 27 | Damage during the 2015 CE earthquakes | yes | damage, earthquakes | 4b3adb40_2 |
| 28 | Damage in earthquake and reconstruction | yes | damage, earthquake | c764be19_1 |
| 29 | Damage suffered by the 2015 earthquakes | yes | collapse, damage, damaged, earthquakes | e333b4f4_2 |
| 30 | Damage suffered from the earthquakes | yes | collapse, damage, damaged, dismantled, earthquakes | 08e7bdc5_2 |
| 31 | Damage suffered from the earthquakes | yes | damage, damaged, earthquakes | 37637b5c_1 |
| 32 | Damage suffered from the earthquakes | yes | damage, earthquakes | 9f7e7e0a_3 |
| 33 | Damage suffered from the earthquakes (A) | yes | damage, damaged, destroyed, earthquake, earthquakes | 1b0a5033_2 |
| 34 | Damage suffered from the earthquakes and renovation | yes | damage, damaged, earthquakes | 1394f154_0 |
| 35 | Damaged in earthquakes | yes | damaged, earthquakes | c07ed9a8_2 |
| 36 | Damaged in the 2015 earthquakes | yes | damaged, earthquake, earthquakes | f8a657a5_1 |
| 37 | Damages during the earthquakes | yes | collapse, damaged, damages, earthquakes | cc222dfb_0 |
| 38 | Damages from the 1934 earthquakes and renovation | yes | collapsed, damages, earthquakes | 08e7bdc5_0 |
| 39 | Damages to the roof and renovation | yes | damages | 08e7bdc5_1 |
| 40 | Demolition and reconstruction | yes | damaged, earthquakes | b23905f8_1 |
| 41 | Destruction and rebuilt | yes | damaged, earthquake | d13507a3_2 |
| 42 | Endowment of lands | yes | damage | d86c93ef_1 |
| 43 | Historical event NS 907 | yes | damages | 48fbbcba_3 |
| 44 | Laying of foundation stone | yes | damage, floods | 91ae947b_4 |
| 45 | Loss of the historic building | yes | damaged, demolished, earthquake | 972f5123_2 |
| 46 | Minor reparations | yes | damaged | 1165bb2e_2 |
| 47 | Monument damage caused by earthquake | yes | collapsed, damage, earthquake | 71d1fd85_1 |
| 48 | Offering a new bell | yes | damaged | ed6d9432_6 |
| 49 | Offering of musical instrument | yes | damaged | 2af3fc6d_3 |
| 50 | Politically motivated damage of the Phalcā | yes | damage, damaged | 4abcfc57_0 |
| 51 | Rebuilding | yes | damaged, earthquakes | 5f7c8a35_2 |
| 52 | Rebuilding | yes | damages, earthquakes | 72d27f5f_0 |
| 53 | Rebuilding the Temple | yes | damages, earthquakes | 01c33990_3 |
| 54 | Rebuilding the Temple in its Original Style | yes | damaged | 23d40c88_2 |
| 55 | Rebuilt of the temple | yes | damaged, earthquake | 6da9c621_1 |
| 56 | Reconstruction | yes | damaged, earthquakes | 04ae4cd7_0 |
| 57 | Reconstruction | yes | damaged, earthquakes | 0ce126ea_1 |
| 58 | Reconstruction | yes | damage, earthquakes | 0f14007d_5 |
| 59 | Reconstruction | yes | damaged, dismantled, earthquake | 0ff1a49f_0 |
| 60 | Reconstruction | yes | damages, earthquakes | 154297b7_4 |
| 61 | Reconstruction | yes | damaged, earthquakes | 26d29a66_2 |
| 62 | Reconstruction | yes | damage, earthquake | 57c22b4c_1 |
| 63 | Reconstruction | yes | damaged, dismantled, earthquakes | 9808e800_1 |
| 64 | Reconstruction | yes | damage | a4df4e50_2 |
| 65 | Reconstruction | yes | damaged, earthquakes | e6c73144_2 |
| 66 | Reconstruction of Vihara | yes | damage, demolished, earthquake | ced28492_1 |
| 67 | Reconstruction of pura | yes | damaged | 5f218d0a_7 |
| 68 | Reconstruction of the Bahī | yes | damages, earthquakes | d46efa17_4 |
| 69 | Reconstruction of the Phalcā | yes | damaged, earthquakes | 786fe3c9_3 |
| 70 | Reconstruction of the Vatsalā Temple | yes | damaged, earthquake | 937ecfa8_3 |
| 71 | Reconstruction of the bāhāḥ | yes | damage, earthquakes | 1b57a5f0_1 |
| 72 | Reconstruction of the bāhāḥ | yes | damaged, earthquake | c3ab5e57_2 |
| 73 | Reconstruction of the monument | yes | damaged, earthquakes | 06151b6a_2 |
| 74 | Reconstruction of the monument | yes | damaged, earthquake | 511d9122_1 |
| 75 | Reconstruction of the monument | yes | damaged, earthquake | a0c8744f_2 |
| 76 | Reconstruction of the monument (?) | yes | damage, earthquake | c76fb177_3 |
| 77 | Reconstruction of the phalcā | yes | damaged, demolished | 911c76c5_4 |
| 78 | Reconstruction of the shrine (KAT2360-005) | yes | collapse, damage, earthquake | ad08a0da_1 |
| 79 | Reconstruction of the temple | yes | damage, earthquakes | 13ab842a_4 |
| 80 | Reconstruction of the temple | yes | damages, dismantling, earthquakes | 2b614d26_4 |
| 81 | Reconstruction of the temple | yes | damaged, earthquakes | cdfdf1b3_1 |
| 82 | Reconstruction of the temple | yes | damaged | d509cc77_2 |
| 83 | Reconstruction of the temple | yes | damaged, earthquake | d86c93ef_6 |
| 84 | Reconstruction of the temple of Aśoka Caitya | yes | damaged, earthquakes | 22b12b9b_11 |
| 85 | Reinstallation of a damaged inscription | yes | damaged, destroyed | 1347d2d6_6 |
| 86 | Renovation | yes | damaged, earthquakes | 1860577b_0 |
| 87 | Renovation | yes | damage, earthquakes | 20b36bbb_1 |
| 88 | Renovation | yes | damaged, earthquakes | 353e0ee9_1 |
| 89 | Renovation | yes | damaged, earthquakes | 5111af39_1 |
| 90 | Renovation | yes | damage, earthquake | 57a467a3_3 |
| 91 | Renovation | yes | damage, earthquakes | 7b46dfdf_3 |
| 92 | Renovation | yes | damage, earthquakes | 8030a639_0 |
| 93 | Renovation | yes | damaged, earthquakes | 89c68953_3 |
| 94 | Renovation | yes | damaged | 8f92f98f_1 |
| 95 | Renovation | yes | damaged, earthquakes | a3a846d8_1 |
| 96 | Renovation | yes | damaged, earthquakes | a5b781d7_2 |
| 97 | Renovation | yes | damaged, earthquakes | b0d9a9f0_1 |
| 98 | Renovation | yes | damaged | d538ba1e_0 |
| 99 | Renovation | yes | damaged, earthquake | df484d8d_2 |
| 100 | Renovation | yes | damages, earthquakes | e29f9e62_0 |
| 101 | Renovation | yes | damaged, earthquake | f142c371_2 |
| 102 | Renovation (B) | yes | damages, earthquakes | ed73a567_1 |
| 103 | Renovation of Hitigāḥcā | yes | damages, earthquakes | e78429eb_1 |
| 104 | Renovation of Khapiṁchẽ Phalcā (now lost) | yes | damage | b8b26a0c_0 |
| 105 | Renovation of Temple | yes | damages, earthquakes | 95211cfa_2 |
| 106 | Renovation of bell | yes | damages, earthquakes | ee6be98a_2 |
| 107 | Renovation of the Bāhāḥ | yes | damaged, earthquake | c232bdac_11 |
| 108 | Renovation of the Sataḥ’s northern wall | yes | damaged, earthquakes | b6c6ae2c_1 |
| 109 | Renovation of the bridge | yes | damaged | b8f4c2b9_2 |
| 110 | Renovation of the bāhāḥ | yes | damaged, earthquake | bbb0b3d2_2 |
| 111 | Renovation of the jaḥdhuṃ | yes | damages | ddcff119_0 |
| 112 | Renovation of the monument | yes | damaged, earthquakes | 2b614d26_3 |
| 113 | Renovation of the monument | yes | damaged | 62468f09_1 |
| 114 | Renovation of the monument | yes | damaged, earthquakes | 64a2bcf3_0 |
| 115 | Renovation of the monument | yes | damage, earthquake | ad08a0da_0 |
| 116 | Renovation of the temple | yes | damaged | 3db42996_4 |
| 117 | Renovation of the Śikharakūṭa Caitya and establishment of Gaṇeśa and Mahākāla | yes | damaged | c3ab5e57_1 |
| 118 | Renovation of the śivālaya | yes | damage, earthquakes | b66dd221_4 |
| 119 | Repair of Aśoka Caitya | yes | damaged | 20787244_1 |
| 120 | Repair of Walls | yes | damaged, earthquakes | 5cb98dcd_6 |
| 121 | Repair of the Shrine | yes | damages, earthquakes | f7ee7e3d_1 |
| 122 | Repair of the bell | yes | damaged | 5486b15f_7 |
| 123 | Repair of the roof | yes | damaged, earthquakes | d472f57f_1 |
| 124 | Repair of the temple | yes | damaged | 989f4dde_2 |
| 125 | Repair of the temple | yes | damage, earthquake | e277eff9_11 |
| 126 | Repair of the śivālaya | yes | damaged, earthquakes | 561d9a2f_1 |
| 127 | Repair of vihāra | yes | damage | 9d5039d0_4 |
| 128 | Replacement of pillars | yes | damaged | a0c8744f_1 |
| 129 | Replacing clay statue with stone one | yes | damaged | fdb69fc2_0 |
| 130 | Restoration | yes | damage, earthquakes | 05ed8b92_3 |
| 131 | Restoration of the Phalcā | yes | damaged, earthquakes | 1db95433_1 |
| 132 | Restoration of the phalcā | yes | damaged, earthquakes | 75693640_1 |
| 133 | Restoration of the temple | yes | damaged, earthquake | c566021c_0 |
| 134 | Restoration of the temple | yes | damage, earthquakes | f96c7cf2_4 |
| 135 | Restoration of the śivālaya | yes | damaged, earthquakes | 83a32702_1 |
| 136 | Restoring the supply of water to the spout | yes | damaged | eb39f614_1 |
| 137 | Second reconstruction of the phalcā | yes | damage, dismantled, earthquakes | af614ba6_3 |
| 138 | Slight damage | yes | damage, damaged, earthquakes | 170a68d0_1 |
| 139 | Structural damage due to earthquake | yes | damage, damages, dismantled, earthquake, earthquakes | 9808e800_0 |
| 140 | Suffered damages by the 2015 earthquakes and renovation | yes | damages, earthquakes | 204170f8_12 |
| 141 | Construction of temple |  | damaged | 3331db72_2 |
| 142 | Damage During the 2015 CE Earthquakes |  | damage, damaged, earthquakes | e73fb90e_0 |
| 143 | Damage During the Earthquakes |  | damage, damaged, earthquake, earthquakes | 5cb98dcd_5 |
| 144 | Damage Suffered from the 2015 CE Earthquakes |  | damage, damaged, earthquakes | b7adbd29_0 |
| 145 | Damage Suffered from the Earthquakes |  | damage, damaged, earthquakes | 4405bb30_0 |
| 146 | Damage as a result ofroad traffic |  | damage | 55bee51e_1 |
| 147 | Damage by 2015 CE earthquakes |  | damage, earthquake, earthquakes | 26f8c123_0 |
| 148 | Damage by 2015 earthquakes |  | damage, damaged, earthquake, earthquakes | 2298db0e_1 |
| 149 | Damage by Fire |  | damage, fire | 7f398f5a_14 |
| 150 | Damage by earthquake |  | collapse, damage, damages, earthquake, earthquakes | 0077a8d9_16 |
| 151 | Damage by earthquake |  | collapse, damage, earthquake | 02f204ae_4 |
| 152 | Damage by earthquake |  | damage, damaged, earthquake, earthquakes | 03774891_2 |
| 153 | Damage by earthquake |  | damage, earthquake, earthquakes | 22b12b9b_10 |
| 154 | Damage by earthquake |  | damage, earthquake, earthquakes | 2e39f1d1_2 |
| 155 | Damage by earthquake |  | damage, earthquake, earthquakes | 313ebade_11 |
| 156 | Damage by earthquake |  | collapse, damage, damaged, earthquake, earthquakes | 3fa0b2f5_14 |
| 157 | Damage by earthquake |  | damage, damaged, earthquake | 44609e5a_4 |
| 158 | Damage by earthquake |  | collapse, damage, earthquake, earthquakes | 5ae13e80_3 |
| 159 | Damage by earthquake |  | damage, earthquake | 5d9c1eae_22 |
| 160 | Damage by earthquake |  | damage, damaged, demolished, earthquake, earthquakes | 60bd57eb_1 |
| 161 | Damage by earthquake |  | collapsed, damage, earthquake | 75171568_1 |
| 162 | Damage by earthquake |  | collapsed, damage, earthquake | 75171568_5 |
| 163 | Damage by earthquake |  | collapse, damage, earthquake, earthquakes | 7f65c791_10 |
| 164 | Damage by earthquake |  | damage, damaged, earthquake, earthquakes | 89c9360f_5 |
| 165 | Damage by earthquake |  | damage, damaged, demolished, earthquake, earthquakes | 8f639858_10 |
| 166 | Damage by earthquake |  | damage, damaged, earthquake, earthquakes | 94df40ea_0 |
| 167 | Damage by earthquake |  | damage, earthquake, earthquakes | 97276b3d_1 |
| 168 | Damage by earthquake |  | collapsed, damage, earthquake | 990ceb20_2 |
| 169 | Damage by earthquake |  | damage, damages, earthquake, earthquakes | a46b0595_2 |
| 170 | Damage by earthquake |  | collapse, damage, earthquake | ac2862e2_0 |
| 171 | Damage by earthquake |  | damage, damaged, earthquake | aefd4c30_0 |
| 172 | Damage by earthquake |  | collapse, collapsed, damage, damaged, earthquake, earthquakes | bf182f12_1 |
| 173 | Damage by earthquake |  | collapse, damage, earthquake, earthquakes | f5a48d0e_29 |
| 174 | Damage by earthquakes |  | damage, earthquakes | 051a3dc8_9 |
| 175 | Damage by earthquakes |  | damage, earthquakes | 2a5fe4da_11 |
| 176 | Damage by earthquakes |  | damage, damaged, earthquakes | 2ac12f52_0 |
| 177 | Damage by earthquakes |  | collapsed, damage, earthquakes | a2680407_0 |
| 178 | Damage by the 2015 earthquake |  | damage, damages, earthquake, earthquakes | 01c33990_1 |
| 179 | Damage by the 2015 earthquakes |  | damage, earthquakes | 13ab842a_3 |
| 180 | Damage by the 2015 earthquakes |  | collapsed, damage, earthquakes | 5607a0f1_1 |
| 181 | Damage by the 2015 earthquakes |  | collapsed, damage, earthquakes | 5ed91e74_1 |
| 182 | Damage caused by the earthquakes |  | damage, earthquakes | 1db95433_0 |
| 183 | Damage during the 2015 earthquakes |  | damage, damages, earthquakes | ae58c406_7 |
| 184 | Damage from the 1834 earthquakes |  | damage, damaged, earthquakes | 24afe176_22 |
| 185 | Damage from the earthquakes |  | damage, earthquake, earthquakes | 6da9c621_0 |
| 186 | Damage in 1934 earthquakes |  | damage, damaged, earthquakes | eec66042_1 |
| 187 | Damage in 1934 earthquakes |  | damage, damaged, earthquakes | f25241a7_1 |
| 188 | Damage in 2015 earthquakes |  | damage, earthquakes | 0a006229_19 |
| 189 | Damage in 2015 earthquakes |  | damage, earthquakes | eec66042_3 |
| 190 | Damage in 2015 earthquakes |  | damage, earthquakes | f25241a7_3 |
| 191 | Damage in the earthquake |  | damage, earthquake, earthquakes | a2cfeca7_1 |
| 192 | Damage of the 1934 CE Earthquakes |  | damage, damages, earthquakes | 443544db_5 |
| 193 | Damage of the 2015 CE Earthquakes |  | damage, damaged, earthquakes | e24051bb_2 |
| 194 | Damage of the Pinnacle |  | damage, damaged | 5790999f_10 |
| 195 | Damage of the temple |  | damage, damaged, earthquake | c79cc000_3 |
| 196 | Damage suffered |  | damage | 59d6dc2c_0 |
| 197 | Damage suffered during earthquake |  | damage, damaged, earthquake, earthquakes | f8366c56_2 |
| 198 | Damage suffered during the 2015 earthquake |  | damage, earthquake | 74ae042c_2 |
| 199 | Damage suffered from the 2015 earthquakes |  | damage, damaged, earthquakes | 48fbbcba_15 |
| 200 | Damage suffered from the 2015 earthquakes |  | damage, damaged, earthquakes | 9e929afa_4 |
| 201 | Damage suffered from the earthquakes |  | damage, earthquakes | 1e15e17c_0 |
| 202 | Damage suffered from the earthquakes |  | damage, earthquakes | 599606e0_0 |
| 203 | Damage suffered from the earthquakes |  | damage, damaged, earthquakes | 68934505_0 |
| 204 | Damage suffered from the earthquakes |  | damage, damaged, earthquakes | 75693640_0 |
| 205 | Damage suffered from the earthquakes |  | damage, damaged, earthquakes | 77b88f79_3 |
| 206 | Damage suffered from the earthquakes |  | damage, damages, earthquakes | 8ad6f527_0 |
| 207 | Damage suffered from the earthquakes |  | damage, damaged, earthquakes | 8ad6f527_5 |
| 208 | Damage suffered from the earthquakes |  | damage, earthquakes | 8e51f3df_0 |
| 209 | Damage suffered from the earthquakes |  | damage, earthquakes | 98358087_3 |
| 210 | Damage suffered from the earthquakes |  | damage, damaged, earthquakes | a0771bce_6 |
| 211 | Damage suffered from the earthquakes |  | damage, damaged, earthquakes | b088faf0_1 |
| 212 | Damage suffered from the earthquakes |  | damage, damaged, earthquakes | ece92710_4 |
| 213 | Damage suffered from the earthquakes (B) |  | damage, damaged, earthquakes | 1b0a5033_0 |
| 214 | Damaged by Earthquakes |  | damaged, earthquakes | 938935b2_0 |
| 215 | Damaged by earthquakes |  | damaged, earthquakes | cc076a1e_2 |
| 216 | Damaged by the earthquake |  | damaged, earthquake | 62468f09_0 |
| 217 | Damaged during earthquake |  | damaged, earthquake, earthquakes | 3167408a_2 |
| 218 | Damaged during the 2015 earthquakes |  | damaged, earthquakes | 786fe3c9_2 |
| 219 | Damaged in 2015 earthquake |  | damaged, earthquake | 09cff614_1 |
| 220 | Damaged in the 2015 earthquake |  | damaged, earthquake | 493f8e80_0 |
| 221 | Damaged in the 2015 earthquakes |  | damaged, earthquakes | f142c371_3 |
| 222 | Damaged inscription |  | damaged | 95de5b2e_0 |
| 223 | Damages by earthquakes |  | collapse, damaged, damages, earthquakes | 8615d9f8_0 |
| 224 | Damages caused by the 2015 earthquakes |  | damaged, damages, earthquakes | f6f28540_2 |
| 225 | Damages during the 2015 earthquakes |  | damaged, damages, earthquakes | 25c65422_7 |
| 226 | Damages during the earthquakes |  | damages, earthquakes | 0d31ecbb_0 |
| 227 | Damages from the 2015 earthquakes |  | damaged, damages, earthquakes | 762a6cae_1 |
| 228 | Damages from the 2015 earthquakes |  | damages, earthquakes | fa6d89bc_0 |
| 229 | Damages from the earthquakes |  | damaged, damages, earthquakes | 25c2dcdd_0 |
| 230 | Damages from the earthquakes |  | damaged, damages, earthquakes | 85fe0c4b_0 |
| 231 | Damages in the 2015 earthquakes |  | damaged, damages, earthquakes | 38b263ba_2 |
| 232 | Damages of the 1934 CE Earthquake |  | damaged, damages, earthquake, earthquakes | 13b406e0_2 |
| 233 | Damages of the 2015 CE Earthquakes |  | damages, earthquakes | 13b406e0_4 |
| 234 | Damages to the Phalcā due to the 2015 earthquakes |  | damages, earthquakes | ae69ba5f_0 |
| 235 | Destruction of temple |  | damaged, earthquake | 5277a9d6_1 |
| 236 | Donation of a bell |  | damaged | 788cd320_3 |
| 237 | Donation of a new Gaṇeśa statue |  | damaged | e333b4f4_0 |
| 238 | Donation of finial, flag and umbrella |  | damaged | 93b01588_3 |
| 239 | Donation of golden pinnacle |  | damaged | 557a604c_2 |
| 240 | Donation of the statue of devotees |  | damaged | 4a025a42_1 |
| 241 | Endowment of lands |  | damaged, fire | 32b21dd4_1 |
| 242 | Erection of a stone pillar |  | damages | 8f5e6a23_1 |
| 243 | Establishment of Ratna Caitya |  | damage | 54b62ce2_0 |
| 244 | Establishment of a śikharakūṭa caitya |  | damagedaśoka | 711b19a4_18 |
| 245 | Establishment of Śivapūjeśvara (PPK0610-012) |  | damaged | 27fefdad_0 |
| 246 | Fixing of an iron grill |  | damage | 0b6871b6_2 |
| 247 | Formation of a Guṭhī |  | damaged | 143b3eaf_0 |
| 248 | Initial Construction of Htigāḥcā, Śiva Mandira, and Phalcā, and Establishment of a Guṭhī |  | damaged | e78429eb_0 |
| 249 | Initial Construction of the Temple, Hiti, and Phalcā, and Establishment of a Guṭhī |  | damaged | e24051bb_0 |
| 250 | Initial construction |  | damaged | a2cfeca7_0 |
| 251 | Initial construction of the temple |  | damaged | 3e718754_0 |
| 252 | Inscription Issued by Licchavi King Aṃśu Varman |  | damage | cbae4fa5_4 |
| 253 | Installation of a statue |  | damage | 89c37d61_8 |
| 254 | Land endowment |  | damaged | 9d4436ef_0 |
| 255 | Offering of a bell |  | damaged | 5d9e8143_4 |
| 256 | Offering of a bell |  | damaged | cdf3de81_4 |
| 257 | Offering of a lion (siṃha) and a banner (dhvaja) |  | damaged | cdf3de81_0 |
| 258 | Offering of oil lamp stand |  | damaged | b071cb98_2 |
| 259 | Stabilisation of the temple |  | damage, earthquake | 3b68c5ca_13 |
| 260 | Suffered damage by the earthquakes |  | damage, damaged, earthquakes | 83e736d7_0 |
| 261 | Suffered damages during the 1934 CE earthquakes |  | damages, earthquakes | ee6be98a_1 |
| 262 | Suffered damages in the 2015 earthquakes |  | damages, earthquakes | 26e53618_0 |
| 263 | Unknown |  | damaged, destroys | 5f27520c_2 |
| 264 | Unknown |  | damaged | 98e982ee_7 |
| 265 | Unknown |  | damaged | 9c2fb17f_1 |
| 266 | Unknown |  | damaged | ccb98862_0 |
| 267 | Unknown |  | damaged | de276e42_19 |
| 268 | Unknown - unidentifiable |  | damaged | a91155c6_1 |
| 269 | Unknown Event |  | damaged | b83ff19b_4 |
| 270 | Unknown Event |  | damaged | b92b7a0f_17 |
| 271 | Unknown Event (not related to the temple) |  | damaged | 1fd94780_3 |
| 272 | Unknown event |  | damaged | 5d44f5b8_0 |
| 273 | Unknown event |  | damaged | 63ee2cfd_0 |
| 274 | Unknown event |  | damaged | 76ab9a02_1 |
| 275 | Unknown event |  | damaged | bb024f91_0 |
| 276 | Unknown event |  | damaged | bb024f91_1 |
| 277 | Unknown event |  | damaged | dbbc37d8_1 |
| 278 | Unknown event |  | damaged | ea45ba64_5 |
| 279 | Unknown event (A) |  | damaged | fe81f05f_7 |
| 280 | Unknown event (C) |  | damaged | fe81f05f_9 |
| 281 | Unknown event (perhaps the construction of a Caitya, i.e., SKH0080-001) |  | damaged | 0d31ecbb_2 |
| 282 | Unknown event(LAL0010-038) |  | damaged | 790c0a2a_22 |
| 283 | Unspecified Event |  | damaged | 06d2c415_10 |
| 284 | not determined |  | damaged | b66fa304_0 |
| 285 | unknown |  | damage | f5a48d0e_26 |

## `earthquake` (152)

| # | Event name | Renov. | Words matched | Event |
|---:|---|:-:|---|---|
| 1 | Bhāi Degaḥ, destruction of the temple | yes | earthquake | d5354d0a_1 |
| 2 | Destruction (2015) and rebuilding of the Phalcā (2022) | yes | earthquakes | 75e422cd_0 |
| 3 | Destruction by earthquake | yes | destroyed, earthquake | 3440946e_2 |
| 4 | Destruction by earthquake | yes | collapsed, earthquake | 44609e5a_2 |
| 5 | Destruction by earthquakes | yes | destroyed, earthquakes | d52dcb5c_3 |
| 6 | Devastation and restoration after the 1933 earthquakes | yes | earthquake, earthquakes | 28a074e0_0 |
| 7 | Dilapidated on earthquake | yes | damaged, earthquake | f142c371_1 |
| 8 | Earthquake Damages | yes | collapsed, damaged, damages, earthquake, earthquakes | 5790999f_0 |
| 9 | Earthquake Damages and Renovation | yes | damages, destroyed, earthquake, earthquakes | 5790999f_9 |
| 10 | Earthquake damage | yes | collapsing, damage, damaged, earthquake, earthquakes | 4bf00773_0 |
| 11 | Earthquake damage | yes | damage, earthquake, earthquakes | 54903008_3 |
| 12 | Empact of 1934 CE earthquake on the Bell | yes | earthquake | 5555d2e1_1 |
| 13 | Hosting of Śrīmadbhāgavata Saptāhā to collect funds for renovation | yes | earthquake | 7fd5e55f_6 |
| 14 | Kṣamāpūjā | yes | damaged, earthquake | f2fd559b_4 |
| 15 | Kṣamāpūā | yes | damaged, earthquake | 02f204ae_7 |
| 16 | Minor repairs | yes | earthquakes | 599606e0_1 |
| 17 | Photo Kathmandu - Patis in Patan | yes | earthquake | 4abcfc57_1 |
| 18 | Pillar restoration | yes | collapsed, earthquake | 72fbb5ec_3 |
| 19 | Rebuild of the phalcā | yes | damaged, earthquake | b5da89bd_0 |
| 20 | Rebuilding | yes | earthquakes | 8f92f98f_2 |
| 21 | Rebuilding of the monument | yes | earthquakes | 28b5cf2f_1 |
| 22 | Rebuilding of the monument | yes | earthquakes | 948ac803_2 |
| 23 | Rebuilding of the monument | yes | damage, earthquake | e93b5856_1 |
| 24 | Rebuilding of the monument | yes | earthquakes | ee74a9e1_1 |
| 25 | Rebuilding of the temple | yes | earthquake | 5bfb6d40_1 |
| 26 | Rebuilding the Dyaḥchẽ | yes | dismantling, earthquakes | 8f7a0db3_3 |
| 27 | Rebuilding the Temple | yes | earthquake | ff7398f9_3 |
| 28 | Rebuilt | yes | damage, earthquake | 673a329f_1 |
| 29 | Rebuilt | yes | damage, earthquake | 7947965c_1 |
| 30 | Rebuilt of the monument | yes | dismantled, earthquake | 083ed396_4 |
| 31 | Rebuilt of the phalcā | yes | collapsed, earthquakes | 6a68a4bf_0 |
| 32 | Rebuilt of the temple | yes | earthquake | 75171568_6 |
| 33 | Reconstruction | yes | earthquake | 3f87ad30_2 |
| 34 | Reconstruction | yes | earthquakes | 479763c6_1 |
| 35 | Reconstruction | yes | earthquakes | 4a473487_4 |
| 36 | Reconstruction | yes | earthquakes | 51fcc336_1 |
| 37 | Reconstruction | yes | damage, earthquake | 6ff6a70a_1 |
| 38 | Reconstruction | yes | damage, earthquakes | 8720f8e8_0 |
| 39 | Reconstruction | yes | earthquakes | 8fe22382_0 |
| 40 | Reconstruction | yes | earthquakes | 9e96833d_0 |
| 41 | Reconstruction | yes | earthquakes | a4be84b1_3 |
| 42 | Reconstruction | yes | earthquakes | a7ca999e_3 |
| 43 | Reconstruction | yes | earthquake | d52dcb5c_4 |
| 44 | Reconstruction after 2015 | yes | earthquakes | 3eed6ff1_5 |
| 45 | Reconstruction after earthquake 1934 | yes | earthquake | f8366c56_3 |
| 46 | Reconstruction after the 2015 earthquakes | yes | earthquakes | 38418dae_2 |
| 47 | Reconstruction after the Great Earthquake of 1934 CE | yes | earthquake | 2fa561e9_0 |
| 48 | Reconstruction after the earthquake of 2015 CE | yes | damage, earthquake | 8f5e6a23_2 |
| 49 | Reconstruction of Phlacā | yes | earthquakes | a867501c_2 |
| 50 | Reconstruction of digichẽ after the earthquakes of 2015 | yes | earthquake, earthquakes | 4ed2374c_11 |
| 51 | Reconstruction of the Akhadā | yes | earthquakes | 0d1f82cf_2 |
| 52 | Reconstruction of the Dyaḥchẽ | yes | earthquakes | 8615d9f8_1 |
| 53 | Reconstruction of the Phalcā | yes | damages, earthquakes | 9d4436ef_2 |
| 54 | Reconstruction of the Sataḥ | yes | damaged, earthquakes | f6f28540_3 |
| 55 | Reconstruction of the Temple | yes | earthquakes | e24051bb_3 |
| 56 | Reconstruction of the Temple after the 2015 earthquakes | yes | damages, earthquakes | 7fd5e55f_7 |
| 57 | Reconstruction of the monument | yes | earthquakes | 0426294d_0 |
| 58 | Reconstruction of the monument | yes | earthquake | 04696efe_1 |
| 59 | Reconstruction of the monument | yes | earthquakes | 13e36370_0 |
| 60 | Reconstruction of the monument | yes | damage, earthquake | 4cddce02_1 |
| 61 | Reconstruction of the monument | yes | earthquakes | 52ea5b64_2 |
| 62 | Reconstruction of the monument | yes | earthquake | 62468f09_2 |
| 63 | Reconstruction of the monument | yes | earthquakes | e642465f_2 |
| 64 | Reconstruction of the temple | yes | earthquakes | 05ed8b92_1 |
| 65 | Reconstruction of the temple | yes | earthquakes | 166b876b_4 |
| 66 | Reconstruction of the temple | yes | earthquakes | 54903008_2 |
| 67 | Reconstruction of the temple | yes | earthquakes | 5ae13e80_4 |
| 68 | Reconstruction of the temple | yes | earthquake | adad44a2_6 |
| 69 | Reconstruction of the temple | yes | damaged, earthquake | ee91d97c_1 |
| 70 | Reconstruction of the śivālaya | yes | earthquakes | 4104c0f3_0 |
| 71 | Reconstruction of the śivālaya | yes | earthquakes | 5f3fcfe9_3 |
| 72 | Reconstruction of the śivālaya | yes | collapsed, earthquakes | 8fef6355_0 |
| 73 | Reconstruction/restoration | yes | damaged, earthquake | a011c059_1 |
| 74 | Relocation of galleries | yes | damaged, earthquakes | bbe0fc5e_4 |
| 75 | Renovation | yes | earthquake | 0af56d4b_1 |
| 76 | Renovation | yes | earthquake | 14cbeef4_3 |
| 77 | Renovation | yes | damaged, earthquakes | 1762458a_1 |
| 78 | Renovation | yes | earthquakes | 2c4ce775_8 |
| 79 | Renovation | yes | damaged, earthquakes | 2e916236_1 |
| 80 | Renovation | yes | earthquakes | 6ac90a62_0 |
| 81 | Renovation | yes | damage, earthquakes | 902fab38_0 |
| 82 | Renovation | yes | earthquakes | a91155c6_0 |
| 83 | Renovation | yes | damages, dismantled, earthquakes | ae69ba5f_1 |
| 84 | Renovation | yes | earthquake | b9ea1eba_1 |
| 85 | Renovation after earthquake | yes | earthquake, earthquakes | 1b0a5033_3 |
| 86 | Renovation of Bāhāḥ | yes | earthquakes | 13b406e0_3 |
| 87 | Renovation of temple | yes | earthquake | e2371888_0 |
| 88 | Renovation of the Bāhāḥ | yes | earthquake | 3c768352_10 |
| 89 | Renovation of the Bāhāḥ | yes | earthquake | 415635af_2 |
| 90 | Renovation of the Bāhāḥ | yes | earthquake | f360c428_2 |
| 91 | Renovation of the Dyaḥchẽ - 2 | yes | earthquakes | 781d9148_1 |
| 92 | Renovation of the Monument | yes | earthquakes | 95211cfa_9 |
| 93 | Renovation of the Sataḥ | yes | earthquakes | 8ad6f527_4 |
| 94 | Renovation of the Temple | yes | earthquakes | 443544db_6 |
| 95 | Renovation of the Temple | yes | destroyed, earthquakes | 7fd5e55f_3 |
| 96 | Renovation of the monument | yes | collapse, earthquakes | 59d6dc2c_1 |
| 97 | Renovation of the roof | yes | damaged, earthquakes | 11b82f01_2 |
| 98 | Renovation of the temple | yes | damage, earthquake | 0a006229_20 |
| 99 | Renovation of the temple | yes | earthquakes | 62af421e_3 |
| 100 | Renovation of the temple | yes | earthquake | 9e929afa_0 |
| 101 | Renovation of the temple after the 2015 earthquakes | yes | damaged, earthquakes | 25c65422_8 |
| 102 | Repair of Bhīmasena statue | yes | earthquake | 557a604c_7 |
| 103 | Repair of roof | yes | earthquakes | 0826415c_9 |
| 104 | Repair of the Façade | yes | earthquakes | 13b406e0_5 |
| 105 | Repair of the śivālaya | yes | damaged, earthquakes | 03c4acec_0 |
| 106 | Repair of the śivālaya | yes | damage, earthquakes | 10e4e283_1 |
| 107 | Repair of the śivālaya | yes | earthquakes | b9ac6b46_1 |
| 108 | Repair of the śivālaya | yes | earthquakes | f8a823df_1 |
| 109 | Replacement of a Bell | yes | collapsed, earthquakes | 5790999f_15 |
| 110 | Restoration after the 1934 earthquake | yes | collapse, damage, earthquake, earthquakes | eeb8d34e_3 |
| 111 | Restoration following the 1934 earthquake | yes | collapse, earthquake | af836f1b_0 |
| 112 | Restoration of rest souses (sataḥ) | yes | earthquakes | 37637b5c_2 |
| 113 | Restoration of the Phalcā | yes | earthquakes | b7adbd29_1 |
| 114 | Restoration of the monument | yes | damaged, earthquakes | 91e10334_4 |
| 115 | Restoration of the sataḥ | yes | damage, earthquakes | 24001b17_2 |
| 116 | Restoration of the stone stambha and lion statue | yes | earthquakes | 3b68c5ca_14 |
| 117 | Restoration of the temple | yes | earthquakes | 05ed8b92_2 |
| 118 | Restoration of the temple | yes | earthquakes | a625bbb3_0 |
| 119 | Sataḥ Restoration Post-2015 CE Earthquake | yes | damage, earthquake | aabd2eaa_2 |
| 120 | 1934 CE earthquakes damage |  | collapse, damage, earthquakes | 05ed8b92_0 |
| 121 | Demolition of the akhaḍā |  | collapse, dismantled, earthquakes | 482bf3db_0 |
| 122 | Destruction by 1934 earthquakes |  | collapsed, earthquakes | 0b0e8dd4_8 |
| 123 | Destruction by earthquake |  | collapsed, earthquake | 16f8b0dc_1 |
| 124 | Destruction by earthquake |  | collapsed, earthquake | 3331db72_0 |
| 125 | Destruction by earthquake |  | earthquake | 460bec90_0 |
| 126 | Destruction by earthquake |  | earthquake | 870f3118_0 |
| 127 | Destruction by earthquake |  | collapsed, damaged, earthquake | 9d5039d0_0 |
| 128 | Destruction by earthquake |  | collapsed, earthquake | 9ff7fad8_1 |
| 129 | Destruction by the 2015 earthquake |  | damaged, earthquake | 3c768352_15 |
| 130 | Destruction in earthquake |  | collapsed, earthquake | 409cfb82_3 |
| 131 | Destruction in earthquake |  | collapsed, earthquake | 409cfb82_4 |
| 132 | Destruction in earthquake |  | destroyed, earthquake | 98358087_1 |
| 133 | Destruction in earthquake |  | collapsed, earthquake, earthquakes | c07ed9a8_1 |
| 134 | Destruction in earthquakes |  | collapsed, earthquakes | aa8a44d5_6 |
| 135 | Destruction of Bāhāḥ by earthquake |  | demolished, earthquake | 711b19a4_22 |
| 136 | Earthquake |  | collapsed, damages, earthquake, earthquakes | 43291104_0 |
| 137 | Earthquake |  | collapsed, earthquake | b1226710_1 |
| 138 | Earthquake Damages |  | damaged, damages, earthquake, earthquakes | a867501c_1 |
| 139 | Earthquake damage |  | damage, damaged, earthquake, earthquakes | 01de2008_4 |
| 140 | Earthquake damage |  | collapsed, damage, damaged, earthquake, earthquakes | 69370820_1 |
| 141 | Earthquake damage |  | damage, damaged, earthquake, earthquakes | 96d763ae_2 |
| 142 | Earthquake damage |  | damage, damaged, earthquake, earthquakes | d6342a6e_1 |
| 143 | Earthquake damage |  | damage, damaged, earthquake, earthquakes | dcfad1e4_5 |
| 144 | Earthquake destruction |  | damaged, earthquake | a79cdd22_2 |
| 145 | Erection of pillar |  | earthquake | f12a1f58_0 |
| 146 | Levelling the temple |  | earthquake | 24afe176_0 |
| 147 | PhotoKathmandu |  | earthquakes | b23905f8_0 |
| 148 | Removal of ruins |  | earthquake | ca7dd19e_4 |
| 149 | Special worship after earthquake 2015 |  | earthquake, earthquakes, fire | d30593b5_22 |
| 150 | Storing earthquake-related materials |  | earthquake | e7ad4210_2 |
| 151 | Toppling of the pillar's upper section and statues |  | damage, earthquakes | 72fbb5ec_2 |
| 152 | Use of the building for the Earthquake Loan Branch |  | earthquake | dcfad1e4_1 |

## `collaps` (112)

| # | Event name | Renov. | Words matched | Event |
|---:|---|:-:|---|---|
| 1 | Beginning of reconstruction | yes | collapse | bf182f12_2 |
| 2 | Collapse | yes | collapse, earthquakes | 6c63cbb9_0 |
| 3 | Collapse | yes | collapse, collapsed, earthquake | b90d17aa_1 |
| 4 | Collapse During the Earthquakes and Reconstruction | yes | collapse, collapsed, earthquakes | 5cb98dcd_7 |
| 5 | Collapse and reconstruction | yes | collapse, collapsed, earthquake | 72fbb5ec_1 |
| 6 | Collapse and reconstruction after earthquake | yes | collapse, earthquake | 930f4862_1 |
| 7 | Collapse during the Great Earthquake | yes | collapse, collapsed, earthquake | 74ae042c_1 |
| 8 | Collapse of the Taleju Ghara | yes | collapse | 02f204ae_5 |
| 9 | Collapse of the Temple and rebuilding it | yes | collapse, collapsed | 9e492819_0 |
| 10 | Collapse of the monument | yes | collapse, collapsed | bbf0265a_0 |
| 11 | Collapse of the pura (tower) | yes | collapse, collapsed, earthquake | 5c063668_1 |
| 12 | Collapse of the temple | yes | collapse, collapsed | 6fc2b495_0 |
| 13 | Collapse of the śikhara | yes | collapse, damage, earthquakes | 9a24d1d5_1 |
| 14 | Collapsed by the 1934 earthquakes | yes | collapsed, earthquakes | 01e4455d_1 |
| 15 | Collapsed during 1934 earthquake | yes | collapsed, earthquake | 03ab0902_0 |
| 16 | Collapsed during the 1833 CE earthquakes | yes | collapsed, earthquakes | 4866412c_0 |
| 17 | Concrete reconstruction | yes | collapse, dismantled | d3c6eaf6_1 |
| 18 | Construction of a new phalcā | yes | collapsed | 600ba6fa_1 |
| 19 | Construction of plinth of the temple | yes | collapsed | a4710aa7_3 |
| 20 | Destruction | yes | collapsed, demolish, earthquake | ca61f6c0_2 |
| 21 | Rebuilding | yes | collapsed, collapsing, earthquake, earthquakes | 98358087_2 |
| 22 | Rebuilding | yes | collapsed, earthquakes | d1fe9550_0 |
| 23 | Rebuilding and relocation of Kumārī Pāṭī | yes | collapse, earthquake | 3f88581e_1 |
| 24 | Rebuilding of the gate | yes | collapsed, earthquake | 8781be4e_0 |
| 25 | Rebuilding of the southern house of the Āgaṃchẽ | yes | collapsed, damaged, earthquakes | affdfc0b_2 |
| 26 | Rebuilding of the śikhara | yes | collapse, earthquakes | 9a24d1d5_4 |
| 27 | Rebuilding the Kvātha Chẽ | yes | collapsed, earthquakes | a2680407_1 |
| 28 | Rebuilt | yes | collapse | 387616cb_1 |
| 29 | Rebuilt | yes | collapsed | 38b263ba_3 |
| 30 | Reconstruction | yes | collapse, dismantled | 11b82f01_0 |
| 31 | Reconstruction | yes | collapsed, earthquakes | 3d6ceece_2 |
| 32 | Reconstruction | yes | collapse, earthquakes | 3f87ad30_3 |
| 33 | Reconstruction | yes | collapse, earthquakes | 56bfc1ff_2 |
| 34 | Reconstruction | yes | collapse, earthquakes | 8fa97d24_1 |
| 35 | Reconstruction | yes | collapsed, earthquakes | d6945b8c_0 |
| 36 | Reconstruction | yes | collapsed, earthquakes | d9c9b8a3_3 |
| 37 | Reconstruction | yes | collapsed, earthquakes | de9f5c23_2 |
| 38 | Reconstruction of the Gate | yes | collapsed | 7a17814e_1 |
| 39 | Reconstruction of the Phalcā | yes | collapsed | 3655168d_3 |
| 40 | Reconstruction of the Phalcā | yes | collapse | cdfc099f_0 |
| 41 | Reconstruction of the Pāṭī | yes | collapsed | 2a0b1750_1 |
| 42 | Reconstruction of the Sataḥ | yes | collapsed | 37d714e8_2 |
| 43 | Reconstruction of the Temple | yes | collapsed, earthquakes | 0826415c_8 |
| 44 | Reconstruction of the Temple | yes | collapsed | 9998e39b_1 |
| 45 | Reconstruction of the akhaḍā | yes | collapse, damage, dismantled, earthquakes | a648d429_1 |
| 46 | Reconstruction of the esoteric shrine | yes | collapsed, earthquake | 711b19a4_20 |
| 47 | Reconstruction of the phalcā | yes | collapse | 3ecea8a6_1 |
| 48 | Reconstruction of the roof tower and renewal of the roof | yes | collapsed, earthquakes | ba4a96ce_3 |
| 49 | Reconstruction of the sataḥ | yes | collapse, earthquakes | da9956e9_1 |
| 50 | Reconstruction of the temple | yes | collapsed, earthquake | 4f116514_8 |
| 51 | Reconstructions of the Sataḥ | yes | collapsed, dismantled, earthquakes | f6f28540_1 |
| 52 | Renovation | yes | collapsed, earthquakes | 0b0e8dd4_9 |
| 53 | Renovation of Bahī | yes | collapsed, earthquake | 7559d8ea_2 |
| 54 | Renovation of a Phalcā | yes | collapse, collapsed | ff7398f9_2 |
| 55 | Renovation of a phalcā | yes | collapsed, earthquakes | 52125686_3 |
| 56 | Renovation of the Dyaḥchẽ | yes | collapse | 227169da_1 |
| 57 | Renovation of the Temple | yes | collapse | b142ec3d_0 |
| 58 | Renovation of the Temple (A) | yes | collapsed | b83ff19b_0 |
| 59 | Repair of Bahī | yes | collapsed, earthquake | 44609e5a_0 |
| 60 | Restoration | yes | collapse, earthquake | 1e15e17c_1 |
| 61 | Restoration of the phalcā | yes | collapse | 65ef3af4_3 |
| 62 | Restoration of the temple | yes | collapse, earthquake | 1a1afb9a_3 |
| 63 | Starting the reconstruction of the dyaḥchẽ | yes | collapse | a9dcf214_11 |
| 64 | Temple Reconstruction | yes | collapse, earthquake | 74763c55_1 |
| 65 | Breaking the stone spout |  | collapsed, earthquakes | 34a4e5bc_0 |
| 66 | Collapse |  | collapse, collapsed, earthquakes | 017a4a8f_1 |
| 67 | Collapse |  | collapse, collapsed | 170a68d0_7 |
| 68 | Collapse |  | collapse, collapsed, earthquakes | 8544a7c2_0 |
| 69 | Collapse During the Earthquakes |  | collapse, collapsed, earthquakes | 5cb98dcd_0 |
| 70 | Collapse during the Gorkha earthquake |  | collapse, collapsed, earthquake, earthquakes | 900a45b8_0 |
| 71 | Collapse during the earthquake |  | collapse, collapsed, earthquake | c9bc2916_4 |
| 72 | Collapse during the earthquakes |  | collapse, collapsed, earthquakes | 9e492819_1 |
| 73 | Collapse in the 2015 earthquake |  | collapse, earthquake | 56bfc1ff_1 |
| 74 | Collapse in the 2015 earthquakes |  | collapse, collapsed, earthquakes | 5bd820a1_1 |
| 75 | Collapse in the 2015 earthquakes |  | collapse, collapsed, earthquakes | adad44a2_5 |
| 76 | Collapse of Bhīmasen's tower |  | collapse, collapsed, earthquakes | 083ed396_8 |
| 77 | Collapse of Phalcā |  | collapse, collapsed, earthquake | 1a0a8ea8_1 |
| 78 | Collapse of palace building |  | collapse, collapsed, earthquakes | bb6f90d7_1 |
| 79 | Collapse of pura (upperroof tower) |  | collapse | 5f218d0a_6 |
| 80 | Collapse of the 3-tiered temple |  | collapse, collapsed, earthquakes | 37637b5c_0 |
| 81 | Collapse of the Phalcā |  | collapse, collapsed, earthquake | ab83bc5c_0 |
| 82 | Collapse of the Phalcā |  | collapse, collapsed, earthquakes | 060e3322_0 |
| 83 | Collapse of the Phalcā |  | collapse, collapsed, earthquakes | a4df4e50_1 |
| 84 | Collapse of the Temple |  | collapse, collapsed | 9998e39b_0 |
| 85 | Collapse of the dyaḥchẽ |  | collapse | a9dcf214_10 |
| 86 | Collapse of the monument |  | collapse, collapsed, earthquakes | 083ed396_3 |
| 87 | Collapse of the monument |  | collapse, collapsed, earthquake | 083ed396_6 |
| 88 | Collapse of the monument |  | collapse, collapsed, damage, earthquakes | a2cfeca7_2 |
| 89 | Collapse of the roof and upper floor |  | collapse, collapsed, earthquakes | ca7dd19e_1 |
| 90 | Collapse of the roof tower (phucā). |  | collapse, collapsed, damaged, earthquakes | ba4a96ce_2 |
| 91 | Collapse of the stone pillar |  | collapse, earthquake | 3b68c5ca_12 |
| 92 | Collapse of the temple |  | collapse, collapsed, earthquake | f3be59cc_0 |
| 93 | Collapse of the top two roofs |  | collapse, collapsed, earthquakes | 1347d2d6_4 |
| 94 | Collapse of the upper roof |  | collapse | c79cc000_4 |
| 95 | Collapse of the āgaṃchẽ in the earthquake. |  | collapse, collapsed, earthquake, earthquakes | 98e982ee_9 |
| 96 | Collapse of the śikhara |  | collapse, earthquakes | 9a24d1d5_3 |
| 97 | Collapse of upper tier in 1934 earthquakes |  | collapse, collapsed, damage, earthquake, earthquakes | 0a006229_16 |
| 98 | Collapsed |  | collapsed | ece92710_1 |
| 99 | Collapsed by earthquake |  | collapsed, earthquake | 5d9c1eae_16 |
| 100 | Collapsed in 2015 CE earthquakes |  | collapsed, destroyed, earthquakes | 4a473487_3 |
| 101 | Collapsed on 2015 earthquake |  | collapsed, earthquake | 2eb2709a_2 |
| 102 | Construction of Mandaḥ Phalcā (KIR4056) |  | collapsed | 1809008c_0 |
| 103 | Construction of the temporary shrine of Buṅgadyaḥ |  | collapse, earthquakes | 8fe3c368_0 |
| 104 | Destruction of the temple |  | collapsed, earthquake | 5f218d0a_0 |
| 105 | Destruction of the temple |  | collapsed, earthquake | d024e070_2 |
| 106 | Establishing an image from the nearby Nārāyaṇa Temple |  | collapsed, earthquake | e5618dda_1 |
| 107 | GPR survey |  | collapsed, earthquake | b947bd74_7 |
| 108 | Installation of wooden pillar |  | collapsed | 742a774c_0 |
| 109 | Offering of a bell |  | collapsed | 9bf90959_0 |
| 110 | Roof collapse |  | collapse, collapsed, earthquakes | a12441fe_1 |
| 111 | Temple Collapse |  | collapse, earthquake | 74763c55_0 |
| 112 | Wall collapse |  | collapse | 6cef8522_2 |

## `dismantl` (68)

| # | Event name | Renov. | Words matched | Event |
|---:|---|:-:|---|---|
| 1 | Addition of a statue and rebuilding of the monument | yes | dismantled | 64a2bcf3_1 |
| 2 | Commencement of reconstruction | yes | dismantling | c6ce5cc1_2 |
| 3 | Construction of Lālabaiṭhaka | yes | dismantled | 58201fa0_1 |
| 4 | Construction of the Sataḥ | yes | dismantled | adfd2472_1 |
| 5 | Converted into a concrete phalcā | yes | dismantled | b5f8d23a_0 |
| 6 | Converting Śikharakūṭa temple into tiered temple | yes | dismantled | f5a48d0e_15 |
| 7 | Demolition of the monument and reconstruction | yes | demolished, dismantled, earthquakes | 7a255e97_4 |
| 8 | Demolition of the phalcā and construction of a commercial building | yes | dismantled | 3ceea016_1 |
| 9 | Dismantling for reconstruction | yes | damaged, dismantled, dismantling, earthquakes | cc74e5d8_3 |
| 10 | Dismantling of the building | yes | damaged, dismantled, dismantling | 0d3c9626_0 |
| 11 | Dismantling of the phalcā | yes | dismantled, dismantling | 83d25607_1 |
| 12 | Kṣamāpūjā and dismantling | yes | dismantling | 6e03bbf6_1 |
| 13 | Rebuilding of the Phalcā | yes | dismantled | 28e34398_2 |
| 14 | Rebuilding of the Phalcā | yes | dismantled | 5576adf8_0 |
| 15 | Rebuilding of the Phalcā | yes | dismantled | f7773bd2_0 |
| 16 | Rebuilding of the monument | yes | dismantled | 8ad6f527_6 |
| 17 | Rebuilding of the west and north wing | yes | dismantled | 68934505_2 |
| 18 | Rebuilding the Phalcā | yes | dismantled | ca193ec5_0 |
| 19 | Rebuilding the monastic building | yes | dismantled | 33d9ec0a_1 |
| 20 | Rebuilding the monument | yes | dismantled | b088faf0_0 |
| 21 | Reconstruction | yes | dismantled | 1c2db54a_0 |
| 22 | Reconstruction | yes | dismantled | 2bbfcb7d_0 |
| 23 | Reconstruction | yes | dismantled | 3a781560_1 |
| 24 | Reconstruction | yes | dismantled | 8ffce5d6_1 |
| 25 | Reconstruction | yes | dismantled | 9ee098ae_0 |
| 26 | Reconstruction | yes | dismantled | adc2f4ee_2 |
| 27 | Reconstruction | yes | dismantled | bc3c1b44_2 |
| 28 | Reconstruction | yes | dismantled | cc74e5d8_1 |
| 29 | Reconstruction | yes | dismantled | d13be190_0 |
| 30 | Reconstruction | yes | dismantled | f9cdfd48_0 |
| 31 | Reconstruction and addition of another floor | yes | dismantled | 3c2f1cda_2 |
| 32 | Reconstruction in the late 90s | yes | dismantled | 38418dae_1 |
| 33 | Reconstruction of Phalcā | yes | dismantled | 2a5c82ae_2 |
| 34 | Reconstruction of Phalcā | yes | dismantled | df0f0bae_0 |
| 35 | Reconstruction of the Capāḥ | yes | dismantled | 06a4360c_1 |
| 36 | Reconstruction of the Phalcā | yes | dismantled | 254b0d1c_0 |
| 37 | Reconstruction of the Phalcā | yes | dismantled | 31a8b585_0 |
| 38 | Reconstruction of the Phalcā | yes | dismantled | 37438b5c_0 |
| 39 | Reconstruction of the Phalcā | yes | dismantled | 786fe3c9_1 |
| 40 | Reconstruction of the Phalcā | yes | dismantled | c1c37f40_1 |
| 41 | Reconstruction of the Phalcā | yes | dismantling | effa4b2e_1 |
| 42 | Reconstruction of the Temple | yes | dismantled | 2a5fe4da_12 |
| 43 | Reconstruction of the dyaḥchẽ | yes | dismantled | a9dcf214_15 |
| 44 | Reconstruction of the east wing | yes | dismantled | 68934505_1 |
| 45 | Reconstruction of the gate | yes | dismantled | 19c47b0a_1 |
| 46 | Reconstruction of the monument | yes | dismantled | 655e33f0_4 |
| 47 | Reconstruction of the monument | yes | dismantled | 78211803_2 |
| 48 | Reconstruction of the sataḥ | yes | dismantled | 8657bd6a_0 |
| 49 | Reconstruction of the sataḥ | yes | dismantled | bddc9722_2 |
| 50 | Reconstruction of the temple | yes | dismantled | 989f4dde_0 |
| 51 | Reconstruction of the temple | yes | damaged, dismantled | bdca6826_1 |
| 52 | Renovation | yes | dismantled, earthquake | 00cf6d20_2 |
| 53 | Renovation of the temple | yes | dismantle | 75171568_0 |
| 54 | Replacing jhiṅgaṭī roof with concrete | yes | dismantled | 7399ba4a_0 |
| 55 | Restoration | yes | dismantled | 5c063668_3 |
| 56 | Restoration | yes | damaged, dismantled | 6206f79c_0 |
| 57 | Restoration | yes | dismantled | 95b952e2_0 |
| 58 | Restoration | yes | dismantled | 9f7d86ba_1 |
| 59 | Restoration 2002 | yes | dismantling | 43291104_1 |
| 60 | Construction of a phalcā |  | dismantled | fb345afd_0 |
| 61 | Construction of a phalcā at Pacalī Bhairava |  | dismantling | ad1fdb35_0 |
| 62 | Construction of fourstoreybuilding |  | dismantled | 60a8a8e0_3 |
| 63 | Converted into a concrete phalcā |  | dismantled | 2298db0e_0 |
| 64 | Demolition of the phalcā |  | dismantled | c6ce5cc1_0 |
| 65 | Dismantling of phalcā |  | dismantle, dismantling | a7417ecf_0 |
| 66 | Inauguration |  | dismantling | 673afbfc_0 |
| 67 | Installing door to build new temple |  | dismantled | 0077a8d9_5 |
| 68 | Shifting the Jadhuṃhiti |  | dismantled | b088faf0_2 |

## `fire` (43)

| # | Event name | Renov. | Words matched | Event |
|---:|---|:-:|---|---|
| 1 | Beatification of Golden Gate | yes | fire | 0232aa9c_1 |
| 2 | Beatification of Golden Gate | yes | fire | 0232aa9c_2 |
| 3 | Construction of a Bhuvaneśvarī Shrine | yes | fire | c501bcf1_0 |
| 4 | Destruction by blaze | yes | destroyed, fire | 16f8b0dc_4 |
| 5 | Formation of a Committee and Renovation of the Temple | yes | fire | 7f398f5a_15 |
| 6 | Reconstruction of the Sīdhvākhā | yes | fire | 3d6d075f_0 |
| 7 | Renovation | yes | fire | 8b6a57d4_4 |
| 8 | Renovation of caityas | yes | fire | 91b124d2_1 |
| 9 | Renovation of phalcā | yes | fire | 94b79277_0 |
| 10 | Renovation of the temple | yes | fire | 425bbdb8_3 |
| 11 | Repair of Cāmuṇḍādevī | yes | fire | 39beb848_9 |
| 12 | Repair of the image of Cakrasaṃvara | yes | fire | f1dcfeda_2 |
| 13 | Repairing the Temple | yes | damage, fire | 8bd0dd8f_2 |
| 14 | Attempts to Set Fire |  | fire | d46efa17_0 |
| 15 | Blood seen on the statue |  | fire | 313ebade_2 |
| 16 | Chariot of Rāto Matsyendranātha Caught in Fire |  | damage, fire | ef7069e0_1 |
| 17 | Construction of Sataḥ |  | fire | 2a8e92e4_0 |
| 18 | Construction of a caitya |  | fire | dcf4fb94_0 |
| 19 | Construction of the temple |  | fire | 00ebce6c_0 |
| 20 | Donation of finials and a lotus flower |  | fire | e862d312_0 |
| 21 | Endowment of land |  | fire | 13b0e238_9 |
| 22 | Endowment of lands |  | fire | b947bd74_2 |
| 23 | Endowment of lands |  | fire | bcb98cfb_2 |
| 24 | Establishment of guṭhī and donation of finial and window |  | fire | 409cfb82_0 |
| 25 | Establishment of the bāhāḥ |  | fire | e4e53fcc_1 |
| 26 | Formation of a Guthi |  | fire | 3b731959_0 |
| 27 | Initial Construction of the Temple |  | fire | b83ff19b_1 |
| 28 | Initial construction |  | fire | 8ad6f527_3 |
| 29 | Installation of a stone buffalo statue |  | fire | 425bbdb8_1 |
| 30 | Installation of statues of Gaṇeśa and Bhairava |  | fire | 1676ae2c_5 |
| 31 | Land endowment |  | fire | 6cb38691_3 |
| 32 | Laying the foundation |  | fire | 487cc7fc_0 |
| 33 | Occupation by Āditya Malla |  | fire | 12e25456_1 |
| 34 | Offering of Yajñakuṇḍa |  | fire | d30593b5_21 |
| 35 | Paving of tiles |  | fired | 5b72e0fa_3 |
| 36 | Performance of koṭyāhuti yajña |  | fire | 0a006229_13 |
| 37 | Performance of rituals for auspiciousness after Caughrā Sataḥ caught fire |  | fire | 959482f1_3 |
| 38 | Performing a fire sacrifice (yajña) |  | fire | 0a7b6845_2 |
| 39 | Selection of stone |  | fire | 576713ba_1 |
| 40 | Selection of stone for construction |  | fire | 576713ba_6 |
| 41 | Selection of the stone |  | fire | ccb9b760_4 |
| 42 | Treaty between Patan, Kantipur and Bhaktapur |  | fire | 39bb2040_2 |
| 43 | Vyāghrinī statue catches fire |  | fire | 7f65c791_7 |

## `demolish` (19)

| # | Event name | Renov. | Words matched | Event |
|---:|---|:-:|---|---|
| 1 | Demolishing the Preceding Structure | yes | demolished, demolishing | 12f3faf5_1 |
| 2 | Demolishing the old small temple and building a new big temple | yes | demolishing | 735f3fdf_0 |
| 3 | Rebuilding of the Temple | yes | demolished | 4405bb30_3 |
| 4 | Rebuilding of the monument | yes | demolished | 71c76072_0 |
| 5 | Rebuilding of the monument | yes | demolished, earthquakes | 77b88f79_4 |
| 6 | Rebuilding of the monument | yes | demolished, earthquake | f4910f52_1 |
| 7 | Rebuilding the Dyaḥchẽ and installation of new statue of Nīlakaṇṭha Lokeśvara | yes | demolished | cdc824f7_2 |
| 8 | Rebuilt | yes | demolished | 4b6b1b40_2 |
| 9 | Reconstruction | yes | demolished | 55ef0210_1 |
| 10 | Reconstruction of the Gate | yes | demolished | 7a17814e_0 |
| 11 | Reconstruction of the Temple | yes | demolished | 6ce75bd3_4 |
| 12 | Reconstruction of the monastic building | yes | demolished | 26404afc_1 |
| 13 | Renovation | yes | demolished | 83e736d7_1 |
| 14 | Renovation of the Caitya | yes | demolished | 553b9314_0 |
| 15 | Restoration of the phalcā | yes | demolished | 6594f9ac_0 |
| 16 | Converted into a concrete Phalcā |  | demolished | 306b0be4_0 |
| 17 | Demolished |  | demolished | 60073217_1 |
| 18 | Demolishing of previous temple |  | demolished, demolishing | 0a006229_4 |
| 19 | Destruction of the  pāṭī |  | demolished | 264bb1e3_0 |

## `destroy` (13)

| # | Event name | Renov. | Words matched | Event |
|---:|---|:-:|---|---|
| 1 | Completion of restoration | yes | destroyed, earthquake | 9d5039d0_1 |
| 2 | Initial construction | yes | destroyed, earthquake | 8fa97d24_2 |
| 3 | Initial construction of the Phalcā | yes | destroyed | b47cd1c2_0 |
| 4 | Reconstruction of the temple | yes | destroyed, earthquake | 256339d6_1 |
| 5 | Reconstruction of the temple | yes | destroyed | 4f116514_4 |
| 6 | Reconstruction of the temple | yes | destroyed, fire | 5d9e8143_2 |
| 7 | Reconstruction of the temple | yes | destroyed, earthquakes | d1b6c182_4 |
| 8 | Renovation | yes | destroyed, earthquake | eb234e74_1 |
| 9 | Renovation of Bhelāchẽ Phalcā | yes | destroyed, earthquake | 0706813a_3 |
| 10 | Construction of the phalcā near the temple |  | destroyed | da572af6_2 |
| 11 | Destroyed by fire |  | destroyed, fire | 12e25456_0 |
| 12 | Destruction |  | destroyed, earthquakes | a2b60b1a_1 |
| 13 | Donation of a toraṇa |  | destroyed, earthquake | b1226710_2 |

## `flood` (2)

| # | Event name | Renov. | Words matched | Event |
|---:|---|:-:|---|---|
| 1 | Cleaning of the hiti |  | flooded | e2a4580b_4 |
| 2 | Washed away by the flood |  | flood, floods | 0a7b6845_3 |

## `burn` (1)

| # | Event name | Renov. | Words matched | Event |
|---:|---|:-:|---|---|
| 1 | Construction of the phalcā and donation of land |  | burning | 55133c56_0 |
