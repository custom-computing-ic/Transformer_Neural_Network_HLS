<<<<<<< HEAD
// Numpy array shape [5, 16]
// Min -0.5246283
// Max 0.7110446
=======
// Numpy array shape [5, 64]
// Min -0.465491
// Max 0.417904
>>>>>>> 9c0d86c28c83f71f1cb2ea0cb2e3aa899ae4e20c
// Number of zeros 0

#ifndef OUT_LAYER_1_WEIGHT_H_
#define OUT_LAYER_1_WEIGHT_H_

#ifndef __SYNTHESIS__
<<<<<<< HEAD
model_default_t out_layer_1_weight[80];
#else
model_default_t out_layer_1_weight[80] = {0.02078797109425068, -0.17202243208885193, 0.11627372354269028, -0.4509080648422241, -0.16722537577152252, -0.06844497472047806, 
-0.06359045952558517, 0.1512320190668106, -0.15432965755462646, -0.21917742490768433, -0.09795388579368591, 0.2277151197195053, -0.018527716398239136, 
0.17448782920837402, 0.27873966097831726, -0.22450236976146698, -0.19954417645931244, -0.20809637010097504, 0.23591183125972748, 0.17663335800170898, 
-0.08834181725978851, 0.2567600607872009, -0.08963444828987122, 0.20812936127185822, -0.1344001293182373, -0.257107675075531, 0.05003809183835983, 
0.32450342178344727, -0.5246282815933228, 0.30065014958381653, -0.36285683512687683, -0.1210363358259201, 0.11556421220302582, 0.2984830439090729, 
-0.07893751561641693, -0.316067099571228, 0.13744480907917023, 0.3050859868526459, 0.05919109657406807, -0.3237791657447815, 0.38563814759254456, 
0.10364944487810135, -0.2299220710992813, -0.20841342210769653, -0.4107835292816162, -0.22116759419441223, -0.08548621833324432, 0.28083109855651855, 
-0.07715906202793121, 0.21968688070774078, 0.20671118795871735, 0.25369417667388916, -0.08066246658563614, 0.04009633883833885, -0.15871891379356384, 
0.06994254887104034, 0.24699674546718597, -0.4194968044757843, -0.09768328070640564, 0.28489360213279724, -0.0526876263320446, -0.09398036450147629, 
-0.20723095536231995, -0.44160908460617065, 0.7110446095466614, 0.16201606392860413, 0.05482153967022896, 0.0042793466709554195, 0.10157135128974915, 
-0.13767854869365692, 0.2408340573310852, 0.36661496758461, 0.08850359171628952, -0.4462393522262573, 0.2163180261850357, -0.2158689796924591, 
0.24877934157848358, -0.19314517080783844, 0.04452255740761757, 0.02206495776772499};
=======
top_mlp_weight_t out_layer_1_weight[320];
#else
top_mlp_weight_t out_layer_1_weight[320] = {-0.13954222202301025, 0.23150207102298737, -0.050581447780132294, -0.1758619248867035, 0.12684325873851776, 0.08673612028360367, 
-0.17316918075084686, 0.1262194812297821, 0.08608376234769821, 0.05513680353760719, -0.08330795913934708, 0.03291607275605202, 0.021273577585816383, 
-0.05798182636499405, 0.13354600965976715, -0.07337882369756699, 0.13264286518096924, -0.0979418009519577, -0.12045618891716003, 0.1398964822292328, 
0.05144119635224342, -0.009276755154132843, -0.040007803589105606, 0.13187281787395477, -0.13497872650623322, -0.0041903904639184475, -0.07466429471969604, 
0.06720228493213654, 0.27874431014060974, -0.006969667971134186, 0.1443290114402771, 0.15999816358089447, -0.1958940625190735, -0.013009189628064632, 
-0.18570509552955627, -0.0926397293806076, -0.049687933176755905, -0.034964870661497116, -0.015612675808370113, 0.2113499939441681, 0.17622560262680054, 
0.1281767189502716, -0.2777959406375885, 0.09518125653266907, 0.0853983610868454, -0.13531593978405, -0.05391830950975418, 0.27801501750946045, 
-0.2548103630542755, 0.10069058835506439, 0.03151929751038551, -0.13704052567481995, 0.0635644719004631, 0.0981922447681427, 0.136363685131073, 
-0.14647874236106873, -0.15344306826591492, 0.19582609832286835, 0.17708949744701385, -0.231339693069458, 0.05433299019932747, 0.13466776907444, 
-0.3216107189655304, -0.014682160690426826, -0.1283993422985077, 0.19069349765777588, 0.22513483464717865, -0.46549099683761597, -0.10002389550209045, 
0.24462205171585083, -0.1347409188747406, 0.07119092345237732, 0.13297827541828156, -0.16958987712860107, 0.16884514689445496, -0.03155512362718582, 
-0.12701468169689178, 0.41790398955345154, -0.13464629650115967, 0.03311973065137863, 0.11986695975065231, 0.0740632489323616, -0.07678069174289703, 
-0.1556870937347412, -0.11006779223680496, -0.13613677024841309, -0.07446754723787308, -0.00011584166350075975, 0.329576313495636, -0.1446290910243988, 
-0.0009151235572062433, -0.14331161975860596, -0.17314504086971283, 0.29933100938796997, -0.14472295343875885, 0.13397358357906342, 0.06304142624139786, 
0.04192142188549042, -0.312472403049469, 0.023434320464730263, -0.12053090333938599, -0.038790810853242874, 0.0760880708694458, 0.07936249673366547, 
-0.14978371560573578, 0.10679725557565689, 0.13355663418769836, 0.03312458470463753, 0.12824691832065582, -0.2000146508216858, -0.09295754134654999, 
-0.11116743832826614, -0.0388006791472435, 0.21866999566555023, -0.021668117493391037, -0.05838568136096001, 0.05205990746617317, 0.14867739379405975, 
0.12033762037754059, -0.2564564347267151, 0.12228503823280334, 0.17183421552181244, -0.18277840316295624, 0.009524676948785782, 0.09821319580078125, 
0.14776428043842316, 0.10349113494157791, -0.2568569779396057, 0.06535589694976807, -0.025376398116350174, 0.06573120504617691, 0.016952307894825935, 
-0.296554297208786, 0.2819960117340088, 0.012744363397359848, -0.22698847949504852, 0.10510700941085815, 0.22371575236320496, 0.17880567908287048, 
-0.12939883768558502, 0.1694602519273758, -0.03602539747953415, -0.15743985772132874, -0.3453613519668579, 0.10991985350847244, 0.0955544039607048, 
0.1561499685049057, -0.2223871946334839, -0.012208975851535797, 0.037835802882909775, 0.1790003925561905, -0.045882221311330795, -0.11989539116621017, 
-0.1676643341779709, 0.1029767096042633, 0.14586521685123444, 0.14016951620578766, -0.21601781249046326, -0.19559533894062042, 0.2245965600013733, 
0.14879927039146423, -0.03247741609811783, -0.154057577252388, -0.2388351559638977, 0.17788565158843994, 0.2298801839351654, 0.012677526101469994, 
-0.1414671242237091, -0.18339841067790985, -0.05003621056675911, -0.050880324095487595, -0.05730330944061279, -0.06737006455659866, 0.024648046121001244, 
0.20421214401721954, 0.03920364752411842, 0.0600937157869339, 0.04818139597773552, 0.1799200028181076, -0.2021874338388443, 0.12226346880197525, 
0.1632266342639923, -0.2979346513748169, 0.07457491755485535, -0.06738283485174179, 0.06071881204843521, 0.09503953903913498, -0.1359451562166214, 
-0.35630327463150024, 0.1656033843755722, 0.17804867029190063, -0.059370122849941254, 0.033816322684288025, -0.16789084672927856, 0.20707865059375763, 
-0.08779136091470718, 0.04988153278827667, -0.014336506836116314, 0.1471215784549713, 0.048498064279556274, -0.17694124579429626, 0.15980279445648193, 
0.0742388442158699, 0.15693821012973785, -0.03421241044998169, 0.0740000456571579, -0.021346237510442734, -0.2957289218902588, 0.31291109323501587, 
-0.003686774056404829, -0.16095198690891266, 0.0016363277100026608, 0.1722041815519333, 0.2718985378742218, -0.1351127326488495, -0.003508427180349827, 
0.0012230593711137772, 0.331013023853302, -0.2006577104330063, -0.03540351986885071, 0.15803633630275726, -0.10550900548696518, -0.06427150964736938, 
-0.12436489760875702, 0.18578287959098816, -0.15685948729515076, 0.039221324026584625, -0.09900769591331482, -0.22362437844276428, 0.19520173966884613, 
0.04993296042084694, -0.008568783290684223, -0.2511342167854309, 0.17419756948947906, 0.2553136348724365, -0.21616831421852112, -0.14125484228134155, 
0.15811145305633545, 0.08931571245193481, 0.18333616852760315, 0.05975634604692459, -0.06988156586885452, 0.16275906562805176, -0.07073554396629333, 
0.20901069045066833, -0.1740434765815735, 0.08230193704366684, 0.06950125843286514, 0.1569156050682068, -0.14526502788066864, 0.10208285599946976, 
-0.0873401090502739, -0.036557503044605255, 0.09931881725788116, -0.12033610790967941, -0.14733602106571198, -0.010864908806979656, 0.02600434608757496, 
0.34969615936279297, 0.056322190910577774, -0.12347596883773804, -0.005804042797535658, -0.06079525128006935, -0.1020260602235794, 0.12829463183879852, 
0.14753231406211853, 0.17641863226890564, -0.10650377720594406, -0.2818247973918915, 0.2109254002571106, -0.11918751150369644, -0.19735758006572723, 
0.28927212953567505, 0.040575869381427765, 0.2778191566467285, 0.019250374287366867, 0.08257739990949631, -0.14125467836856842, -0.16605263948440552, 
-0.14009304344654083, 0.010349967516958714, 0.028193214908242226, -0.2323121279478073, 0.26448529958724976, 0.15234626829624176, -0.10489969700574875, 
-0.16363823413848877, 0.14218029379844666, 0.004057766869664192, 0.004075202625244856, -0.11475870758295059, -0.13342097401618958, 0.18061195313930511, 
0.19037337601184845, -0.07413735240697861, -0.015947310253977776, 0.008284213952720165, -0.05916354060173035, -0.26535189151763916, 0.17909975349903107, 
0.08912932127714157, -0.10142162442207336, 0.05621304735541344, -0.07638012617826462, -0.16298064589500427, -0.06414484232664108, -0.023158548399806023, 
0.2636248767375946, -0.2159896194934845, -0.06585066020488739, -0.06455673277378082, -0.1575334519147873, -0.05973824858665466, -0.012568256817758083, 
0.16470035910606384, -0.12819775938987732, -0.12598255276679993, 0.10573777556419373, -0.028085723519325256, 0.09204700589179993};
>>>>>>> 9c0d86c28c83f71f1cb2ea0cb2e3aa899ae4e20c

#endif

#endif
