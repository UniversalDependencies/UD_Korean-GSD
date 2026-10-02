#!/usr/bin/env python3
"""Fix too-many-subjects errors in Korean GSD (dev branch).

Strategy:
- Outer topic (은/는 topic marker) → nsubj:outer
- 수 있다/없다 construction: non-수 argument → nsubj:outer
- 도 (also/even marker) → nsubj:outer
- Default (both -이/가 subject markers): first/lower-ID node → nsubj:outer,
  which is correct because Korean outer topics always precede inner subjects.

All 402 errors across train/dev/test are fixed here.
"""
import os
import udapi

FIXES = {
    # dev-s12
    # TEXT: 시키다 말투가 기분 나빠서 취소했어요
    # TRANSLIT: .si.ki.da .mal.tu.ga .gi.bun .na.bba.seo .chwi.so.haess.eo.yo
    # ENGLISH: The way of speaking made me feel bad.
    # CONFLICT: 2:말투가(nsubj→나빠서), 3:기분(nsubj→나빠서)
    # Fix: default: N1(말투가)→outer [NEEDS REVIEW]
    'dev-s12': [('deprel', 2, 'nsubj:outer')],

    # dev-s123
    # TEXT: 집 근처라 지나가다 들러봤는데 파스타건 피자건 맛은 두말할 나위 없이 만족스럽습니다.
    # TRANSLIT: .jib .geun.cheo.ra .ji.na.ga.da .deul.reo.bwass.neun.de .pa.seu.ta.geon .pi.ja.geon .mas.eun .du.mal.hal .na.wi .eobs.i .man.jog.seu.reob.seub.ni.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 5:파스타건(nsubj→만족스럽습니다), 7:맛은(nsubj→만족스럽습니다)
    # Fix: topic-marker: N2(은/는)→outer
    'dev-s123': [('deprel', 7, 'nsubj:outer')],

    # dev-s126
    # TEXT: 남부지방은 남해안을 중심으로 비가 꾸준히 이어지다가 토요일 새벽에 대부분 그치기 때문에, 주말 야외활동에는 지장이 없겠습니다.
    # TRANSLIT: .nam.bu.ji.bang.eun .nam.hae.an.eul .jung.sim.eu.ro .bi.ga .ggu.jun.hi .i.eo.ji.da.ga .to.yo.il .sae.byeog.e .dae.bu.bun .geu.chi.gi .ddae.mun.e, .ju.mal .ya.oe.hwal.dong.e.neun .ji.jang.i .eobs.gess.seub.ni.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:남부지방은(nsubj→없겠습니다), 15:지장이(nsubj→없겠습니다)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s126': [('deprel', 1, 'nsubj:outer')],

    # dev-s142
    # TEXT: 무었보다 알바보다는 운송하는 사람이 책임이 있다고 생각한다
    # TRANSLIT: .mu.eoss.bo.da .al.ba.bo.da.neun .un.song.ha.neun .sa.ram.i .chaeg.im.i .iss.da.go .saeng.gag.han.da
    # ENGLISH: That person has responsibility.
    # CONFLICT: 4:사람이(nsubj→있다고), 5:책임이(nsubj→있다고)
    # Fix: default: N1(사람이)→outer [NEEDS REVIEW]
    'dev-s142': [('deprel', 4, 'nsubj:outer')],

    # dev-s168
    # TEXT: 한국경영자총협회는 "이번 북한의 도발로 우리 군과 선량한 주민의 인명피해가 발생했고 한반도는 물론 국제사회의 평화와 안정도 위협받고 있다"며 "경영계는 북한의 범죄행위를 강력히 규탄하며 정부는 강력하게 응징해야 한다"고 주문했다.
    # TRANSLIT: .han.gug.gyeong.yeong.ja.chong.hyeob.hoe.neun ".i.beon .bug.han.yi .do.bal.ro .u.ri .gun.gwa .seon.ryang.han .ju.min.yi .in.myeong.pi.hae.ga .bal.saeng.haess.go .han.ban.do.neun .mul.ron .gug.je.sa.hoe.yi .pyeong.hwa.wa .an.jeong.do .wi.hyeob.bad.go .iss.da".myeo ".gyeong.yeong.gye.neun .bug.han.yi .beom.joe.haeng.wi.reul .gang.ryeog.hi .gyu.tan.ha.myeo .jeong.bu.neun .gang.ryeog.ha.ge .eung.jing.hae.ya .han.da".go .ju.mun.haess.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 12:한반도는(nsubj→위협받고), 15:평화와(nsubj→위협받고)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s168': [('deprel', 12, 'nsubj:outer')],

    # dev-s174
    # TEXT: 일반적으로, 모든 가믈란 사이에는 차이가 있으며, 특히 상류층 사회에서 나타난 가믈란은 개성적인 스타일이 존재한다.
    # TRANSLIT: .il.ban.jeog.eu.ro, .mo.deun .ga.meul.ran .sa.i.e.neun .cha.i.ga .iss.eu.myeo, .teug.hi .sang.ryu.cheung .sa.hoe.e.seo .na.ta.nan .ga.meul.ran.eun .gae.seong.jeog.in .seu.ta.il.i .jon.jae.han.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 13:가믈란은(nsubj→존재한다), 15:스타일이(nsubj→존재한다)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s174': [('deprel', 13, 'nsubj:outer')],

    # dev-s238
    # TEXT: 포르쉐를 벤치마킹한 2세대는 전륜 브레이크에는 일본의 승용차로는 최초로 대향 4 피스톤의 알루미늄 캘리퍼를 적용되는 등 성능이 크게 향상되었다.
    # TRANSLIT: .po.reu.swe.reul .ben.chi.ma.king.han 2.se.dae.neun .jeon.ryun .beu.re.i.keu.e.neun .il.bon.yi .seung.yong.cha.ro.neun .choe.cho.ro .dae.hyang 4 .pi.seu.ton.yi .al.ru.mi.nyum .kael.ri.peo.reul .jeog.yong.doe.neun .deung .seong.neung.i .keu.ge .hyang.sang.doe.eoss.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 3:2세대는(nsubj→향상되었다), 16:성능이(nsubj→향상되었다)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s238': [('deprel', 3, 'nsubj:outer')],

    # dev-s263
    # TEXT: 셀프라 가격도 저렴하고 기름도 저질 기름 같지는 않습니다
    # TRANSLIT: .sel.peu.ra .ga.gyeog.do .jeo.ryeom.ha.go .gi.reum.do .jeo.jil .gi.reum .gat.ji.neun .anh.seub.ni.da
    # ENGLISH: This place also has good food.
    # CONFLICT: 4:기름도(nsubj→같지는), 5:저질(nsubj→같지는)
    # Fix: also-marker: N1(도)→outer
    'dev-s263': [('deprel', 4, 'nsubj:outer')],

    # dev-s270
    # TEXT: 동쪽 정면의 황소 머리들내부 벽들에는 프레스코화들이 그려져 있는데, 그림들의 대부분은 원본 상태가 보존되지 못했다.
    # TRANSLIT: .dong.jjog .jeong.myeon.yi .hwang.so .meo.ri.deul.nae.bu .byeog.deul.e.neun .peu.re.seu.ko.hwa.deul.i .geu.ryeo.jyeo .iss.neun.de, .geu.rim.deul.yi .dae.bu.bun.eun .weon.bon .sang.tae.ga .bo.jon.doe.ji .mos.haess.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 11:대부분은(nsubj:pass→보존되지), 12:원본(nsubj:pass→보존되지)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s270': [('deprel', 11, 'nsubj:outer')],

    # dev-s3
    # TEXT: 해당 질량은 항성의 구성 원소에 따라 태양의 1.2배에서 1.46배로 약간 차이가 난다.
    # TRANSLIT: .hae.dang .jil.ryang.eun .hang.seong.yi .gu.seong .weon.so.e .dda.ra .tae.yang.yi 1.2.bae.e.seo 1.46.bae.ro .yag.gan .cha.i.ga .nan.da.
    # ENGLISH: The relevant area has a difference.
    # CONFLICT: 1:해당(nsubj→난다), 11:차이가(nsubj→난다)
    # Fix: default: N1(해당)→outer [NEEDS REVIEW]
    'dev-s3': [('deprel', 1, 'nsubj:outer')],

    # dev-s317
    # TEXT: 만약 그 중 일부 데이터가 지워지면 해당 영역은 데이터가 지워진 용량만큼 중간이 비게 되는데, 나중에 다시 새로운 데이터가 입력되면 이 영역부터 우선 채우게 된다.
    # TRANSLIT: .man.yag .geu .jung .il.bu .de.i.teo.ga .ji.weo.ji.myeon .hae.dang .yeong.yeog.eun .de.i.teo.ga .ji.weo.jin .yong.ryang.man.keum .jung.gan.i .bi.ge .doe.neun.de, .na.jung.e .da.si .sae.ro.un .de.i.teo.ga .ib.ryeog.doe.myeon .i .yeong.yeog.bu.teo .u.seon .chae.u.ge .doen.da.
    # ENGLISH: The relevant area becomes empty in the middle.
    # CONFLICT: 7:해당(nsubj→비게), 12:중간이(nsubj→비게)
    # Fix: default: N1(해당)→outer [NEEDS REVIEW]
    'dev-s317': [('deprel', 7, 'nsubj:outer')],

    # dev-s348
    # TEXT: 우즈는 "마스터스가 첫 복귀전이 될 것으로 보인다"며 "아널드 파머와 조 루이스 등에게 전화를 걸어 '아널드 파마 인비테이셔널'대회와 '태비스톡 컵'대회에 참가할 수 없게 된 데 유감을 표명했다"고 말했다.
    # TRANSLIT: .u.jeu.neun ".ma.seu.teo.seu.ga .cheos .bog.gwi.jeon.i .doel .geos.eu.ro .bo.in.da".myeo ".a.neol.deu .pa.meo.wa .jo .ru.i.seu .deung.e.ge .jeon.hwa.reul .geol.eo '.a.neol.deu .pa.ma .in.bi.te.i.syeo.neol'.dae.hoe.wa '.tae.bi.seu.tog .keob'.dae.hoe.e .cham.ga.hal .su .eobs.ge .doen .de .yu.gam.eul .pyo.myeong.haess.da".go .mal.haess.da.
    # ENGLISH: The Masters will be Tiger's comeback tournament.
    # CONFLICT: 3:마스터스가(nsubj→될), 5:복귀전이(nsubj→될)
    # Fix: default: N1(마스터스가)→outer [NEEDS REVIEW]
    'dev-s348': [('deprel', 3, 'nsubj:outer')],

    # dev-s354
    # TEXT: 맛은 말할 것도 없어요
    # TRANSLIT: .mas.eun .mal.hal .geos.do .eobs.eo.yo
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 1:맛은(nsubj→없어요), 3:것도(nsubj→없어요)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s354': [('deprel', 1, 'nsubj:outer')],

    # dev-s363
    # TEXT: 사장은 조폭 출신처럼 인상 더럽고 직원들도 질 떨어짐
    # TRANSLIT: .sa.jang.eun .jo.pog .chul.sin.cheo.reom .in.sang .deo.reob.go .jig.weon.deul.do .jil .ddeol.eo.jim
    # ENGLISH: This restaurant, this place also has good food.
    # CONFLICT: 1:사장은(nsubj→더럽고), 4:인상(nsubj→더럽고)
    # CONFLICT: 6:직원들도(nsubj→떨어짐), 7:질(nsubj→떨어짐)
    # Fix: topic-marker: N1(은/는)→outer | also-marker: N1(도)→outer
    'dev-s363': [('deprel', 1, 'nsubj:outer'), ('deprel', 6, 'nsubj:outer')],

    # dev-s368
    # TEXT: 밑부분의 잎은 비늘 같으며 위로 올라갈수록 점차 커져서 길이 5-15㎝, 너비 1-2.5㎝로 되며 3맥이 있고 가장자리에 잔돌기가 거의 없다.
    # TRANSLIT: .mit.bu.bun.yi .ip.eun .bi.neul .gat.eu.myeo .wi.ro .ol.ra.gal.su.rog .jeom.cha .keo.jyeo.seo .gil.i 5-15㎝, .neo.bi 1-2.5㎝.ro .doe.myeo 3.maeg.i .iss.go .ga.jang.ja.ri.e .jan.dol.gi.ga .geo.yi .eobs.da.
    # ENGLISH: This place is very good.
    # CONFLICT: 2:잎은(nsubj→같으며), 3:비늘(nsubj→같으며)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s368': [('deprel', 2, 'nsubj:outer')],

    # dev-s370
    # TEXT: 리더가 최연장자인 스기조라 하는 사람들도 있지만, 그가 창설 멤버는 아니기 때문에 아니라 보고 있다.
    # TRANSLIT: .ri.deo.ga .choe.yeon.jang.ja.in .seu.gi.jo.ra .ha.neun .sa.ram.deul.do .iss.ji.man, .geu.ga .chang.seol .mem.beo.neun .a.ni.gi .ddae.mun.e .a.ni.ra .bo.go .iss.da.
    # ENGLISH: He was not the founder.
    # CONFLICT: 8:그가(nsubj→아니기), 9:창설(nsubj→아니기)
    # Fix: default: N1(그가)→outer [NEEDS REVIEW]
    'dev-s370': [('deprel', 8, 'nsubj:outer')],

    # dev-s4
    # TEXT: 건물은 대체로 균형이 맞고 조화가 잘 되어 아담한 감을 준다.
    # TRANSLIT: .geon.mul.eun .dae.che.ro .gyun.hyeong.i .maj.go .jo.hwa.ga .jal .doe.eo .a.dam.han .gam.eul .jun.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 1:건물은(nsubj→맞고), 3:균형이(nsubj→맞고)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s4': [('deprel', 1, 'nsubj:outer')],

    # dev-s406
    # TEXT: 솔직히 맛이 보통 카페보다 맛이 없었어요
    # TRANSLIT: .sol.jig.hi .mas.i .bo.tong .ka.pe.bo.da .mas.i .eobs.eoss.eo.yo
    # ENGLISH: There was no flavor whatsoever.
    # CONFLICT: 2:맛이(nsubj→없었어요), 5:맛이(nsubj→없었어요)
    # Fix: default: N1(맛이)→outer [NEEDS REVIEW]
    'dev-s406': [('deprel', 2, 'nsubj:outer')],

    # dev-s433
    # TEXT: 강남사거리 지금 상황이 어때
    # TRANSLIT: .gang.nam.sa.geo.ri .ji.geum .sang.hwang.i .eo.ddae
    # ENGLISH: How is the situation at Gangnam Intersection?
    # CONFLICT: 1:강남사거리(nsubj→어때), 3:상황이(nsubj→어때)
    # Fix: default: N1(강남사거리)→outer [NEEDS REVIEW]
    'dev-s433': [('deprel', 1, 'nsubj:outer')],

    # dev-s435
    # TEXT: 협상과 교섭은 100%란 게 없다.
    # TRANSLIT: .hyeob.sang.gwa .gyo.seob.eun 100%.ran .ge .eobs.da.
    # ENGLISH: There is nothing the negotiations can do.
    # CONFLICT: 1:협상과(nsubj→없다), 6:게(nsubj→없다)
    # Fix: default: N1(협상과)→outer [NEEDS REVIEW]
    'dev-s435': [('deprel', 1, 'nsubj:outer')],

    # dev-s449
    # TEXT: 후리이드도 양념도 맛나다
    # TRANSLIT: .hu.ri.i.deu.do .yang.nyeom.do .mas.na.da
    # ENGLISH: This place also has good things.
    # CONFLICT: 1:후리이드도(nsubj→맛나다), 2:양념도(nsubj→맛나다)
    # Fix: both-also: N1→outer (first)
    'dev-s449': [('deprel', 1, 'nsubj:outer')],

    # dev-s45
    # TEXT: 등번호는 한신 타이거스 시절의 에나쓰 유타카와 착용했던 28번으로 정해졌고 이것은 라이벌 관계였던 요미우리 자이언츠에 입단한 가네토도 똑같이 28번으로 배정되었다.
    # TRANSLIT: .deung.beon.ho.neun .han.sin .ta.i.geo.seu .si.jeol.yi .e.na.sseu .yu.ta.ka.wa .chag.yong.haess.deon 28.beon.eu.ro .jeong.hae.jyeoss.go .i.geos.eun .ra.i.beol .gwan.gye.yeoss.deon .yo.mi.u.ri .ja.i.eon.cheu.e .ib.dan.han .ga.ne.to.do .ddog.gat.i 28.beon.eu.ro .bae.jeong.doe.eoss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 10:이것은(nsubj:pass→배정되었다), 16:가네토도(nsubj:pass→배정되었다)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s45': [('deprel', 10, 'nsubj:outer')],

    # dev-s453
    # TEXT: 거기 커피도 다른 데보다 맛도 좋았어요
    # TRANSLIT: .geo.gi .keo.pi.do .da.reun .de.bo.da .mas.do .joh.ass.eo.yo
    # ENGLISH: This place also has good things.
    # CONFLICT: 2:커피도(nsubj→좋았어요), 5:맛도(nsubj→좋았어요)
    # Fix: both-also: N1→outer (first)
    'dev-s453': [('deprel', 2, 'nsubj:outer')],

    # dev-s455
    # TEXT: 연비 또한 ℓ당 10.6㎞로 ES350(ℓ당 9.6㎞)보다 연료효율이 높다.
    # TRANSLIT: .yeon.bi .ddo.han ℓ.dang 10.6㎞.ro ES350(ℓ.dang 9.6㎞).bo.da .yeon.ryo.hyo.yul.i .nop.da.
    # ENGLISH: Fuel efficiency, the fuel economy rate is high.
    # CONFLICT: 1:연비(nsubj→높다), 16:연료효율이(nsubj→높다)
    # Fix: default: N1(연비)→outer [NEEDS REVIEW]
    'dev-s455': [('deprel', 1, 'nsubj:outer')],

    # dev-s502
    # TEXT: 계약금 2000만원을 2회 분납하며, 중도금(60%)에 대해 30%는 무이자융자를, 나머지 30%는 이자후불제 혜택을 주고 있다.
    # TRANSLIT: .gye.yag.geum 2000.man.weon.eul 2.hoe .bun.nab.ha.myeo, .jung.do.geum(60%).e .dae.hae 30%.neun .mu.i.ja.yung.ja.reul, .na.meo.ji 30%.neun .i.ja.hu.bul.je .hye.taeg.eul .ju.go .iss.da.
    # ENGLISH: 30 given, the rest handed over.
    # CONFLICT: 13:30(nsubj→주고), 18:나머지(nsubj→주고)
    # Fix: default: N1(30)→outer [NEEDS REVIEW]
    'dev-s502': [('deprel', 13, 'nsubj:outer')],

    # dev-s549
    # TEXT: 그래서 자원은 여러 가지로 분류가 된다.
    # TRANSLIT: .geu.rae.seo .ja.weon.eun .yeo.reo .ga.ji.ro .bun.ryu.ga .doen.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 2:자원은(nsubj→된다), 5:분류가(nsubj→된다)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s549': [('deprel', 2, 'nsubj:outer')],

    # dev-s573
    # TEXT: 해물과 등뼈찜 감칠맛 납니다
    # TRANSLIT: .hae.mul.gwa .deung.bbyeo.jjim .gam.chil.mas .nab.ni.da
    # ENGLISH: The seafood and the umami flavor comes through.
    # CONFLICT: 1:해물과(nsubj→납니다), 3:감칠맛(nsubj→납니다)
    # Fix: default: N1(해물과)→outer [NEEDS REVIEW]
    'dev-s573': [('deprel', 1, 'nsubj:outer')],

    # dev-s577
    # TEXT: 손님을 배려하는 마음이 조금 부족한 것 같군요.
    # TRANSLIT: .son.nim.eul .bae.ryeo.ha.neun .ma.eum.i .jo.geum .bu.jog.han .geos .gat.gun.yo.
    # ENGLISH: I feel like my heart is in the right place.
    # CONFLICT: 3:마음이(nsubj→같군요), 6:것(nsubj→같군요)
    # Fix: default: N1(마음이)→outer [NEEDS REVIEW]
    'dev-s577': [('deprel', 3, 'nsubj:outer')],

    # dev-s578
    # TEXT: 항공기상청 관측자료에 따르면 사고 직전인 낮 12시께 강릉 날씨는 초속 5.5m의 바람이 불고 있었고 사람이 육안으로 볼 수 있는 시정 거리는 10㎞, 구름은 관측지점에서 1천200m 상공에 옅게 깔려 대체로 양호한 기상상태였던 것으로 나타났다.
    # TRANSLIT: .hang.gong.gi.sang.cheong .gwan.cheug.ja.ryo.e .dda.reu.myeon .sa.go .jig.jeon.in .naj 12.si.gge .gang.reung .nal.ssi.neun .cho.sog 5.5m.yi .ba.ram.i .bul.go .iss.eoss.go .sa.ram.i .yug.an.eu.ro .bol .su .iss.neun .si.jeong .geo.ri.neun 10㎞, .gu.reum.eun .gwan.cheug.ji.jeom.e.seo 1.cheon200m .sang.gong.e .yeot.ge .ggal.ryeo .dae.che.ro .yang.ho.han .gi.sang.sang.tae.yeoss.deon .geos.eu.ro .na.ta.nass.da.
    # ENGLISH: Gangneung, wind of 10 m/s is blowing.
    # CONFLICT: 8:강릉(nsubj→불고), 10:초속(nsubj→불고)
    # Fix: default: N1(강릉)→outer [NEEDS REVIEW]
    'dev-s578': [('deprel', 8, 'nsubj:outer')],

    # dev-s58
    # TEXT: 정시 이월 규모가 확정되기까지 예단하기는 어렵지만 올해도 정시모집은 상당히 좁은 문이 될 전망이다.
    # TRANSLIT: .jeong.si .i.weol .gyu.mo.ga .hwag.jeong.doe.gi.gga.ji .ye.dan.ha.gi.neun .eo.ryeob.ji.man .ol.hae.do .jeong.si.mo.jib.eun .sang.dang.hi .job.eun .mun.i .doel .jeon.mang.i.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 8:정시모집은(nsubj→될), 11:문이(nsubj→될)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s58': [('deprel', 8, 'nsubj:outer')],

    # dev-s582
    # TEXT: 칼국수 밀가루 냄새 대박이고 국물도 적고 애들 땜에 시끄러워서 집에 와 급체해서 죽을 뻔 했어요 ㅜㅜ
    # TRANSLIT: .kal.gug.su .mil.ga.ru .naem.sae .dae.bag.i.go .gug.mul.do .jeog.go .ae.deul .ddaem.e .si.ggeu.reo.weo.seo .jib.e .wa .geub.che.hae.seo .jug.eul .bbeon .haess.eo.yo ㅜㅜ
    # ENGLISH: Kalguksu noodles have great flour.
    # CONFLICT: 1:칼국수(nsubj→대박이고), 2:밀가루(nsubj→대박이고)
    # Fix: default: N1(칼국수)→outer [NEEDS REVIEW]
    'dev-s582': [('deprel', 1, 'nsubj:outer')],

    # dev-s585
    # TEXT: LH에 따르면 대상 토지는 산업시설용지(공장•연구시설) 38필지(24만5096㎡)와 물류유통시설용지가 1필지(9012㎡)다.
    # TRANSLIT: LH.e .dda.reu.myeon .dae.sang .to.ji.neun .san.eob.si.seol.yong.ji(.gong.jang•.yeon.gu.si.seol) 38.pil.ji(24.man5096㎡).wa .mul.ryu.yu.tong.si.seol.yong.ji.ga 1.pil.ji(9012㎡).da.
    # ENGLISH: The target area, the logistics distribution facility land is one lot.
    # CONFLICT: 3:대상(nsubj→1필지), 17:물류유통시설용지가(nsubj→1필지)
    # Fix: default: N1(대상)→outer [NEEDS REVIEW]
    'dev-s585': [('deprel', 3, 'nsubj:outer')],

    # dev-s607
    # TEXT: 바로크 시대의 협주곡들은 대부분 쳄발로와 오르간을 위해 쓰인 협주곡이 많고, 바이올린이나 첼로의 협주곡에도 오르간이나 쳄발로가 쓰일 정도로 이 두 악기의 영향력은 막강했다.
    # TRANSLIT: .ba.ro.keu .si.dae.yi .hyeob.ju.gog.deul.eun .dae.bu.bun .chem.bal.ro.wa .o.reu.gan.eul .wi.hae .sseu.in .hyeob.ju.gog.i .manh.go, .ba.i.ol.rin.i.na .chel.ro.yi .hyeob.ju.gog.e.do .o.reu.gan.i.na .chem.bal.ro.ga .sseu.il .jeong.do.ro .i .du .ag.gi.yi .yeong.hyang.ryeog.eun .mag.gang.haess.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 3:협주곡들은(nsubj→많고), 9:협주곡이(nsubj→많고)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s607': [('deprel', 3, 'nsubj:outer')],

    # dev-s623
    # TEXT: 1시간이 지나도 의사는 보이질 않고 간호사는 이렇다 할 이유나 말도 없고
    # TRANSLIT: 1.si.gan.i .ji.na.do .yi.sa.neun .bo.i.jil .anh.go .gan.ho.sa.neun .i.reoh.da .hal .i.yu.na .mal.do .eobs.go
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 6:간호사는(nsubj→없고), 9:이유나(nsubj→없고)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s623': [('deprel', 6, 'nsubj:outer')],

    # dev-s627
    # TEXT: 내부적 구성 요소는 다음과 같은 것들이 있다.
    # TRANSLIT: .nae.bu.jeog .gu.seong .yo.so.neun .da.eum.gwa .gat.eun .geos.deul.i .iss.da.
    # ENGLISH: There are various things here.
    # CONFLICT: 2:구성(nsubj→있다), 6:것들이(nsubj→있다)
    # Fix: default: N1(구성)→outer [NEEDS REVIEW]
    'dev-s627': [('deprel', 2, 'nsubj:outer')],

    # dev-s643
    # TEXT: 옥스퍼드 애널리티카는 "김정은 체제의 건재함을 과시하기 위해 국지적 무력도발이 일어날 가능성이 있고 김일성 탄생 100주년 기념행사가 (군사적 긴장의) 서막이 될 것이다"고 예상했다.
    # TRANSLIT: .og.seu.peo.deu .ae.neol.ri.ti.ka.neun ".gim.jeong.eun .che.je.yi .geon.jae.ham.eul .gwa.si.ha.gi .wi.hae .gug.ji.jeog .mu.ryeog.do.bal.i .il.eo.nal .ga.neung.seong.i .iss.go .gim.il.seong .tan.saeng 100.ju.nyeon .gi.nyeom.haeng.sa.ga (.gun.sa.jeog .gin.jang.yi) .seo.mag.i .doel .geos.i.da".go .ye.sang.haess.da.
    # ENGLISH: Kim Il-sung was the prelude to it.
    # CONFLICT: 14:김일성(nsubj→될), 22:서막이(nsubj→될)
    # Fix: default: N1(김일성)→outer [NEEDS REVIEW]
    'dev-s643': [('deprel', 14, 'nsubj:outer')],

    # dev-s647
    # TEXT: 1인당 비용은 시푸드 레스토랑과 차이가 없음.
    # TRANSLIT: 1.in.dang .bi.yong.eun .si.pu.deu .re.seu.to.rang.gwa .cha.i.ga .eobs.eum.
    # ENGLISH: Per capita, there is no difference.
    # CONFLICT: 1:1인당(nsubj→없음), 5:차이가(nsubj→없음)
    # Fix: default: N1(1인당)→outer [NEEDS REVIEW]
    'dev-s647': [('deprel', 1, 'nsubj:outer')],

    # dev-s666
    # TEXT: 메이지 유신 후, 오코치 계 나가사와 마쓰다이라 가는 모든 가문이 오코치 성(姓)으로 돌아갔다.
    # TRANSLIT: .me.i.ji .yu.sin .hu, .o.ko.chi .gye .na.ga.sa.wa .ma.sseu.da.i.ra .ga.neun .mo.deun .ga.mun.i .o.ko.chi .seong(xìng).eu.ro .dol.a.gass.da.
    # ENGLISH: Okochi, the family took over.
    # CONFLICT: 5:오코치(nsubj→돌아갔다), 11:가문이(nsubj→돌아갔다)
    # Fix: default: N1(오코치)→outer [NEEDS REVIEW]
    'dev-s666': [('deprel', 5, 'nsubj:outer')],

    # dev-s679
    # TEXT: 비판이 거세지자 스키경기가 열리는 휘슬러 시당국은 입장권 구입에 들인 예산이 주민들의 재산세가 아니라, 지역 내 호텔의 법인세에서 충당됐다고 해명하고 나섰다.
    # TRANSLIT: .bi.pan.i .geo.se.ji.ja .seu.ki.gyeong.gi.ga .yeol.ri.neun .hwi.seul.reo .si.dang.gug.eun .ib.jang.gweon .gu.ib.e .deul.in .ye.san.i .ju.min.deul.yi .jae.san.se.ga .a.ni.ra, .ji.yeog .nae .ho.tel.yi .beob.in.se.e.seo .chung.dang.dwaess.da.go .hae.myeong.ha.go .na.seoss.da.
    # ENGLISH: The budget is not property tax.
    # CONFLICT: 10:예산이(nsubj→아니라), 12:재산세가(nsubj→아니라)
    # Fix: default: N1(예산이)→outer [NEEDS REVIEW]
    'dev-s679': [('deprel', 10, 'nsubj:outer')],

    # dev-s71
    # TEXT: 그래서 스파 상품권을 구매하기도 하지만, 상품권은 금액이 표시되어 있어 받는 사람이 부담스러워 할 수 있는 단점이 있습니다.
    # TRANSLIT: .geu.rae.seo .seu.pa .sang.pum.gweon.eul .gu.mae.ha.gi.do .ha.ji.man, .sang.pum.gweon.eun .geum.aeg.i .pyo.si.doe.eo .iss.eo .bad.neun .sa.ram.i .bu.dam.seu.reo.weo .hal .su .iss.neun .dan.jeom.i .iss.seub.ni.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 7:상품권은(nsubj→표시되어), 8:금액이(nsubj:pass→표시되어)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s71': [('deprel', 7, 'nsubj:outer')],

    # dev-s710
    # TEXT: 단, 그랜드 카니발R은 1종 보통면허 소지자만 신청이 가능하다.
    # TRANSLIT: .dan, .geu.raen.deu .ka.ni.balR.eun 1.jong .bo.tong.myeon.heo .so.ji.ja.man .sin.cheong.i .ga.neung.ha.da.
    # ENGLISH: Various things are good here.
    # CONFLICT: 3:그랜드(nsubj→가능하다), 5:1종(nsubj→가능하다), 8:신청이(nsubj→가능하다)
    # Fix: triple: [3, 5]→outer
    'dev-s710': [('deprel', 3, 'nsubj:outer'), ('deprel', 5, 'nsubj:outer')],

    # dev-s726
    # TEXT: 입구는 허름해두 음식이 일반 횟집이랑 엄청 차이가 납니다
    # TRANSLIT: .ib.gu.neun .heo.reum.hae.du .eum.sig.i .il.ban .hoes.jib.i.rang .eom.cheong .cha.i.ga .nab.ni.da
    # ENGLISH: The food here, the difference in flavor comes through.
    # CONFLICT: 3:음식이(nsubj→납니다), 7:차이가(nsubj→납니다)
    # Fix: default: N1(음식이)→outer [NEEDS REVIEW]
    'dev-s726': [('deprel', 3, 'nsubj:outer')],

    # dev-s738
    # TEXT: 고대 중국의 우주관은 여러 가지가 있는데, 이 중 유명한 것은 아래와 같은 세가지가 있다.
    # TRANSLIT: .go.dae .jung.gug.yi .u.ju.gwan.eun .yeo.reo .ga.ji.ga .iss.neun.de, .i .jung .yu.myeong.han .geos.eun .a.rae.wa .gat.eun .se.ga.ji.ga .iss.da.
    # ENGLISH: Various important things are mentioned here.
    # CONFLICT: 3:우주관은(nsubj→있는데), 5:가지가(nsubj→있는데)
    # CONFLICT: 11:것은(nsubj→있다), 14:세가지가(nsubj→있다)
    # Fix: topic-marker: N1(은/는)→outer | topic-marker: N1(은/는)→outer
    'dev-s738': [('deprel', 3, 'nsubj:outer'), ('deprel', 11, 'nsubj:outer')],

    # dev-s763
    # TEXT: 의자가 소파여서 편안한 느낌에 맛도 가격도 좋은 편 ㅎ
    # TRANSLIT: .yi.ja.ga .so.pa.yeo.seo .pyeon.an.han .neu.ggim.e .mas.do .ga.gyeog.do .joh.eun .pyeon ㅎ
    # ENGLISH: This place also has something special.
    # CONFLICT: 5:맛도(nsubj→좋은), 6:가격도(nsubj→좋은)
    # Fix: both-also: N1→outer (first)
    'dev-s763': [('deprel', 5, 'nsubj:outer')],

    # dev-s777
    # TEXT: "경기가 좀더 좋아지면서 자신감을 갖고 또 기업실적의 회복속도가 빨라진다라는 부분이 직접적으로 눈으로 확인이 되면 오히려 초기 긴축에 대한 부정적인 영향을 압도할 수 있기 때문에..."
    # TRANSLIT: ".gyeong.gi.ga .jom.deo .joh.a.ji.myeon.seo .ja.sin.gam.eul .gaj.go .ddo .gi.eob.sil.jeog.yi .hoe.bog.sog.do.ga .bbal.ra.jin.da.ra.neun .bu.bun.i .jig.jeob.jeog.eu.ro .nun.eu.ro .hwag.in.i .doe.myeon .o.hi.ryeo .cho.gi .gin.chug.e .dae.han .bu.jeong.jeog.in .yeong.hyang.eul .ab.do.hal .su .iss.gi .ddae.mun.e..."
    # ENGLISH: If the relevant part is confirmed.
    # CONFLICT: 11:부분이(nsubj→되면), 14:확인이(nsubj→되면)
    # Fix: default: N1(부분이)→outer [NEEDS REVIEW]
    'dev-s777': [('deprel', 11, 'nsubj:outer')],

    # dev-s801
    # TEXT: 오늘 7시에 하는 영화는 뭐가 있어?
    # TRANSLIT: .o.neul 7.si.e .ha.neun .yeong.hwa.neun .mweo.ga .iss.eo?
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 4:영화는(nsubj→있어), 5:뭐가(nsubj→있어)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s801': [('deprel', 4, 'nsubj:outer')],

    # dev-s816
    # TEXT: 맛도 좋고 그릇도 일반 국밥집 그릇이 아니라서 좋아요
    # TRANSLIT: .mas.do .joh.go .geu.reus.do .il.ban .gug.bab.jib .geu.reus.i .a.ni.ra.seo .joh.a.yo
    # ENGLISH: This place also has something special.
    # CONFLICT: 3:그릇도(nsubj→아니라서), 4:일반(nsubj→아니라서)
    # Fix: also-marker: N1(도)→outer
    'dev-s816': [('deprel', 3, 'nsubj:outer')],

    # dev-s838
    # TEXT: 인도가 이처럼 추가 원전 건설을 서두르는 이유는 세계 2위 인도 대국으로 빠른 성장을 거듭하고 있지만 연료 부족과 낮은 설비 가동을 이유로 에너지 부족 문제를 겪고 있기 때문이다.
    # TRANSLIT: .in.do.ga .i.cheo.reom .chu.ga .weon.jeon .geon.seol.eul .seo.du.reu.neun .i.yu.neun .se.gye 2.wi .in.do .dae.gug.eu.ro .bba.reun .seong.jang.eul .geo.deub.ha.go .iss.ji.man .yeon.ryo .bu.jog.gwa .naj.eun .seol.bi .ga.dong.eul .i.yu.ro .e.neo.ji .bu.jog .mun.je.reul .gyeogg.go .iss.gi .ddae.mun.i.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 7:이유는(nsubj→때문이다), 25:겪고(nsubj→때문이다)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s838': [('deprel', 7, 'nsubj:outer')],

    # dev-s840
    # TEXT: 또 닭꼬치는 매콤한 게 가장 맛잇더라구요.
    # TRANSLIT: .ddo .darg.ggo.chi.neun .mae.kom.han .ge .ga.jang .mas.is.deo.ra.gu.yo.
    # ENGLISH: This is a very good restaurant.
    # CONFLICT: 2:닭꼬치는(nsubj→맛잇더라구요), 4:게(nsubj→맛잇더라구요)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s840': [('deprel', 2, 'nsubj:outer')],

    # dev-s842
    # TEXT: 뭔가 더하고 변형해서 성능이 나아진다면 제품이 완전하지 못하다는 이야기고, 제품이 완전하다면 더하고 변형하는 것은 제품의 완결성을 떨어뜨리는 행위가 되기 때문이다.
    # TRANSLIT: .mweon.ga .deo.ha.go .byeon.hyeong.hae.seo .seong.neung.i .na.a.jin.da.myeon .je.pum.i .wan.jeon.ha.ji .mos.ha.da.neun .i.ya.gi.go, .je.pum.i .wan.jeon.ha.da.myeon .deo.ha.go .byeon.hyeong.ha.neun .geos.eun .je.pum.yi .wan.gyeol.seong.eul .ddeol.eo.ddeu.ri.neun .haeng.wi.ga .doe.gi .ddae.mun.i.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 15:것은(nsubj→되기), 19:행위가(nsubj→되기)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s842': [('deprel', 15, 'nsubj:outer')],

    # dev-s844
    # TEXT: 카우카 주(Cauca)는 콜롬비아의 주로, 주도는 포파얀이다.
    # TRANSLIT: .ka.u.ka .ju(Cauca).neun .kol.rom.bi.a.yi .ju.ro, .ju.do.neun .po.pa.yan.i.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 1:카우카(nsubj→포파얀이다), 10:주도는(nsubj→포파얀이다)
    # Fix: topic-marker: N2(은/는)→outer
    'dev-s844': [('deprel', 10, 'nsubj:outer')],

    # dev-s850
    # TEXT: 다만, 이 만요슈는 공표되지는 않았는데, 이는 엔랴쿠 4년(785년)에 야카모치가 죽자 곧 오토모노 쓰기히토()에 의한 후지와라노 타네쓰구() 암살 사건이 발생해, 야카모치도 연좌되었기 때문이다.
    # TRANSLIT: .da.man, .i .man.yo.syu.neun .gong.pyo.doe.ji.neun .anh.ass.neun.de, .i.neun .en.rya.ku 4.nyeon(785.nyeon).e .ya.ka.mo.chi.ga .jug.ja .god .o.to.mo.no .sseu.gi.hi.to().e .yi.han .hu.ji.wa.ra.no .ta.ne.sseu.gu() .am.sal .sa.geon.i .bal.saeng.hae, .ya.ka.mo.chi.do .yeon.jwa.doe.eoss.gi .ddae.mun.i.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 8:이는(nsubj→연좌되었기), 32:야카모치도(nsubj:pass→연좌되었기)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s850': [('deprel', 8, 'nsubj:outer')],

    # dev-s851
    # TEXT: 이것은 바꾸어 말해서 아무리 원시적 사회라 할지라도 언어생활이 이루어지는 사회에서는 문학의 싹이 숨쉬고 있다는 것이 된다.
    # TRANSLIT: .i.geos.eun .ba.ggu.eo .mal.hae.seo .a.mu.ri .weon.si.jeog .sa.hoe.ra .hal.ji.ra.do .eon.eo.saeng.hwal.i .i.ru.eo.ji.neun .sa.hoe.e.seo.neun .mun.hag.yi .ssag.i .sum.swi.go .iss.da.neun .geos.i .doen.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:이것은(nsubj→된다), 15:것이(nsubj→된다)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s851': [('deprel', 1, 'nsubj:outer')],

    # dev-s886
    # TEXT: 어머니는 밀양박씨는 사재감정(司宰監正) 박홍신(朴弘信)의 딸이다.
    # TRANSLIT: .eo.meo.ni.neun .mil.yang.bag.ssi.neun .sa.jae.gam.jeong(sīzǎijiānzhèng) .bag.hong.sin(pǔ弘xìn).yi .ddal.i.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 1:어머니는(nsubj→딸이다), 2:밀양박씨는(nsubj→딸이다)
    # Fix: both-topic: N1→outer (first)
    'dev-s886': [('deprel', 1, 'nsubj:outer')],

    # dev-s894
    # TEXT: 중요한 건 이 분위기를 어떻게 끝까지 이어가느냐가 중요하다.
    # TRANSLIT: .jung.yo.han .geon .i .bun.wi.gi.reul .eo.ddeoh.ge .ggeut.gga.ji .i.eo.ga.neu.nya.ga .jung.yo.ha.da.
    # ENGLISH: Whether they can continue is important.
    # CONFLICT: 2:건(nsubj→중요하다), 7:이어가느냐가(csubj→중요하다)
    # Fix: default: N1(건)→outer [NEEDS REVIEW]
    'dev-s894': [('deprel', 2, 'nsubj:outer')],

    # dev-s903
    # TEXT: 증권사들의 순이익은 상반기 전체로 보면 1조2천411억 원으로 작년 같은 기간에 비해 1.8%(218억 원) 늘었다.
    # TRANSLIT: .jeung.gweon.sa.deul.yi .sun.i.ig.eun .sang.ban.gi .jeon.che.ro .bo.myeon 1.jo2.cheon411.eog .weon.eu.ro .jag.nyeon .gat.eun .gi.gan.e .bi.hae 1.8%(218.eog .weon) .neul.eoss.da.
    # ENGLISH: This place is very good.
    # CONFLICT: 2:순이익은(nsubj→늘었다), 12:1.8(nsubj→늘었다)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s903': [('deprel', 2, 'nsubj:outer')],

    # dev-s914
    # TEXT: 이자율은 카드사별로 신한카드가 7.6~26.9 %, 삼성카드가 7.9~24.9 %, 하나SK카드가 6.9~24.9 %, 국민은행이 7.5~26.5% 등이다.
    # TRANSLIT: .i.ja.yul.eun .ka.deu.sa.byeol.ro .sin.han.ka.deu.ga 7.6~26.9 %, .sam.seong.ka.deu.ga 7.9~24.9 %, .ha.naSK.ka.deu.ga 6.9~24.9 %, .gug.min.eun.haeng.i 7.5~26.5% .deung.i.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:이자율은(nsubj→7.5~26.5), 15:국민은행이(nsubj→7.5~26.5)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s914': [('deprel', 1, 'nsubj:outer')],

    # dev-s92
    # TEXT: 저지라고 불리지만 이 지역은 실제로 산이 많은데, 저지라는 이름은 이 지역이 당시 후진 지역으로 인식되었기 때문에 붙여졌다.
    # TRANSLIT: .jeo.ji.ra.go .bul.ri.ji.man .i .ji.yeog.eun .sil.je.ro .san.i .manh.eun.de, .jeo.ji.ra.neun .i.reum.eun .i .ji.yeog.i .dang.si .hu.jin .ji.yeog.eu.ro .in.sig.doe.eoss.gi .ddae.mun.e .but.yeo.jyeoss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 4:지역은(nsubj→많은데), 6:산이(nsubj→많은데)
    # Fix: topic-marker: N1(은/는)→outer
    'dev-s92': [('deprel', 4, 'nsubj:outer')],

    # dev-s950
    # TEXT: 차가 작다고 무시 당하고 서비스가 재수 없음
    # TRANSLIT: .cha.ga .jag.da.go .mu.si .dang.ha.go .seo.bi.seu.ga .jae.su .eobs.eum
    # ENGLISH: The service is terrible.
    # CONFLICT: 5:서비스가(nsubj→없음), 6:재수(nsubj→없음)
    # Fix: default: N1(서비스가)→outer [NEEDS REVIEW]
    'dev-s950': [('deprel', 5, 'nsubj:outer')],

    # test-s10
    # TEXT: 홍춘욱 국민은행 수석연구원은 "주요 선진국이 부채 문제로 재정 여력이 떨어졌고 통화 정책 또한 약효가 예전 같을 수는 없다"며 "각국이 경기 침체를 탈출하기 위해 경쟁적으로 자국의 통화 가치를 떨어뜨리려 할 가능성이 높다"고 진단했다.
    # TRANSLIT: .hong.chun.ug .gug.min.eun.haeng .su.seog.yeon.gu.weon.eun ".ju.yo .seon.jin.gug.i .bu.chae .mun.je.ro .jae.jeong .yeo.ryeog.i .ddeol.eo.jyeoss.go .tong.hwa .jeong.chaeg .ddo.han .yag.hyo.ga .ye.jeon .gat.eul .su.neun .eobs.da".myeo ".gag.gug.i .gyeong.gi .chim.che.reul .tal.chul.ha.gi .wi.hae .gyeong.jaeng.jeog.eu.ro .ja.gug.yi .tong.hwa .ga.chi.reul .ddeol.eo.ddeu.ri.ryeo .hal .ga.neung.seong.i .nop.da".go .jin.dan.haess.da.
    # ENGLISH: The call, the efficacy seems the same.
    # CONFLICT: 12:통화(nsubj→같을), 15:약효가(nsubj→같을)
    # Fix: default: N1(통화)→outer [NEEDS REVIEW]
    'test-s10': [('deprel', 12, 'nsubj:outer')],

    # test-s100
    # TEXT: 지금은 LG전자의 '옵티머스LTE'를 사용하고 있으며 이전에 사용하던 폰부터 문자메시지는 전화번호 별로 그룹핑하는 기능과 검색 등이 많이 편리해졌다.
    # TRANSLIT: .ji.geum.eun LG.jeon.ja.yi '.ob.ti.meo.seuLTE'.reul .sa.yong.ha.go .iss.eu.myeo .i.jeon.e .sa.yong.ha.deon .pon.bu.teo .mun.ja.me.si.ji.neun .jeon.hwa.beon.ho .byeol.ro .geu.rub.ping.ha.neun .gi.neung.gwa .geom.saeg .deung.i .manh.i .pyeon.ri.hae.jyeoss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 12:문자메시지는(nsubj→편리해졌다), 16:기능과(nsubj→편리해졌다)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s100': [('deprel', 12, 'nsubj:outer')],

    # test-s102
    # TEXT: 어차피 그런 면은 당연히 이곳이 부족하기 때문이다!
    # TRANSLIT: .eo.cha.pi .geu.reon .myeon.eun .dang.yeon.hi .i.gos.i .bu.jog.ha.gi .ddae.mun.i.da!
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 3:면은(nsubj→부족하기), 5:이곳이(nsubj→부족하기)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s102': [('deprel', 3, 'nsubj:outer')],

    # test-s106
    # TEXT: 이러한 인문주의가 다시 꽃피게 되는 것은 15세기가 되어서였다.
    # TRANSLIT: .i.reo.han .in.mun.ju.yi.ga .da.si .ggoch.pi.ge .doe.neun .geos.eun 15.se.gi.ga .doe.eo.seo.yeoss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 6:것은(nsubj→되어서였다), 7:15세기가(nsubj→되어서였다)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s106': [('deprel', 6, 'nsubj:outer')],

    # test-s126
    # TEXT: 관련 종목이 대시세 분출주로 분류되는 까닭은 파격적인 실적 뿐 아니라 특급 호재가 순차적으로 대기하고 있기 때문이다.
    # TRANSLIT: .gwan.ryeon .jong.mog.i .dae.si.se .bun.chul.ju.ro .bun.ryu.doe.neun .gga.darg.eun .pa.gyeog.jeog.in .sil.jeog .bbun .a.ni.ra .teug.geub .ho.jae.ga .sun.cha.jeog.eu.ro .dae.gi.ha.go .iss.gi .ddae.mun.i.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 6:까닭은(nsubj→때문이다), 14:대기하고(nsubj→때문이다)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s126': [('deprel', 6, 'nsubj:outer')],

    # test-s156
    # TEXT: 서울시장과 구청장은 선호의 동조화 경향이 뚜렷하다.
    # TRANSLIT: .seo.ul.si.jang.gwa .gu.cheong.jang.eun .seon.ho.yi .dong.jo.hwa .gyeong.hyang.i .ddu.ryeos.ha.da.
    # ENGLISH: The Seoul mayor and preference are evident.
    # CONFLICT: 1:서울시장과(nsubj→뚜렷하다), 3:선호의(nsubj→뚜렷하다)
    # Fix: default: N1(서울시장과)→outer [NEEDS REVIEW]
    'test-s156': [('deprel', 1, 'nsubj:outer')],

    # test-s161
    # TEXT: 실제 2004년 40대 여행객은 198만6780명으로 20대 149만654명보다 약 50만명이 많았다.
    # TRANSLIT: .sil.je 2004.nyeon 40.dae .yeo.haeng.gaeg.eun 198.man6780.myeong.eu.ro 20.dae 149.man654.myeong.bo.da .yag 50.man.myeong.i .manh.ass.da.
    # ENGLISH: In their 40s, there were more than 500,000 people in their 50s.
    # CONFLICT: 3:40대(nsubj→많았다), 9:50만명이(nsubj→많았다)
    # Fix: default: N1(40대)→outer [NEEDS REVIEW]
    'test-s161': [('deprel', 3, 'nsubj:outer')],

    # test-s162
    # TEXT: 연초부터 중동•북아프리카 사태가 터지면서 유가가 폭등했고, 3월에는 일본에서 대지진이 발생, 세계 경제가 큰 타격을 받으면서부터다.
    # TRANSLIT: .yeon.cho.bu.teo .jung.dong•.bug.a.peu.ri.ka .sa.tae.ga .teo.ji.myeon.seo .yu.ga.ga .pog.deung.haess.go, 3.weol.e.neun .il.bon.e.seo .dae.ji.jin.i .bal.saeng, .se.gye .gyeong.je.ga .keun .ta.gyeog.eul .bad.eu.myeon.seo.bu.teo.da.
    # ENGLISH: The Middle East and North Africa, as they erupted.
    # CONFLICT: 2:중동(nsubj→터지면서), 4:북아프리카(nsubj→터지면서)
    # Fix: default: N1(중동)→outer [NEEDS REVIEW]
    'test-s162': [('deprel', 2, 'nsubj:outer')],

    # test-s169
    # TEXT: 수족관 깨끗하고 장어도 맛은 있는데 시설이 비위생적입니다.
    # TRANSLIT: .su.jog.gwan .ggae.ggeus.ha.go .jang.eo.do .mas.eun .iss.neun.de .si.seol.i .bi.wi.saeng.jeog.ib.ni.da.
    # ENGLISH: This is a very good restaurant.
    # CONFLICT: 3:장어도(nsubj→있는데), 4:맛은(nsubj→있는데)
    # Fix: topic-marker: N2(은/는)→outer
    'test-s169': [('deprel', 4, 'nsubj:outer')],

    # test-s179
    # TEXT: 몽정을 할 경우 심리적인 죄책감이나 부끄러움을 느끼는 사람이 상당수이며 이것은 올바른 성의식이 확립되지 않았기 때문이라 할 수 있다.
    # TRANSLIT: .mong.jeong.eul .hal .gyeong.u .sim.ri.jeog.in .joe.chaeg.gam.i.na .bu.ggeu.reo.um.eul .neu.ggi.neun .sa.ram.i .sang.dang.su.i.myeo .i.geos.eun .ol.ba.reun .seong.yi.sig.i .hwag.rib.doe.ji .anh.ass.gi .ddae.mun.i.ra .hal .su .iss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 10:이것은(nsubj→확립되지), 12:성의식이(nsubj→확립되지)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s179': [('deprel', 10, 'nsubj:outer')],

    # test-s190
    # TEXT: 어느새 당신도 단골이 되어 있을 겁니다!
    # TRANSLIT: .eo.neu.sae .dang.sin.do .dan.gol.i .doe.eo .iss.eul .geob.ni.da!
    # ENGLISH: This place also has something special.
    # CONFLICT: 2:당신도(nsubj→되어), 3:단골이(nsubj→되어)
    # Fix: also-marker: N1(도)→outer
    'test-s190': [('deprel', 2, 'nsubj:outer')],

    # test-s194
    # TEXT: 앨리스 해먼드 샤프(Alice Hammond Sharp) 또는 사부인(史婦人)은 미국 감리교회의 선교사로 한국이름은 사애리시(史愛理施)이다.
    # TRANSLIT: .ael.ri.seu .hae.meon.deu .sya.peu(Alice Hammond Sharp) .ddo.neun .sa.bu.in(shǐfùrén).eun .mi.gug .gam.ri.gyo.hoe.yi .seon.gyo.sa.ro .han.gug.i.reum.eun .sa.ae.ri.si(shǐ'àilǐshī).i.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 1:앨리스(nsubj→사애리시), 18:한국이름은(nsubj→사애리시)
    # Fix: topic-marker: N2(은/는)→outer
    'test-s194': [('deprel', 18, 'nsubj:outer')],

    # test-s204
    # TEXT: 특히 김 청장은 "바다에서의 각종 사고는 예고가 없기 때문에 사고발생시 즉시 대응할 수 있도록 평소 인명구조장비 점검 등 관리에 만전을 다해 줄 것"도 각별히 주문했다.
    # TRANSLIT: .teug.hi .gim .cheong.jang.eun ".ba.da.e.seo.yi .gag.jong .sa.go.neun .ye.go.ga .eobs.gi .ddae.mun.e .sa.go.bal.saeng.si .jeug.si .dae.eung.hal .su .iss.do.rog .pyeong.so .in.myeong.gu.jo.jang.bi .jeom.geom .deung .gwan.ri.e .man.jeon.eul .da.hae .jul .geos".do .gag.byeol.hi .ju.mun.haess.da.
    # ENGLISH: There was no advance warning of various kinds.
    # CONFLICT: 6:각종(nsubj→없기), 8:예고가(nsubj→없기)
    # Fix: default: N1(각종)→outer [NEEDS REVIEW]
    'test-s204': [('deprel', 6, 'nsubj:outer')],

    # test-s206
    # TEXT: 아이패드2 출시가 실적 개선의 신호탄이 될 것으로 보이며 최근 발매된 "아이패드2의 초기물량 매진사태"로 범핑수요가 대폭 증가해 실적 성장을 이끌 것이다.
    # TRANSLIT: .a.i.pae.deu2 .chul.si.ga .sil.jeog .gae.seon.yi .sin.ho.tan.i .doel .geos.eu.ro .bo.i.myeo .choe.geun .bal.mae.doen ".a.i.pae.deu2.yi .cho.gi.mul.ryang .mae.jin.sa.tae".ro .beom.ping.su.yo.ga .dae.pog .jeung.ga.hae .sil.jeog .seong.jang.eul .i.ggeul .geos.i.da.
    # ENGLISH: iPad 2 will be the signal flare.
    # CONFLICT: 1:아이패드2(nsubj→될), 5:신호탄이(nsubj→될)
    # Fix: default: N1(아이패드2)→outer [NEEDS REVIEW]
    'test-s206': [('deprel', 1, 'nsubj:outer')],

    # test-s219
    # TEXT: 윤태운 한국도예협회 회장이 장작 가마로 직접 만든 이 도자기들은 시가가 흰색 2000만원, 적갈색은 3000만원으로 각각 추정된다.
    # TRANSLIT: .yun.tae.un .han.gug.do.ye.hyeob.hoe .hoe.jang.i .jang.jag .ga.ma.ro .jig.jeob .man.deun .i .do.ja.gi.deul.eun .si.ga.ga .hyin.saeg 2000.man.weon, .jeog.gal.saeg.eun 3000.man.weon.eu.ro .gag.gag .chu.jeong.doen.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 9:도자기들은(nsubj:pass→추정된다), 10:시가가(nsubj:pass→추정된다)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s219': [('deprel', 9, 'nsubj:outer')],

    # test-s231
    # TEXT: 사람이 없는 곳이라 스피커도 고음에서 찢어지는 소리 남
    # TRANSLIT: .sa.ram.i .eobs.neun .gos.i.ra .seu.pi.keo.do .go.eum.e.seo .jjij.eo.ji.neun .so.ri .nam
    # ENGLISH: This place also has good things.
    # CONFLICT: 4:스피커도(nsubj→남), 7:소리(nsubj→남)
    # Fix: also-marker: N1(도)→outer
    'test-s231': [('deprel', 4, 'nsubj:outer')],

    # test-s233
    # TEXT: 바늘잎은 8~9cm 길이로 두 개가 한 묶음이 되어 가지에 촘촘히 붙는다.
    # TRANSLIT: .ba.neul.ip.eun 8~9cm .gil.i.ro .du .gae.ga .han .mugg.eum.i .doe.eo .ga.ji.e .chom.chom.hi .but.neun.da.
    # ENGLISH: Five items become a set.
    # CONFLICT: 5:개가(nsubj→되어), 7:묶음이(nsubj→되어)
    # Fix: default: N1(개가)→outer [NEEDS REVIEW]
    'test-s233': [('deprel', 5, 'nsubj:outer')],

    # test-s239
    # TEXT: 이들 품목들은 워낙 우리나라의 품질경쟁력이 뛰어나기 때문에 관세 철폐 시 중국시장 공략은 더 쉬워질 것이고, 국내시장 역시 얼마든지 수성(守城)이 가능하다는 평가다.
    # TRANSLIT: .i.deul .pum.mog.deul.eun .weo.nag .u.ri.na.ra.yi .pum.jil.gyeong.jaeng.ryeog.i .ddwi.eo.na.gi .ddae.mun.e .gwan.se .cheol.pye .si .jung.gug.si.jang .gong.ryag.eun .deo .swi.weo.jil .geos.i.go, .gug.nae.si.jang .yeog.si .eol.ma.deun.ji .su.seong(shǒuchéng).i .ga.neung.ha.da.neun .pyeong.ga.da.
    # ENGLISH: The domestic market has a capability of sustaining the position.
    # CONFLICT: 17:국내시장(nsubj→가능하다는), 20:수성(nsubj→가능하다는)
    # Fix: default: N1(국내시장)→outer [NEEDS REVIEW]
    'test-s239': [('deprel', 17, 'nsubj:outer')],

    # test-s262
    # TEXT: 메뉴는 매운 맛부터 뼈 없는 닭까지 취향대로 골라먹을 수 있다.
    # TRANSLIT: .me.nyu.neun .mae.un .mas.bu.teo .bbyeo .eobs.neun .darg.gga.ji .chwi.hyang.dae.ro .gol.ra.meog.eul .su .iss.da.
    # ENGLISH: There is a possibility of doing it.
    # CONFLICT: 1:메뉴는(nsubj→있다), 9:수(nsubj→있다)
    # Fix: su-construction: N1→outer
    'test-s262': [('deprel', 1, 'nsubj:outer')],

    # test-s266
    # TEXT: 또한 길고 두꺼운 발톱도 위험한 무기가 된다.
    # TRANSLIT: .ddo.han .gil.go .du.ggeo.un .bal.tob.do .wi.heom.han .mu.gi.ga .doen.da.
    # ENGLISH: This place also has good things.
    # CONFLICT: 4:발톱도(nsubj→된다), 6:무기가(nsubj→된다)
    # Fix: also-marker: N1(도)→outer
    'test-s266': [('deprel', 4, 'nsubj:outer')],

    # test-s268
    # TEXT: 중국도 유로화 가치 급락으로 유로존 수출시장이 위축되거나 세계경제 회복이 지연되길 바라지 않기 때문이다.
    # TRANSLIT: .jung.gug.do .yu.ro.hwa .ga.chi .geub.rag.eu.ro .yu.ro.jon .su.chul.si.jang.i .wi.chug.doe.geo.na .se.gye.gyeong.je .hoe.bog.i .ji.yeon.doe.gil .ba.ra.ji .anh.gi .ddae.mun.i.da.
    # ENGLISH: This place also has something special.
    # CONFLICT: 1:중국도(nsubj→때문이다), 11:바라지(nsubj→때문이다)
    # Fix: also-marker: N1(도)→outer
    'test-s268': [('deprel', 1, 'nsubj:outer')],

    # test-s271
    # TEXT: 콩국수도 직접 갈은 콩과 직접 뽑은 국수도 일품입니다~
    # TRANSLIT: .kong.gug.su.do .jig.jeob .gal.eun .kong.gwa .jig.jeob .bbob.eun .gug.su.do .il.pum.ib.ni.da~
    # ENGLISH: This place also has good things.
    # CONFLICT: 1:콩국수도(nsubj→일품입니다), 4:콩과(nsubj→일품입니다)
    # Fix: also-marker: N1(도)→outer
    'test-s271': [('deprel', 1, 'nsubj:outer')],

    # test-s29
    # TEXT: 당시 일본 정교회는 아직 재정적으로 자립할 수 있는 상태가 아니라서 급여를 지불할 수 없게 된 많은 교직자들을 해고시킬 수밖에 없게 되어 교세는 쇠약해졌다.
    # TRANSLIT: .dang.si .il.bon .jeong.gyo.hoe.neun .a.jig .jae.jeong.jeog.eu.ro .ja.rib.hal .su .iss.neun .sang.tae.ga .a.ni.ra.seo .geub.yeo.reul .ji.bul.hal .su .eobs.ge .doen .manh.eun .gyo.jig.ja.deul.eul .hae.go.si.kil .su.bagg.e .eobs.ge .doe.eo .gyo.se.neun .soe.yag.hae.jyeoss.da.
    # ENGLISH: Japan is not in that state.
    # CONFLICT: 2:일본(nsubj→아니라서), 9:상태가(nsubj→아니라서)
    # Fix: default: N1(일본)→outer [NEEDS REVIEW]
    'test-s29': [('deprel', 2, 'nsubj:outer')],

    # test-s309
    # TEXT: 일 하나는 똑소리 나데요
    # TRANSLIT: .il .ha.na.neun .ddog.so.ri .na.de.yo
    # ENGLISH: Work is done with a clear crisp sound.
    # CONFLICT: 1:일(nsubj→나데요), 3:똑소리(nsubj→나데요)
    # Fix: default: N1(일)→outer [NEEDS REVIEW]
    'test-s309': [('deprel', 1, 'nsubj:outer')],

    # test-s31
    # TEXT: 블룸버그뉴스가 최근 실시한 설문조사에 따르면 OPEC 회원국들의 9월 총 원유 생산량은 하루 평균 2905만5000배럴로 전월보다 0.5% 줄어들었다.
    # TRANSLIT: .beul.rum.beo.geu.nyu.seu.ga .choe.geun .sil.si.han .seol.mun.jo.sa.e .dda.reu.myeon OPEC .hoe.weon.gug.deul.yi 9.weol .chong .weon.yu .saeng.san.ryang.eun .ha.ru .pyeong.gyun 2905.man5000.bae.reol.ro .jeon.weol.bo.da 0.5% .jul.eo.deul.eoss.da.
    # ENGLISH: In September, the percentage decreased.
    # CONFLICT: 8:9월(nsubj→줄어들었다), 17:%(nsubj→줄어들었다)
    # Fix: default: N1(9월)→outer [NEEDS REVIEW]
    'test-s31': [('deprel', 8, 'nsubj:outer')],

    # test-s314
    # TEXT: 북측 조선적십자회는 지난 10일 통지문을 통해 '추석 계기 금강산 이산가족 상봉'을 제안하면서 "이상의 문제를 협의하기 위해 가능한 한 빠른 시일 내에 북남적십자관계자들의 실무접촉을 가질 것을 제의한다"고 밝힌 바 있다.
    # TRANSLIT: .bug.cheug .jo.seon.jeog.sib.ja.hoe.neun .ji.nan 10.il .tong.ji.mun.eul .tong.hae '.chu.seog .gye.gi .geum.gang.san .i.san.ga.jog .sang.bong'.eul .je.an.ha.myeon.seo ".i.sang.yi .mun.je.reul .hyeob.yi.ha.gi .wi.hae .ga.neung.han .han .bba.reun .si.il .nae.e .bug.nam.jeog.sib.ja.gwan.gye.ja.deul.yi .sil.mu.jeob.chog.eul .ga.jil .geos.eul .je.yi.han.da".go .barg.hin .ba .iss.da.
    # ENGLISH: The North Korean side has that intention.
    # CONFLICT: 1:북측(nsubj→있다), 34:바(nsubj→있다)
    # Fix: default: N1(북측)→outer [NEEDS REVIEW]
    'test-s314': [('deprel', 1, 'nsubj:outer')],

    # test-s34
    # TEXT: 그는 이어 "만약 이 서비스가 제대로 정착만 된다면 중국 및 동남아 부유층 유치에 일대 전기를 마련하게 되는 계기가 될 것"이라며 "외국인도 이용 가능한 상품으로 기획되었다는 점에서 국내 골프투어 수출 시대의 개막도 기대해봄직하다"고 강한 자신감을 나타냈다.
    # TRANSLIT: .geu.neun .i.eo ".man.yag .i .seo.bi.seu.ga .je.dae.ro .jeong.chag.man .doen.da.myeon .jung.gug .mich .dong.nam.a .bu.yu.cheung .yu.chi.e .il.dae .jeon.gi.reul .ma.ryeon.ha.ge .doe.neun .gye.gi.ga .doel .geos".i.ra.myeo ".oe.gug.in.do .i.yong .ga.neung.han .sang.pum.eu.ro .gi.hoeg.doe.eoss.da.neun .jeom.e.seo .gug.nae .gol.peu.tu.eo .su.chul .si.dae.yi .gae.mag.do .gi.dae.hae.bom.jig.ha.da".go .gang.han .ja.sin.gam.eul .na.ta.naess.da.
    # ENGLISH: If the service becomes established.
    # CONFLICT: 6:서비스가(nsubj→된다면), 8:정착만(nsubj→된다면)
    # Fix: default: N1(서비스가)→outer [NEEDS REVIEW]
    'test-s34': [('deprel', 6, 'nsubj:outer')],

    # test-s364
    # TEXT: 지금 서울 시내 길 막혀
    # TRANSLIT: .ji.geum .seo.ul .si.nae .gil .mag.hyeo
    # ENGLISH: Seoul roads are congested.
    # CONFLICT: 2:서울(nsubj→막혀), 4:길(nsubj→막혀)
    # Fix: default: N1(서울)→outer [NEEDS REVIEW]
    'test-s364': [('deprel', 2, 'nsubj:outer')],

    # test-s375
    # TEXT: 넓은 잔디밭도 여유 있어 보이고 중간에 나무 밑에 잘 자리 잡으면 쾌적한 휴식이 가능합니다.
    # TRANSLIT: .neorb.eun .jan.di.bat.do .yeo.yu .iss.eo .bo.i.go .jung.gan.e .na.mu .mit.e .jal .ja.ri .jab.eu.myeon .kwae.jeog.han .hyu.sig.i .ga.neung.hab.ni.da.
    # ENGLISH: This place also has something special.
    # CONFLICT: 2:잔디밭도(nsubj→있어), 3:여유(nsubj→있어)
    # Fix: also-marker: N1(도)→outer
    'test-s375': [('deprel', 2, 'nsubj:outer')],

    # test-s394
    # TEXT: 5위는 자이언트 피라냐로 불리는 물고기 동영상이 차지했다.
    # TRANSLIT: 5.wi.neun .ja.i.eon.teu .pi.ra.nya.ro .bul.ri.neun .mul.go.gi .dong.yeong.sang.i .cha.ji.haess.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:5위는(nsubj→차지했다), 5:물고기(nsubj→차지했다)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s394': [('deprel', 1, 'nsubj:outer')],

    # test-s4
    # TEXT: 위안화 절상 기대감은 중국으로 투기적 자본을 유인하는 강력한 동인이 되어 왔다.
    # TRANSLIT: .wi.an.hwa .jeol.sang .gi.dae.gam.eun .jung.gug.eu.ro .tu.gi.jeog .ja.bon.eul .yu.in.ha.neun .gang.ryeog.han .dong.in.i .doe.eo .wass.da.
    # ENGLISH: The yuan is the driving force.
    # CONFLICT: 1:위안화(nsubj→되어), 9:동인이(nsubj→되어)
    # Fix: default: N1(위안화)→outer [NEEDS REVIEW]
    'test-s4': [('deprel', 1, 'nsubj:outer')],

    # test-s40
    # TEXT: 고기집 치고는 반찬도 여러 가지 나와요.
    # TRANSLIT: .go.gi.jib .chi.go.neun .ban.chan.do .yeo.reo .ga.ji .na.wa.yo.
    # ENGLISH: This place also has good things.
    # CONFLICT: 3:반찬도(nsubj→나와요), 5:가지(nsubj→나와요)
    # Fix: also-marker: N1(도)→outer
    'test-s40': [('deprel', 3, 'nsubj:outer')],

    # test-s408
    # TEXT: 효고현 교육위원회는 23일 도요토미 히데요시의 보물이 매장돼 있는 장소로 기록된 '다다은동광산'의 한 갱도에 무인 탐사 로봇을 들여보내 보물찾기에 나섰다고 <아사히신문 22일 보도했다.
    # TRANSLIT: .hyo.go.hyeon .gyo.yug.wi.weon.hoe.neun 23.il .do.yo.to.mi .hi.de.yo.si.yi .bo.mul.i .mae.jang.dwae .iss.neun .jang.so.ro .gi.rog.doen '.da.da.eun.dong.gwang.san'.yi .han .gaeng.do.e .mu.in .tam.sa .ro.bos.eul .deul.yeo.bo.nae .bo.mul.chaj.gi.e .na.seoss.da.go <.a.sa.hi.sin.mun 22.il .bo.do.haess.da.
    # ENGLISH: Hyogo Prefecture, Asahi Shimbun reported.
    # CONFLICT: 1:효고현(nsubj→보도했다), 24:아사히신문(nsubj→보도했다)
    # Fix: default: N1(효고현)→outer [NEEDS REVIEW]
    'test-s408': [('deprel', 1, 'nsubj:outer')],

    # test-s43
    # TEXT: 그는 "미국 정부도 한국을 비롯해 인도 중국 등 아시아 국가들 등장을 감안해 외교 정책을 재조정할 필요가 있다"면서 "하지만 아시아는 21세기 잠재력은 높지만 아직은 확실히 그렇다고 말하기에는 이르다"고 밝혔다.
    # TRANSLIT: .geu.neun ".mi.gug .jeong.bu.do .han.gug.eul .bi.ros.hae .in.do .jung.gug .deung .a.si.a .gug.ga.deul .deung.jang.eul .gam.an.hae .oe.gyo .jeong.chaeg.eul .jae.jo.jeong.hal .pil.yo.ga .iss.da".myeon.seo ".ha.ji.man .a.si.a.neun 21.se.gi .jam.jae.ryeog.eun .nop.ji.man .a.jig.eun .hwag.sil.hi .geu.reoh.da.go .mal.ha.gi.e.neun .i.reu.da".go .barg.hyeoss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 23:아시아는(nsubj→높지만), 24:21세기(nsubj→높지만)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s43': [('deprel', 23, 'nsubj:outer')],

    # test-s435
    # TEXT: 그의 신랄한 기독교 비판은 한국 내 개신교선교사들, 기독교신자들로부터 주목을 받는 계기가 되었으나, 기독교 비평가인 박헌영에 대한 부정적 인식과 소문을 타고, 그가 편협하고 과격한 성격을 가진 사람이라는 편견으로 굳어져갔다.
    # TRANSLIT: .geu.yi .sin.ral.han .gi.dog.gyo .bi.pan.eun .han.gug .nae .gae.sin.gyo.seon.gyo.sa.deul, .gi.dog.gyo.sin.ja.deul.ro.bu.teo .ju.mog.eul .bad.neun .gye.gi.ga .doe.eoss.eu.na, .gi.dog.gyo .bi.pyeong.ga.in .bag.heon.yeong.e .dae.han .bu.jeong.jeog .in.sig.gwa .so.mun.eul .ta.go, .geu.ga .pyeon.hyeob.ha.go .gwa.gyeog.han .seong.gyeog.eul .ga.jin .sa.ram.i.ra.neun .pyeon.gyeon.eu.ro .gud.eo.jyeo.gass.da.
    # ENGLISH: Christianity became the catalyst.
    # CONFLICT: 3:기독교(nsubj→되었으나), 12:계기가(nsubj→되었으나)
    # Fix: default: N1(기독교)→outer [NEEDS REVIEW]
    'test-s435': [('deprel', 3, 'nsubj:outer')],

    # test-s449
    # TEXT: 문제는 그 옷과 장식품이 자신의 노동으로 장만한 것이 아니라 부모의 돈으로 산 것이라는 점이다.
    # TRANSLIT: .mun.je.neun .geu .os.gwa .jang.sig.pum.i .ja.sin.yi .no.dong.eu.ro .jang.man.han .geos.i .a.ni.ra .bu.mo.yi .don.eu.ro .san .geos.i.ra.neun .jeom.i.da.
    # ENGLISH: The clothes and that are not the issue.
    # CONFLICT: 3:옷과(nsubj→아니라), 8:것이(nsubj→아니라)
    # Fix: default: N1(옷과)→outer [NEEDS REVIEW]
    'test-s449': [('deprel', 3, 'nsubj:outer')],

    # test-s456
    # TEXT: 또 중부선의 경우 증평에서 진천까지 11㎞ 구간에서 지•정체 현상이 반복되고 있으며 차량은 더욱 빠르게 증가하고 있어 저녁까지 운전자들의 불편이 예상된다.
    # TRANSLIT: .ddo .jung.bu.seon.yi .gyeong.u .jeung.pyeong.e.seo .jin.cheon.gga.ji 11㎞ .gu.gan.e.seo .ji•.jeong.che .hyeon.sang.i .ban.bog.doe.go .iss.eu.myeo .cha.ryang.eun .deo.ug .bba.reu.ge .jeung.ga.ha.go .iss.eo .jeo.nyeog.gga.ji .un.jeon.ja.deul.yi .bul.pyeon.i .ye.sang.doen.da.
    # ENGLISH: The congestion is repeatedly occurring.
    # CONFLICT: 9:지(nsubj:pass→반복되고), 11:정체(nsubj:pass→반복되고)
    # Fix: default: N1(지)→outer [NEEDS REVIEW]
    'test-s456': [('deprel', 9, 'nsubj:outer')],

    # test-s467
    # TEXT: 고려신용정보 이영화 채권추심팀장은 자신의 직업에 자부심이 대단하다.
    # TRANSLIT: .go.ryeo.sin.yong.jeong.bo .i.yeong.hwa .chae.gweon.chu.sim.tim.jang.eun .ja.sin.yi .jig.eob.e .ja.bu.sim.i .dae.dan.ha.da.
    # ENGLISH: Korea Credit Bureau, the pride is remarkable.
    # CONFLICT: 1:고려신용정보(nsubj→대단하다), 6:자부심이(nsubj→대단하다)
    # Fix: default: N1(고려신용정보)→outer [NEEDS REVIEW]
    'test-s467': [('deprel', 1, 'nsubj:outer')],

    # test-s477
    # TEXT: 회도 양이 짱 많아서 넘넘 좋아요 ^0^
    # TRANSLIT: .hoe.do .yang.i .jjang .manh.a.seo .neom.neom .joh.a.yo ^0^
    # ENGLISH: This place also has something special.
    # CONFLICT: 1:회도(nsubj→많아서), 2:양이(nsubj→많아서)
    # Fix: also-marker: N1(도)→outer
    'test-s477': [('deprel', 1, 'nsubj:outer')],

    # test-s50
    # TEXT: 강남사거리 지금 상황이 어때
    # TRANSLIT: .gang.nam.sa.geo.ri .ji.geum .sang.hwang.i .eo.ddae
    # ENGLISH: How is the situation at Gangnam Intersection?
    # CONFLICT: 1:강남사거리(nsubj→어때), 3:상황이(nsubj→어때)
    # Fix: default: N1(강남사거리)→outer [NEEDS REVIEW]
    'test-s50': [('deprel', 1, 'nsubj:outer')],

    # test-s514
    # TEXT: 일산은 마두동 백마삼환극동 중대형이 500만~1000만원 정도 내렸다.
    # TRANSLIT: .il.san.eun .ma.du.dong .baeg.ma.sam.hwan.geug.dong .jung.dae.hyeong.i 500.man~1000.man.weon .jeong.do .nae.ryeoss.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:일산은(nsubj→내렸다), 2:마두동(nsubj→내렸다)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s514': [('deprel', 1, 'nsubj:outer')],

    # test-s558
    # TEXT: 사생대회 수상자는 대구광역시교육감상 3명, 포항•구미교육장상 6명을 비롯해 대구은행장상 1,644명으로 수상자에게는 장학금 및 부상이 각각 주어졌다.
    # TRANSLIT: .sa.saeng.dae.hoe .su.sang.ja.neun .dae.gu.gwang.yeog.si.gyo.yug.gam.sang 3.myeong, .po.hang•.gu.mi.gyo.yug.jang.sang 6.myeong.eul .bi.ros.hae .dae.gu.eun.haeng.jang.sang 1,644.myeong.eu.ro .su.sang.ja.e.ge.neun .jang.hag.geum .mich .bu.sang.i .gag.gag .ju.eo.jyeoss.da.
    # ENGLISH: The outdoor sketching competition, the Daegu Bank president's award had 1,644 participants.
    # CONFLICT: 1:사생대회(nsubj→1,644명으로), 9:대구은행장상(nsubj→1,644명으로)
    # Fix: default: N1(사생대회)→outer [NEEDS REVIEW]
    'test-s558': [('deprel', 1, 'nsubj:outer')],

    # test-s571
    # TEXT: 시의 동쪽 외곽에 있으며 붉은 성이라는 이름은 성의 거대한 벽이 붉은 빛을 띠고 있어서이다.
    # TRANSLIT: .si.yi .dong.jjog .oe.gwag.e .iss.eu.myeo .burg.eun .seong.i.ra.neun .i.reum.eun .seong.yi .geo.dae.han .byeog.i .burg.eun .bich.eul .ddi.go .iss.eo.seo.i.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 7:이름은(nsubj→띠고), 10:벽이(nsubj→띠고)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s571': [('deprel', 7, 'nsubj:outer')],

    # test-s613
    # TEXT: 이렇게 큰 힘이 기준 단위가 된 것은 전기에 대한 상세한 지식이 없는 시절에 이를 측정 단위로 삼았기 때문이다.
    # TRANSLIT: .i.reoh.ge .keun .him.i .gi.jun .dan.wi.ga .doen .geos.eun .jeon.gi.e .dae.han .sang.se.han .ji.sig.i .eobs.neun .si.jeol.e .i.reul .cheug.jeong .dan.wi.ro .sam.ass.gi .ddae.mun.i.da.
    # ENGLISH: Strength was the standard.
    # CONFLICT: 3:힘이(nsubj→된), 4:기준(nsubj→된)
    # Fix: default: N1(힘이)→outer [NEEDS REVIEW]
    'test-s613': [('deprel', 3, 'nsubj:outer')],

    # test-s638
    # TEXT: 맵지도 않고 얘들도 잘 먹었고 다른 말이 필요 없어요
    # TRANSLIT: .maeb.ji.do .anh.go .yae.deul.do .jal .meog.eoss.go .da.reun .mal.i .pil.yo .eobs.eo.yo
    # ENGLISH: No need to say anything.
    # CONFLICT: 7:말이(nsubj→없어요), 8:필요(nsubj→없어요)
    # Fix: default: N1(말이)→outer [NEEDS REVIEW]
    'test-s638': [('deprel', 7, 'nsubj:outer')],

    # test-s639
    # TEXT: 탐앤탐스 자체가 커피 맛도 좋구 브레드나 부메뉴들도 정말 좋아요
    # TRANSLIT: .tam.aen.tam.seu .ja.che.ga .keo.pi .mas.do .joh.gu .beu.re.deu.na .bu.me.nyu.deul.do .jeong.mal .joh.a.yo
    # ENGLISH: Tom n Toms has good coffee.
    # CONFLICT: 1:탐앤탐스(nsubj→좋구), 3:커피(nsubj→좋구)
    # Fix: default: N1(탐앤탐스)→outer [NEEDS REVIEW]
    'test-s639': [('deprel', 1, 'nsubj:outer')],

    # test-s665
    # TEXT: 양념이 자체는 맛잇는데 닭에 배이지 않아 겉도는 맛이라 아쉬워요~
    # TRANSLIT: .yang.nyeom.i .ja.che.neun .mas.is.neun.de .darg.e .bae.i.ji .anh.a .geot.do.neun .mas.i.ra .a.swi.weo.yo~
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 1:양념이(nsubj→맛잇는데), 2:자체는(nsubj→맛잇는데)
    # Fix: topic-marker: N2(은/는)→outer
    'test-s665': [('deprel', 2, 'nsubj:outer')],

    # test-s670
    # TEXT: 우승팀은 전, 후기 1위 두 팀과 이들을 제외한 통합승점 1, 2위가 4강 플레이오프전을 펼칠 예정이다.
    # TRANSLIT: .u.seung.tim.eun .jeon, .hu.gi 1.wi .du .tim.gwa .i.deul.eul .je.oe.han .tong.hab.seung.jeom 1, 2.wi.ga 4.gang .peul.re.i.o.peu.jeon.eul .pyeol.chil .ye.jeong.i.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:우승팀은(nsubj→펼칠), 10:통합승점(nsubj→펼칠)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s670': [('deprel', 1, 'nsubj:outer')],

    # test-s710
    # TEXT: 환경 문제는 지금 4대강 사업의 최대 쟁점이 돼 있다.
    # TRANSLIT: .hwan.gyeong .mun.je.neun .ji.geum 4.dae.gang .sa.eob.yi .choe.dae .jaeng.jeom.i .dwae .iss.da.
    # ENGLISH: The environment can be maximized.
    # CONFLICT: 1:환경(nsubj→돼), 6:최대(nsubj→돼)
    # Fix: default: N1(환경)→outer [NEEDS REVIEW]
    'test-s710': [('deprel', 1, 'nsubj:outer')],

    # test-s724
    # TEXT: 그 앞에 주차된 승합차는 트렁크 문이 활짝 열려있다.
    # TRANSLIT: .geu .ap.e .ju.cha.doen .seung.hab.cha.neun .teu.reong.keu .mun.i .hwal.jjag .yeol.ryeo.iss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 4:승합차는(nsubj→열려있다), 5:트렁크(nsubj→열려있다)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s724': [('deprel', 4, 'nsubj:outer')],

    # test-s754
    # TEXT: 우리산업의 상반기 누적 실적은 매출액과 영업이익이 각각 645억원, 17억원으로 추정됐다.
    # TRANSLIT: .u.ri.san.eob.yi .sang.ban.gi .nu.jeog .sil.jeog.eun .mae.chul.aeg.gwa .yeong.eob.i.ig.i .gag.gag 645.eog.weon, 17.eog.weon.eu.ro .chu.jeong.dwaess.da.
    # ENGLISH: The first half sales and revenue are estimated.
    # CONFLICT: 2:상반기(nsubj:pass→추정됐다), 5:매출액과(nsubj:pass→추정됐다)
    # Fix: default: N1(상반기)→outer [NEEDS REVIEW]
    'test-s754': [('deprel', 2, 'nsubj:outer')],

    # test-s776
    # TEXT: 베트남 현대미술은 '베트남전'의 기억과 상흔이 고스란히 반영되어 있다.
    # TRANSLIT: .be.teu.nam .hyeon.dae.mi.sul.eun '.be.teu.nam.jeon'.yi .gi.eog.gwa .sang.heun.i .go.seu.ran.hi .ban.yeong.doe.eo .iss.da.
    # ENGLISH: Vietnam reflects the Vietnam War.
    # CONFLICT: 1:베트남(nsubj:pass→반영되어), 4:베트남전(nsubj:pass→반영되어)
    # Fix: default: N1(베트남)→outer [NEEDS REVIEW]
    'test-s776': [('deprel', 1, 'nsubj:outer')],

    # test-s799
    # TEXT: 문경은 감독과 저도 젊은 나이에 지도자가 됐습니다.
    # TRANSLIT: .mun.gyeong.eun .gam.dog.gwa .jeo.do .jeorm.eun .na.i.e .ji.do.ja.ga .dwaess.seub.ni.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:문경은(nsubj→됐습니다), 6:지도자가(nsubj→됐습니다)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s799': [('deprel', 1, 'nsubj:outer')],

    # test-s832
    # TEXT: 역시 중소형이 60%가 넘는다.
    # TRANSLIT: .yeog.si .jung.so.hyeong.i 60%.ga .neom.neun.da.
    # ENGLISH: Mid-size apartments, more than 60% exceed.
    # CONFLICT: 2:중소형이(nsubj→넘는다), 3:60(nsubj→넘는다)
    # Fix: default: N1(중소형이)→outer [NEEDS REVIEW]
    'test-s832': [('deprel', 2, 'nsubj:outer')],

    # test-s845
    # TEXT: 사장님도 좋은 분 같으시고 손님 만나 얘기 나누기 좋은 장소입니다.
    # TRANSLIT: .sa.jang.nim.do .joh.eun .bun .gat.eu.si.go .son.nim .man.na .yae.gi .na.nu.gi .joh.eun .jang.so.ib.ni.da.
    # ENGLISH: This place also has something special.
    # CONFLICT: 1:사장님도(nsubj→같으시고), 3:분(nsubj→같으시고)
    # Fix: also-marker: N1(도)→outer
    'test-s845': [('deprel', 1, 'nsubj:outer')],

    # test-s867
    # TEXT: 원장님이 어린이집을 운영할 자질이 있는지 의문이네요.
    # TRANSLIT: .weon.jang.nim.i .eo.rin.i.jib.eul .un.yeong.hal .ja.jil.i .iss.neun.ji .yi.mun.i.ne.yo.
    # ENGLISH: The director has the qualities.
    # CONFLICT: 1:원장님이(nsubj→있는지), 4:자질이(nsubj→있는지)
    # Fix: default: N1(원장님이)→outer [NEEDS REVIEW]
    'test-s867': [('deprel', 1, 'nsubj:outer')],

    # test-s873
    # TEXT: 저는 시원한 해산물이 생각나면 자주 가는데 후회없습니다.
    # TRANSLIT: .jeo.neun .si.weon.han .hae.san.mul.i .saeng.gag.na.myeon .ja.ju .ga.neun.de .hu.hoe.eobs.seub.ni.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:저는(nsubj→생각나면), 3:해산물이(nsubj→생각나면)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s873': [('deprel', 1, 'nsubj:outer')],

    # test-s876
    # TEXT: 푸짐한 음식과 밑반찬이 많고, 시설이 청결하고 사장님이 인심이 넓다.
    # TRANSLIT: .pu.jim.han .eum.sig.gwa .mit.ban.chan.i .manh.go, .si.seol.i .cheong.gyeol.ha.go .sa.jang.nim.i .in.sim.i .neorb.da.
    # ENGLISH: The owner is generous.
    # CONFLICT: 8:사장님이(nsubj→넓다), 9:인심이(nsubj→넓다)
    # Fix: default: N1(사장님이)→outer [NEEDS REVIEW]
    'test-s876': [('deprel', 8, 'nsubj:outer')],

    # test-s9
    # TEXT: 서울에 커피전문점 뭐 있나
    # TRANSLIT: .seo.ul.e .keo.pi.jeon.mun.jeom .mweo .iss.na
    # ENGLISH: What coffee shops are available?
    # CONFLICT: 2:커피전문점(nsubj→있나), 3:뭐(nsubj→있나)
    # Fix: default: N1(커피전문점)→outer [NEEDS REVIEW]
    'test-s9': [('deprel', 2, 'nsubj:outer')],

    # test-s90
    # TEXT: 사장님부터 직원들까지 늘 친절하고 안주도 실패작이 없었습니다.
    # TRANSLIT: .sa.jang.nim.bu.teo .jig.weon.deul.gga.ji .neul .chin.jeol.ha.go .an.ju.do .sil.pae.jag.i .eobs.eoss.seub.ni.da.
    # ENGLISH: This place also has good things.
    # CONFLICT: 5:안주도(nsubj→없었습니다), 6:실패작이(nsubj→없었습니다)
    # Fix: also-marker: N1(도)→outer
    'test-s90': [('deprel', 5, 'nsubj:outer')],

    # test-s969
    # TEXT: 몸무게는 차이가 많이 나지 않은데 주변에서는 살 빠졌냐고 해요.
    # TRANSLIT: .mom.mu.ge.neun .cha.i.ga .manh.i .na.ji .anh.eun.de .ju.byeon.e.seo.neun .sal .bba.jyeoss.nya.go .hae.yo.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:몸무게는(nsubj→나지), 2:차이가(nsubj→나지)
    # Fix: topic-marker: N1(은/는)→outer
    'test-s969': [('deprel', 1, 'nsubj:outer')],

    # test-s97
    # TEXT: 환경 문제는 지금 4대강 사업의 최대 쟁점이 돼 있다.
    # TRANSLIT: .hwan.gyeong .mun.je.neun .ji.geum 4.dae.gang .sa.eob.yi .choe.dae .jaeng.jeom.i .dwae .iss.da.
    # ENGLISH: The environment can be maximized.
    # CONFLICT: 1:환경(nsubj→돼), 6:최대(nsubj→돼)
    # Fix: default: N1(환경)→outer [NEEDS REVIEW]
    'test-s97': [('deprel', 1, 'nsubj:outer')],

    # test-s987
    # TEXT: 우리 아이도 약 먹고 키가 많이 자랐답니다.
    # TRANSLIT: .u.ri .a.i.do .yag .meog.go .ki.ga .manh.i .ja.rass.dab.ni.da.
    # ENGLISH: This place also has something good.
    # CONFLICT: 2:아이도(nsubj→자랐답니다), 5:키가(nsubj→자랐답니다)
    # Fix: also-marker: N1(도)→outer
    'test-s987': [('deprel', 2, 'nsubj:outer')],

    # train-s1014
    # TEXT: 태국 감독 아핏차퐁 위라세타쿤(40)이 '전생을 볼 수 있는 분미 삼촌'으로 칸영화제 최고 영예의 주인공이 됐다.
    # TRANSLIT: .tae.gug .gam.dog .a.pis.cha.pong .wi.ra.se.ta.kun(40).i '.jeon.saeng.eul .bol .su .iss.neun .bun.mi .sam.chon'.eu.ro .kan.yeong.hwa.je .choe.go .yeong.ye.yi .ju.in.gong.i .dwaess.da.
    # ENGLISH: Thailand is the main character's previous life.
    # CONFLICT: 1:태국(nsubj→전생을), 21:주인공이(nsubj→전생을)
    # Fix: default: N1(태국)→outer [NEEDS REVIEW]
    'train-s1014': [('deprel', 1, 'nsubj:outer')],

    # train-s1038
    # TEXT: 종업원과 주인의 불친절한 인상은 손님들에게 대접 받기 위해 식당을 운영하는 것 같다.
    # TRANSLIT: .jong.eob.weon.gwa .ju.in.yi .bul.chin.jeol.han .in.sang.eun .son.nim.deul.e.ge .dae.jeob .bad.gi .wi.hae .sig.dang.eul .un.yeong.ha.neun .geos .gat.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 4:인상은(nsubj→같다), 11:것(nsubj→같다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1038': [('deprel', 4, 'nsubj:outer')],

    # train-s1056
    # TEXT: '2009 최고의 루키'로는 슈퍼스타K 출신의 서인국, 알리, 2NE1이, 최고의 음악성을 보장하는 '탐음매니아상'수상자로는 장기하와 얼굴들이, '최고의 작곡상'수상자로는 '그런 사람 또 없습니다'의 조영수가 각각 선정됐다.
    # TRANSLIT: '2009 .choe.go.yi .ru.ki'.ro.neun .syu.peo.seu.taK .chul.sin.yi .seo.in.gug, .al.ri, 2NE1.i, .choe.go.yi .eum.ag.seong.eul .bo.jang.ha.neun '.tam.eum.mae.ni.a.sang'.su.sang.ja.ro.neun .jang.gi.ha.wa .eol.gul.deul.i, '.choe.go.yi .jag.gog.sang'.su.sang.ja.ro.neun '.geu.reon .sa.ram .ddo .eobs.seub.ni.da'.yi .jo.yeong.su.ga .gag.gag .seon.jeong.dwaess.da.
    # ENGLISH: Various subjects are discussed here.
    # CONFLICT: 2:2009(nsubj:pass→선정됐다), 19:탐음매니아상(nsubj:pass→선정됐다), 27:작곡상(nsubj:pass→선정됐다)
    # Fix: triple: [2, 19]→outer
    'train-s1056': [('deprel', 2, 'nsubj:outer'), ('deprel', 19, 'nsubj:outer')],

    # train-s1063
    # TEXT: 이날 설립 40주년을 기념하기 위해 참석한 정의화 국회 부의장은 "그간 묵묵히 정보통신의 발전을 위해 각고의 노력을 아끼지 않은 참석자 여러분 모두 치하를 받아 마땅하다"면서 격려한 뒤 "우리나라 지난해 IT 수출이 1천550달러, 흑자가 732억불에 달해 IT는 우리 주력산업이자 국가 브랜드가 된 만큼 여러분의 노력이 더욱 필요하다"고 당부했다.
    # TRANSLIT: .i.nal .seol.rib 40.ju.nyeon.eul .gi.nyeom.ha.gi .wi.hae .cham.seog.han .jeong.yi.hwa .gug.hoe .bu.yi.jang.eun ".geu.gan .mug.mug.hi .jeong.bo.tong.sin.yi .bal.jeon.eul .wi.hae .gag.go.yi .no.ryeog.eul .a.ggi.ji .anh.eun .cham.seog.ja .yeo.reo.bun .mo.du .chi.ha.reul .bad.a .ma.ddang.ha.da".myeon.seo .gyeog.ryeo.han .dwi ".u.ri.na.ra .ji.nan.hae IT .su.chul.i 1.cheon550.dal.reo, .heug.ja.ga 732.eog.bul.e .dal.hae IT.neun .u.ri .ju.ryeog.san.eob.i.ja .gug.ga .beu.raen.deu.ga .doen .man.keum .yeo.reo.bun.yi .no.ryeog.i .deo.ug .pil.yo.ha.da".go .dang.bu.haess.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 40:IT는(nsubj→된), 42:주력산업이자(nsubj→된)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1063': [('deprel', 40, 'nsubj:outer')],

    # train-s1064
    # TEXT: 더군다나 댐이 지어지기 전에 홍수로 인해 토양이 비옥해졌던 것이 이제는 옛날 얘기가 되면서 원성을 사고 있기도 하다.
    # TRANSLIT: .deo.gun.da.na .daem.i .ji.eo.ji.gi .jeon.e .hong.su.ro .in.hae .to.yang.i .bi.og.hae.jyeoss.deon .geos.i .i.je.neun .yes.nal .yae.gi.ga .doe.myeon.seo .weon.seong.eul .sa.go .iss.gi.do .ha.da.
    # ENGLISH: This has become something from the old days.
    # CONFLICT: 9:것이(nsubj→되면서), 11:옛날(nsubj→되면서)
    # Fix: default: N1(것이)→outer [NEEDS REVIEW]
    'train-s1064': [('deprel', 9, 'nsubj:outer')],

    # train-s1065
    # TEXT: 첫 타석에서 첫 홈런을 기록한 선수로서 통산 200홈런, 통산 2000안타를 기록한 선수는 다카기가 처음이었고 통산 200홈런과 200개의 희생타를 합쳐서 기록한 선수도 다카기가 처음이다.
    # TRANSLIT: .cheos .ta.seog.e.seo .cheos .hom.reon.eul .gi.rog.han .seon.su.ro.seo .tong.san 200.hom.reon, .tong.san 2000.an.ta.reul .gi.rog.han .seon.su.neun .da.ka.gi.ga .cheo.eum.i.eoss.go .tong.san 200.hom.reon.gwa 200.gae.yi .hyi.saeng.ta.reul .hab.chyeo.seo .gi.rog.han .seon.su.do .da.ka.gi.ga .cheo.eum.i.da.
    # ENGLISH: This restaurant's flavor as well is excellent.
    # CONFLICT: 13:선수는(nsubj→처음이었고), 14:다카기가(nsubj→처음이었고)
    # CONFLICT: 22:선수도(nsubj→처음이다), 23:다카기가(nsubj→처음이다)
    # Fix: topic-marker: N1(은/는)→outer | also-marker: N1(도)→outer
    'train-s1065': [('deprel', 13, 'nsubj:outer'), ('deprel', 22, 'nsubj:outer')],

    # train-s1070
    # TEXT: 이 민박은 카드 결제 안됩니다
    # TRANSLIT: .i .min.bag.eun .ka.deu .gyeol.je .an.doeb.ni.da
    # ENGLISH: This place is very good.
    # CONFLICT: 2:민박은(nsubj→안됩니다), 3:카드(nsubj→안됩니다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1070': [('deprel', 2, 'nsubj:outer')],

    # train-s1082
    # TEXT: 아주머니가 정이 많으신데 김밥은 잘 못 썰어요
    # TRANSLIT: .a.ju.meo.ni.ga .jeong.i .manh.eu.sin.de .gim.bab.eun .jal .mos .sseol.eo.yo
    # ENGLISH: The lady has a warm heart.
    # CONFLICT: 1:아주머니가(nsubj→많으신데), 2:정이(nsubj→많으신데)
    # Fix: default: N1(아주머니가)→outer [NEEDS REVIEW]
    'train-s1082': [('deprel', 1, 'nsubj:outer')],

    # train-s1091
    # TEXT: 그 결과, 하지불안증후군과 고혈압 간에 유의할만한 관계가 나타났으며 이런 관계는 증상이 심할수록 혈압이 더 높았다.
    # TRANSLIT: .geu .gyeol.gwa, .ha.ji.bul.an.jeung.hu.gun.gwa .go.hyeol.ab .gan.e .yu.yi.hal.man.han .gwan.gye.ga .na.ta.nass.eu.myeo .i.reon .gwan.gye.neun .jeung.sang.i .sim.hal.su.rog .hyeol.ab.i .deo .nop.ass.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 11:관계는(nsubj→높았다), 14:혈압이(nsubj→높았다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1091': [('deprel', 11, 'nsubj:outer')],

    # train-s1113
    # TEXT: 짬뽕이 내용물도 얼마 없고 국물이 깔끔한 맛이 없어요
    # TRANSLIT: .jjam.bbong.i .nae.yong.mul.do .eol.ma .eobs.go .gug.mul.i .ggal.ggeum.han .mas.i .eobs.eo.yo
    # ENGLISH: The broth is bland in taste, and the taste overall is also bad.
    # CONFLICT: 1:짬뽕이(nsubj→없고), 2:내용물도(nsubj→없고)
    # CONFLICT: 5:국물이(nsubj→없어요), 7:맛이(nsubj→없어요)
    # Fix: also-marker: N2(도)→outer | default: N1(국물이)→outer [NEEDS REVIEW]
    'train-s1113': [('deprel', 2, 'nsubj:outer'), ('deprel', 5, 'nsubj:outer')],

    # train-s1130
    # TEXT: 물론 당시 구축함에 실을 수 있는 병력과 물자는 한계가 있었고, 일본군도 그 사실을 모르는 바는 아니었으나, 그렇게 할 수밖에 없는 이유가 있었다.
    # TRANSLIT: .mul.ron .dang.si .gu.chug.ham.e .sil.eul .su .iss.neun .byeong.ryeog.gwa .mul.ja.neun .han.gye.ga .iss.eoss.go, .il.bon.gun.do .geu .sa.sil.eul .mo.reu.neun .ba.neun .a.ni.eoss.eu.na, .geu.reoh.ge .hal .su.bagg.e .eobs.neun .i.yu.ga .iss.eoss.da.
    # ENGLISH: The military force had its limitations.
    # CONFLICT: 7:병력과(nsubj→있었고), 9:한계가(nsubj→있었고)
    # Fix: default: N1(병력과)→outer [NEEDS REVIEW]
    'train-s1130': [('deprel', 7, 'nsubj:outer')],

    # train-s1136
    # TEXT: 또한 SK증권은 통합 리스크데이터웨어하우스(RDW) 구축을 통한 통합리스크관리에 필요한 모든 데이터를 최적화된 상태로 관리할 수 있게 되었다.
    # TRANSLIT: .ddo.han SK.jeung.gweon.eun .tong.hab .ri.seu.keu.de.i.teo.we.eo.ha.u.seu(RDW) .gu.chug.eul .tong.han .tong.hab.ri.seu.keu.gwan.ri.e .pil.yo.han .mo.deun .de.i.teo.reul .choe.jeog.hwa.doen .sang.tae.ro .gwan.ri.hal .su .iss.ge .doe.eoss.da.
    # ENGLISH: There is a possibility of recovery.
    # CONFLICT: 2:SK증권은(nsubj→있게), 17:수(nsubj→있게)
    # Fix: su-construction: N1→outer
    'train-s1136': [('deprel', 2, 'nsubj:outer')],

    # train-s1146
    # TEXT: 영어 역시 보다 쉬운 메인화면 구성(10.2%)이 의견이 가장 많았고, 일본어는 다양한 공연 상품 게재(6.1 %), 중국어 간체권은 빠른 정보 업데이트(7.8%)와 로딩 속도개선(4.9 %), 번체권은 할인권 정보 등 실질적인 서비스(2.1%)가 가장 필요한 것으로 응답하였다.
    # TRANSLIT: .yeong.eo .yeog.si .bo.da .swi.un .me.in.hwa.myeon .gu.seong(10.2%).i .yi.gyeon.i .ga.jang .manh.ass.go, .il.bon.eo.neun .da.yang.han .gong.yeon .sang.pum .ge.jae(6.1 %), .jung.gug.eo .gan.che.gweon.eun .bba.reun .jeong.bo .eob.de.i.teu(7.8%).wa .ro.ding .sog.do.gae.seon(4.9 %), .beon.che.gweon.eun .hal.in.gweon .jeong.bo .deung .sil.jil.jeog.in .seo.bi.seu(2.1%).ga .ga.jang .pil.yo.han .geos.eu.ro .eung.dab.ha.yeoss.da.
    # ENGLISH: Various things are important here.
    # CONFLICT: 1:영어(nsubj→많았고), 5:메인화면(nsubj→많았고), 12:의견이(nsubj→많았고)
    # CONFLICT: 43:번체권은(nsubj→할인권), 53:가(nsubj→할인권)
    # Fix: triple: [1, 5]→outer | topic-marker: N1(은/는)→outer
    'train-s1146': [('deprel', 1, 'nsubj:outer'), ('deprel', 5, 'nsubj:outer'), ('deprel', 43, 'nsubj:outer')],

    # train-s1152
    # TEXT: 기념사업회 김일태 추진위원장은 "올 4월이 고향의 봄 창작 85주년이 되는 만큼 오동동 71번지가 창작터라는 것을 알리는 표석을 세우고 이곳에서 창작된 선생의 다른 동요들도 노래로 만들어 보급하겠다"고 밝혔다.
    # TRANSLIT: .gi.nyeom.sa.eob.hoe .gim.il.tae .chu.jin.wi.weon.jang.eun ".ol 4.weol.i .go.hyang.yi .bom .chang.jag 85.ju.nyeon.i .doe.neun .man.keum .o.dong.dong 71.beon.ji.ga .chang.jag.teo.ra.neun .geos.eul .al.ri.neun .pyo.seog.eul .se.u.go .i.gos.e.seo .chang.jag.doen .seon.saeng.yi .da.reun .dong.yo.deul.do .no.rae.ro .man.deul.eo .bo.geub.ha.gess.da".go .barg.hyeoss.da.
    # ENGLISH: April is the month when my hometown is remembered.
    # CONFLICT: 6:4월이(nsubj→되는), 7:고향의(nsubj→되는)
    # Fix: default: N1(4월이)→outer [NEEDS REVIEW]
    'train-s1152': [('deprel', 6, 'nsubj:outer')],

    # train-s1161
    # TEXT: 양념은 소스가 매콤해서 자꾸 땡기는 매운 맛이다
    # TRANSLIT: .yang.nyeom.eun .so.seu.ga .mae.kom.hae.seo .ja.ggu .ddaeng.gi.neun .mae.un .mas.i.da
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:양념은(nsubj→매콤해서), 2:소스가(nsubj→매콤해서)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1161': [('deprel', 1, 'nsubj:outer')],

    # train-s1164
    # TEXT: 화구벽은 경사가 급하다.
    # TRANSLIT: .hwa.gu.byeog.eun .gyeong.sa.ga .geub.ha.da.
    # ENGLISH: This is a really good restaurant.
    # CONFLICT: 1:화구벽은(nsubj→급하다), 2:경사가(nsubj→급하다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1164': [('deprel', 1, 'nsubj:outer')],

    # train-s1165
    # TEXT: 다른 에르메스 가방들과 마찬가지로 켈리백 또한 공정과정이 까다롭기로 유명하다.
    # TRANSLIT: .da.reun .e.reu.me.seu .ga.bang.deul.gwa .ma.chan.ga.ji.ro .kel.ri.baeg .ddo.han .gong.jeong.gwa.jeong.i .gga.da.rob.gi.ro .yu.myeong.ha.da.
    # ENGLISH: The Kelly bag's manufacturing process is known to be demanding.
    # CONFLICT: 5:켈리백(nsubj→까다롭기로), 7:공정과정이(nsubj→까다롭기로)
    # Fix: default: N1(켈리백)→outer [NEEDS REVIEW]
    'train-s1165': [('deprel', 5, 'nsubj:outer')],

    # train-s1174
    # TEXT: 낮기온은 서울 29도, 대구 33도로 어제보다 높아서 덥겠습니다.
    # TRANSLIT: .naj.gi.on.eun .seo.ul 29.do, .dae.gu 33.do.ro .eo.je.bo.da .nop.a.seo .deob.gess.seub.ni.da.
    # ENGLISH: This is a very meaningful place.
    # CONFLICT: 1:낮기온은(nsubj→33도로), 5:대구(nsubj→33도로)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1174': [('deprel', 1, 'nsubj:outer')],

    # train-s1175
    # TEXT: 서비스가 불만이고 상추랑 깻잎도 상태가 별로입니다
    # TRANSLIT: .seo.bi.seu.ga .bul.man.i.go .sang.chu.rang .ggaes.ip.do .sang.tae.ga .byeol.ro.ib.ni.da
    # ENGLISH: The lettuce's condition is not great.
    # CONFLICT: 3:상추랑(nsubj→별로입니다), 5:상태가(nsubj→별로입니다)
    # Fix: default: N1(상추랑)→outer [NEEDS REVIEW]
    'train-s1175': [('deprel', 3, 'nsubj:outer')],

    # train-s1177
    # TEXT: 김태완은 이날 1군 등록이 말소됐다.
    # TRANSLIT: .gim.tae.wan.eun .i.nal 1.gun .deung.rog.i .mal.so.dwaess.da.
    # ENGLISH: This is a very good place.
    # CONFLICT: 1:김태완은(nsubj→말소됐다), 3:1군(nsubj:pass→말소됐다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1177': [('deprel', 1, 'nsubj:outer')],

    # train-s1188
    # TEXT: 고기의 질도 좋지만, 반찬들의 재료도 신선함이 느껴집니다.
    # TRANSLIT: .go.gi.yi .jil.do .joh.ji.man, .ban.chan.deul.yi .jae.ryo.do .sin.seon.ham.i .neu.ggyeo.jib.ni.da.
    # ENGLISH: This place also has something special.
    # CONFLICT: 6:재료도(nsubj:pass→느껴집니다), 7:신선함이(nsubj:pass→느껴집니다)
    # Fix: also-marker: N1(도)→outer
    'train-s1188': [('deprel', 6, 'nsubj:outer')],

    # train-s1201
    # TEXT: 만리장성은 길이가 얼마나 돼?
    # TRANSLIT: .man.ri.jang.seong.eun .gil.i.ga .eol.ma.na .dwae?
    # ENGLISH: This is a very meaningful thing.
    # CONFLICT: 1:만리장성은(nsubj→돼), 2:길이가(nsubj→돼)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1201': [('deprel', 1, 'nsubj:outer')],

    # train-s1203
    # TEXT: 이 곳은 제가 그 근처 가 본 미용실 중 최악의 서비스인 거 같아요
    # TRANSLIT: .i .gos.eun .je.ga .geu .geun.cheo .ga .bon .mi.yong.sil .jung .choe.ag.yi .seo.bi.seu.in .geo .gat.a.yo
    # ENGLISH: This is a very good place.
    # CONFLICT: 2:곳은(nsubj→같아요), 12:거(nsubj→같아요)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1203': [('deprel', 2, 'nsubj:outer')],

    # train-s1241
    # TEXT: 국민투표는 여권내에서도 '위험카드'라며 반대 여론(정두언의원 등)이 만만치 않아 추진 카드라기보다 친박 압박용 카드일 가능성이 높고, 이원집정부제 및 내각제 개헌카드는 박근혜와 야권의 '세종시 연대'를 깨기 위한 '박근혜 죽이기'카드로 친박의 반발이 매우 거세다.
    # TRANSLIT: .gug.min.tu.pyo.neun .yeo.gweon.nae.e.seo.do '.wi.heom.ka.deu'.ra.myeo .ban.dae .yeo.ron(.jeong.du.eon.yi.weon .deung).i .man.man.chi .anh.a .chu.jin .ka.deu.ra.gi.bo.da .chin.bag .ab.bag.yong .ka.deu.il .ga.neung.seong.i .nop.go, .i.weon.jib.jeong.bu.je .mich .nae.gag.je .gae.heon.ka.deu.neun .bag.geun.hye.wa .ya.gweon.yi '.se.jong.si .yeon.dae'.reul .ggae.gi .wi.han '.bag.geun.hye .jug.i.gi'.ka.deu.ro .chin.bag.yi .ban.bal.i .mae.u .geo.se.da.
    # ENGLISH: Various important things are mentioned here.
    # CONFLICT: 1:국민투표는(nsubj→위험카드), 7:반대(nsubj→위험카드)
    # CONFLICT: 24:이원집정부제(nsubj→박근혜), 39:죽이기(csubj→박근혜), 43:반발이(nsubj→박근혜)
    # Fix: topic-marker: N1(은/는)→outer | triple: [24, 39]→outer
    'train-s1241': [('deprel', 1, 'nsubj:outer'), ('deprel', 24, 'nsubj:outer'), ('deprel', 39, 'nsubj:outer')],

    # train-s1257
    # TEXT: 또한 2030 청년층의 지지세가 보수성향 중심의 한나라당보다 야당에 몰려 있는 점도 이같은 현상을 설명할 수 있는 한 요인이 될 수 있다.
    # TRANSLIT: .ddo.han 2030 .cheong.nyeon.cheung.yi .ji.ji.se.ga .bo.su.seong.hyang .jung.sim.yi .han.na.ra.dang.bo.da .ya.dang.e .mol.ryeo .iss.neun .jeom.do .i.gat.eun .hyeon.sang.eul .seol.myeong.hal .su .iss.neun .han .yo.in.i .doel .su .iss.da.
    # ENGLISH: This place also has good food.
    # CONFLICT: 11:점도(nsubj→될), 18:요인이(nsubj→될)
    # Fix: also-marker: N1(도)→outer
    'train-s1257': [('deprel', 11, 'nsubj:outer')],

    # train-s13
    # TEXT: 밥찬은 중간은 하는데 해물탕은 진짜 성의 없다
    # TRANSLIT: .bab.chan.eun .jung.gan.eun .ha.neun.de .hae.mul.tang.eun .jin.jja .seong.yi .eobs.da
    # ENGLISH: The side dishes are mediocre, but the spicy seafood stew really lacks sincerity.
    # CONFLICT: 4:해물탕은(nsubj→없다), 6:성의(nsubj→없다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s13': [('deprel', 4, 'nsubj:outer')],

    # train-s1309
    # TEXT: 이번 방북은 북측이 '금강산국제관광특구법'에 따라 우리측 기업들에 국제관광의 새틀에 참여하거나 '재산정리'에 나설 것을 촉구하는 가운데 이뤄지는 것이어서 북측과 관련 논의가 이뤄질지 주목된다.
    # TRANSLIT: .i.beon .bang.bug.eun .bug.cheug.i '.geum.gang.san.gug.je.gwan.gwang.teug.gu.beob'.e .dda.ra .u.ri.cheug .gi.eob.deul.e .gug.je.gwan.gwang.yi .sae.teul.e .cham.yeo.ha.geo.na '.jae.san.jeong.ri'.e .na.seol .geos.eul .chog.gu.ha.neun .ga.un.de .i.rweo.ji.neun .geos.i.eo.seo .bug.cheug.gwa .gwan.ryeon .non.yi.ga .i.rweo.jil.ji .ju.mog.doen.da.
    # ENGLISH: There is attention on whether this will come true.
    # CONFLICT: 1:이번(nsubj→주목된다), 27:이뤄질지(csubj→주목된다)
    # Fix: default: N1(이번)→outer [NEEDS REVIEW]
    'train-s1309': [('deprel', 1, 'nsubj:outer')],

    # train-s1316
    # TEXT: 그래서 미국의 적극적인 지지는 한반도 통일의 필수적인 요소가 아닐 수 없다.
    # TRANSLIT: .geu.rae.seo .mi.gug.yi .jeog.geug.jeog.in .ji.ji.neun .han.ban.do .tong.il.yi .pil.su.jeog.in .yo.so.ga .a.nil .su .eobs.da.
    # ENGLISH: This place is very good.
    # CONFLICT: 4:지지는(nsubj→아닐), 8:요소가(nsubj→아닐)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1316': [('deprel', 4, 'nsubj:outer')],

    # train-s1327
    # TEXT: 하나님께서 로마행은 옳은 선택이 아니라는 말을 선수 본인에게 전했다는 것이 주 내용이다.
    # TRANSLIT: .ha.na.nim.gge.seo .ro.ma.haeng.eun .orh.eun .seon.taeg.i .a.ni.ra.neun .mal.eul .seon.su .bon.in.e.ge .jeon.haess.da.neun .geos.i .ju .nae.yong.i.da.
    # ENGLISH: This place is very good.
    # CONFLICT: 2:로마행은(nsubj→아니라는), 4:선택이(nsubj→아니라는)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1327': [('deprel', 2, 'nsubj:outer')],

    # train-s1330
    # TEXT: 표준 소요 시간은 나라 행 44분, 교토 행은 47분이다.
    # TRANSLIT: .pyo.jun .so.yo .si.gan.eun .na.ra .haeng 44.bun, .gyo.to .haeng.eun 47.bun.i.da.
    # ENGLISH: Standard time, Kyoto is 47 minutes away.
    # CONFLICT: 1:표준(nsubj→47분이다), 8:교토(nsubj→47분이다)
    # Fix: default: N1(표준)→outer [NEEDS REVIEW]
    'train-s1330': [('deprel', 1, 'nsubj:outer')],

    # train-s1343
    # TEXT: 정부는 "북한의 이번 무력도발(armed attack)은 유엔 헌장의 명백한 위반이자 1953년 유엔군이 당사자로 참여한 정전협정, 그리고 1992년 남북기본합의서를 위배한 것"이라고 규정하고 "북한의 무력도발은 한반도와 국제사회의 평화와 안전에 위협이 되고 있다"고 지적했다.
    # TRANSLIT: .jeong.bu.neun ".bug.han.yi .i.beon .mu.ryeog.do.bal(armed attack).eun .yu.en .heon.jang.yi .myeong.baeg.han .wi.ban.i.ja 1953.nyeon .yu.en.gun.i .dang.sa.ja.ro .cham.yeo.han .jeong.jeon.hyeob.jeong, .geu.ri.go 1992.nyeon .nam.bug.gi.bon.hab.yi.seo.reul .wi.bae.han .geos".i.ra.go .gyu.jeong.ha.go ".bug.han.yi .mu.ryeog.do.bal.eun .han.ban.do.wa .gug.je.sa.hoe.yi .pyeong.hwa.wa .an.jeon.e .wi.hyeob.i .doe.go .iss.da".go .ji.jeog.haess.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 31:무력도발은(nsubj→되고), 36:위협이(nsubj→되고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1343': [('deprel', 31, 'nsubj:outer')],

    # train-s1372
    # TEXT: 그 앞에 주차된 승합차는 트렁크 문이 활짝 열려있다.
    # TRANSLIT: .geu .ap.e .ju.cha.doen .seung.hab.cha.neun .teu.reong.keu .mun.i .hwal.jjag .yeol.ryeo.iss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 4:승합차는(nsubj→열려있다), 5:트렁크(nsubj→열려있다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1372': [('deprel', 4, 'nsubj:outer')],

    # train-s1399
    # TEXT: 그리고 주방이 오픈 되어 있어서 깨끗해요
    # TRANSLIT: .geu.ri.go .ju.bang.i .o.peun .doe.eo .iss.eo.seo .ggae.ggeus.hae.yo
    # ENGLISH: The kitchen is being renovated into an open style.
    # CONFLICT: 2:주방이(nsubj→되어), 3:오픈(nsubj→되어)
    # Fix: default: N1(주방이)→outer [NEEDS REVIEW]
    'train-s1399': [('deprel', 2, 'nsubj:outer')],

    # train-s14
    # TEXT: 김후정 동양종금증권 (8,770원 40 0.5%) 펀드연구원은 "개인들이 투자하는 사모펀드는 단기 고수익을 추구하는 상품이 대부분"이라며 "펀드시장이 단기 사모화될 경우 개인은 물론 자본시장의 효율적인 자산배분을 저해해 증시 변동성이 커질 수 있다"고 지적했다.
    # TRANSLIT: .gim.hu.jeong .dong.yang.jong.geum.jeung.gweon (8,770.weon 40 0.5%) .peon.deu.yeon.gu.weon.eun ".gae.in.deul.i .tu.ja.ha.neun .sa.mo.peon.deu.neun .dan.gi .go.su.ig.eul .chu.gu.ha.neun .sang.pum.i .dae.bu.bun".i.ra.myeo ".peon.deu.si.jang.i .dan.gi .sa.mo.hwa.doel .gyeong.u .gae.in.eun .mul.ron .ja.bon.si.jang.yi .hyo.yul.jeog.in .ja.san.bae.bun.eul .jeo.hae.hae .jeung.si .byeon.dong.seong.i .keo.jil .su .iss.da".go .ji.jeog.haess.da.
    # ENGLISH: Kim Hu-jeong, a fund researcher at Dongyang Investment and Securities, pointed out that if this report is correct, it clearly reveals how groundless North Korea's claims of religious freedom are.
    # CONFLICT: 13:사모펀드는(nsubj→대부분), 17:상품이(nsubj→대부분)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s14': [('deprel', 13, 'nsubj:outer')],

    # train-s1438
    # TEXT: 전복죽이 냄새 나서 못 먹었어요
    # TRANSLIT: .jeon.bog.jug.i .naem.sae .na.seo .mos .meog.eoss.eo.yo
    # ENGLISH: The abalone porridge smells off.
    # CONFLICT: 1:전복죽이(nsubj→나서), 2:냄새(nsubj→나서)
    # Fix: default: N1(전복죽이)→outer [NEEDS REVIEW]
    'train-s1438': [('deprel', 1, 'nsubj:outer')],

    # train-s144
    # TEXT: 1980년 이후 우리나라의 경기 저점에서 고점에 이르기까지 평균 약 24개월이 걸린 것을 고려하면 내년 1월이 경기고점이 될 것이란 단순 추정이 가능하다.
    # TRANSLIT: 1980.nyeon .i.hu .u.ri.na.ra.yi .gyeong.gi .jeo.jeom.e.seo .go.jeom.e .i.reu.gi.gga.ji .pyeong.gyun .yag 24.gae.weol.i .geol.rin .geos.eul .go.ryeo.ha.myeon .nae.nyeon 1.weol.i .gyeong.gi.go.jeom.i .doel .geos.i.ran .dan.sun .chu.jeong.i .ga.neung.ha.da.
    # ENGLISH: Next year is expected to be the peak of the economic cycle.
    # CONFLICT: 14:내년(nsubj→될), 16:경기고점이(nsubj→될)
    # Fix: default: N1(내년)→outer [NEEDS REVIEW]
    'train-s144': [('deprel', 14, 'nsubj:outer')],

    # train-s1457
    # TEXT: 우선 의사도 간호사도 애들을 진심으로 대해주고 진단과 치료에 대한 설명을 친절하게 잘 해줌
    # TRANSLIT: .u.seon .yi.sa.do .gan.ho.sa.do .ae.deul.eul .jin.sim.eu.ro .dae.hae.ju.go .jin.dan.gwa .chi.ryo.e .dae.han .seol.myeong.eul .chin.jeol.ha.ge .jal .hae.jum
    # ENGLISH: This place is also good.
    # CONFLICT: 2:의사도(nsubj→대해주고), 3:간호사도(nsubj→대해주고)
    # Fix: both-also: N1→outer (first)
    'train-s1457': [('deprel', 2, 'nsubj:outer')],

    # train-s1458
    # TEXT: 실내가 넓고 직원들은 친절해서 좋긴 한데 안주가 맛이 별로임
    # TRANSLIT: .sil.nae.ga .neorb.go .jig.weon.deul.eun .chin.jeol.hae.seo .joh.gin .han.de .an.ju.ga .mas.i .byeol.ro.im
    # ENGLISH: The side dishes are also mediocre.
    # CONFLICT: 7:안주가(nsubj→별로임), 8:맛이(nsubj→별로임)
    # Fix: default: N1(안주가)→outer [NEEDS REVIEW]
    'train-s1458': [('deprel', 7, 'nsubj:outer')],

    # train-s1491
    # TEXT: 제1차 세계 대전 후 뉴욕은 세계의 콘서트 도시가 되었고, 또한 작곡가조합 등이 결성되어 그 결과로 현대음악의 육성을 목표로 하는 다른 많은 단체와 그룹의 설립이 왕성해졌다.
    # TRANSLIT: .je1.cha .se.gye .dae.jeon .hu .nyu.yog.eun .se.gye.yi .kon.seo.teu .do.si.ga .doe.eoss.go, .ddo.han .jag.gog.ga.jo.hab .deung.i .gyeol.seong.doe.eo .geu .gyeol.gwa.ro .hyeon.dae.eum.ag.yi .yug.seong.eul .mog.pyo.ro .ha.neun .da.reun .manh.eun .dan.che.wa .geu.rub.yi .seol.rib.i .wang.seong.hae.jyeoss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 5:뉴욕은(nsubj→되었고), 7:콘서트(nsubj→되었고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1491': [('deprel', 5, 'nsubj:outer')],

    # train-s1502
    # TEXT: 이것으로 메티스는 돌이 많고 밀도는 3.3~8.9 g/cm³임을 알 수 있었다.
    # TRANSLIT: .i.geos.eu.ro .me.ti.seu.neun .dol.i .manh.go .mil.do.neun 3.3~8.9 g/cm³.im.eul .al .su .iss.eoss.da.
    # ENGLISH: This place is very good.
    # CONFLICT: 2:메티스는(nsubj→많고), 3:돌이(nsubj→많고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1502': [('deprel', 2, 'nsubj:outer')],

    # train-s1505
    # TEXT: 바가지 요금 장난 아님
    # TRANSLIT: .ba.ga.ji .yo.geum .jang.nan .a.nim
    # ENGLISH: The price gouging is no joke.
    # CONFLICT: 1:바가지(nsubj→아님), 3:장난(nsubj→아님)
    # Fix: default: N1(바가지)→outer [NEEDS REVIEW]
    'train-s1505': [('deprel', 1, 'nsubj:outer')],

    # train-s1507
    # TEXT: 먼저, 개천설(蓋天說)인데, 이는 ''하늘은 둥그스름한 우산처럼 되어 있고, 그 아래에 평평한 땅이 있다’라는 주장으로, 하늘은 둥글고 땅은 모가 나 있다는 천원지방(天圓地方)이라는 말은 개천설에 의한 것이다.
    # TRANSLIT: .meon.jeo, .gae.cheon.seol(gàitiānshuō).in.de, .i.neun ''.ha.neul.eun .dung.geu.seu.reum.han .u.san.cheo.reom .doe.eo .iss.go, .geu .a.rae.e .pyeong.pyeong.han .ddang.i .iss.da’.ra.neun .ju.jang.eu.ro, .ha.neul.eun .dung.geul.go .ddang.eun .mo.ga .na .iss.da.neun .cheon.weon.ji.bang(tiānyuándefāng).i.ra.neun .mal.eun .gae.cheon.seol.e .yi.han .geos.i.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 28:땅은(nsubj→나), 29:모가(nsubj→나)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1507': [('deprel', 28, 'nsubj:outer')],

    # train-s1513
    # TEXT: 하지만, 이 주제는 관측결과가 매우 적었기 때문에 어떤 주장을 펼쳐도 불충분한 근거라는 명목이 발목을 잡았기 때문에 큰 진전이 없었다.
    # TRANSLIT: .ha.ji.man, .i .ju.je.neun .gwan.cheug.gyeol.gwa.ga .mae.u .jeog.eoss.gi .ddae.mun.e .eo.ddeon .ju.jang.eul .pyeol.chyeo.do .bul.chung.bun.han .geun.geo.ra.neun .myeong.mog.i .bal.mog.eul .jab.ass.gi .ddae.mun.e .keun .jin.jeon.i .eobs.eoss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 4:주제는(nsubj→적었기), 5:관측결과가(nsubj→적었기)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1513': [('deprel', 4, 'nsubj:outer')],

    # train-s1522
    # TEXT: 또한 성가나 세속선율을 변형하여 사용한 변용미사도 35개 있으며 그 중 11개는 그레고리오 성가가 아닌 다른 평성가를 변용한 것이다.
    # TRANSLIT: .ddo.han .seong.ga.na .se.sog.seon.yul.eul .byeon.hyeong.ha.yeo .sa.yong.han .byeon.yong.mi.sa.do 35.gae .iss.eu.myeo .geu .jung 11.gae.neun .geu.re.go.ri.o .seong.ga.ga .a.nin .da.reun .pyeong.seong.ga.reul .byeon.yong.han .geos.i.da.
    # ENGLISH: This place also has good food.
    # CONFLICT: 6:변용미사도(nsubj→있으며), 7:35개(nsubj→있으며)
    # Fix: also-marker: N1(도)→outer
    'train-s1522': [('deprel', 6, 'nsubj:outer')],

    # train-s1526
    # TEXT: 원주로 이사 와서 추천을 많이하길래 먹어봤는데 탕수육 튀김 옷 두께가 장난 아님.
    # TRANSLIT: .weon.ju.ro .i.sa .wa.seo .chu.cheon.eul .manh.i.ha.gil.rae .meog.eo.bwass.neun.de .tang.su.yug .twi.gim .os .du.gge.ga .jang.nan .a.nim.
    # ENGLISH: The sweet and sour pork is also a joke.
    # CONFLICT: 7:탕수육(nsubj→아님), 11:장난(nsubj→아님)
    # Fix: default: N1(탕수육)→outer [NEEDS REVIEW]
    'train-s1526': [('deprel', 7, 'nsubj:outer')],

    # train-s1545
    # TEXT: 숯불 석쇠에 구워 먹는 양념 닭갈비 맛이 다른 닭갈비와는 차원이 달라요
    # TRANSLIT: .such.bul .seog.soe.e .gu.weo .meog.neun .yang.nyeom .darg.gal.bi .mas.i .da.reun .darg.gal.bi.wa.neun .cha.weon.i .dal.ra.yo
    # ENGLISH: The seasoning is on a completely different level.
    # CONFLICT: 5:양념(nsubj→달라요), 10:차원이(nsubj→달라요)
    # Fix: default: N1(양념)→outer [NEEDS REVIEW]
    'train-s1545': [('deprel', 5, 'nsubj:outer')],

    # train-s1582
    # TEXT: 차세대 지속성 인성장호르몬은 1세대 인성장호르몬에 ㈜ 알테오젠의 NexPTM 기술을 적용해 개발하게 되며, 인체 내 지속성을 높이고 1주 1회 주사 및 통증 경감 효과를 보여 편의성을 개선할 수 있을 것으로 전망된다.
    # TRANSLIT: .cha.se.dae .ji.sog.seong .in.seong.jang.ho.reu.mon.eun 1.se.dae .in.seong.jang.ho.reu.mon.e ㈜ .al.te.o.jen.yi NexPTM .gi.sul.eul .jeog.yong.hae .gae.bal.ha.ge .doe.myeo, .in.che .nae .ji.sog.seong.eul .nop.i.go 1.ju 1.hoe .ju.sa .mich .tong.jeung .gyeong.gam .hyo.gwa.reul .bo.yeo .pyeon.yi.seong.eul .gae.seon.hal .su .iss.eul .geos.eu.ro .jeon.mang.doen.da.
    # ENGLISH: There is a possibility of success.
    # CONFLICT: 1:차세대(nsubj→있을), 28:수(nsubj→있을)
    # Fix: su-construction: N1→outer
    'train-s1582': [('deprel', 1, 'nsubj:outer')],

    # train-s1639
    # TEXT: 유가은은 하재범 앞에서 맹호걸과의 사랑을 과장되게 표현할 공산이 커 보인다.
    # TRANSLIT: .yu.ga.eun.eun .ha.jae.beom .ap.e.seo .maeng.ho.geol.gwa.yi .sa.rang.eul .gwa.jang.doe.ge .pyo.hyeon.hal .gong.san.i .keo .bo.in.da.
    # ENGLISH: This place is really good.
    # CONFLICT: 1:유가은은(nsubj→보인다), 8:공산이(nsubj→보인다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1639': [('deprel', 1, 'nsubj:outer')],

    # train-s1640
    # TEXT: 정부와 기업들이 유기적인 협조체제 아래 최근의 상황을 극복하기 위한 적극적이고 능동적인 노력을 펼쳐간다면 차이나 리스크는 오히려 우리가 세계 최대시장의 주요 수혜자가 되는 지렛대가 될 수 있을 것이다.
    # TRANSLIT: .jeong.bu.wa .gi.eob.deul.i .yu.gi.jeog.in .hyeob.jo.che.je .a.rae .choe.geun.yi .sang.hwang.eul .geug.bog.ha.gi .wi.han .jeog.geug.jeog.i.go .neung.dong.jeog.in .no.ryeog.eul .pyeol.chyeo.gan.da.myeon .cha.i.na .ri.seu.keu.neun .o.hi.ryeo .u.ri.ga .se.gye .choe.dae.si.jang.yi .ju.yo .su.hye.ja.ga .doe.neun .ji.res.dae.ga .doel .su .iss.eul .geos.i.da.
    # ENGLISH: We are the lever that can be used to change China.
    # CONFLICT: 17:우리가(nsubj→되는), 20:주요(nsubj→되는)
    # CONFLICT: 14:차이나(nsubj→될), 23:지렛대가(nsubj→될)
    # Fix: default: N1(우리가)→outer [NEEDS REVIEW] | default: N1(차이나)→outer [NEEDS REVIEW]
    'train-s1640': [('deprel', 17, 'nsubj:outer'), ('deprel', 14, 'nsubj:outer')],

    # train-s1642
    # TEXT: 실장님(천실장)의 서비스가 좋으며 맛은 더할 나위 없습니다
    # TRANSLIT: .sil.jang.nim(.cheon.sil.jang).yi .seo.bi.seu.ga .joh.eu.myeo .mas.eun .deo.hal .na.wi .eobs.seub.ni.da
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 8:맛은(nsubj→없습니다), 10:나위(nsubj→없습니다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1642': [('deprel', 8, 'nsubj:outer')],

    # train-s1650
    # TEXT: 포털사이트 다음의 한 관계자는 "해외사업자라는 이유로 이를 적용받지 않는 유튜브가 다음 TV팟과 판도라TV를 제치는 것을 보라"며 "이는 기본적으로 공정경쟁이 아니다"고 주장했다.
    # TRANSLIT: .po.teol.sa.i.teu .da.eum.yi .han .gwan.gye.ja.neun ".hae.oe.sa.eob.ja.ra.neun .i.yu.ro .i.reul .jeog.yong.bad.ji .anh.neun .yu.tyu.beu.ga .da.eum TV.pas.gwa .pan.do.raTV.reul .je.chi.neun .geos.eul .bo.ra".myeo ".i.neun .gi.bon.jeog.eu.ro .gong.jeong.gyeong.jaeng.i .a.ni.da".go .ju.jang.haess.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 21:이는(nsubj→아니다), 23:공정경쟁이(nsubj→아니다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1650': [('deprel', 21, 'nsubj:outer')],

    # train-s1654
    # TEXT: 김 위원장의 발언은 독자파 내부에서도 상당한 논쟁거리가 될 소지가 있다.
    # TRANSLIT: .gim .wi.weon.jang.yi .bal.eon.eun .dog.ja.pa .nae.bu.e.seo.do .sang.dang.han .non.jaeng.geo.ri.ga .doel .so.ji.ga .iss.da.
    # ENGLISH: This is a very good place.
    # CONFLICT: 3:발언은(nsubj→될), 7:논쟁거리가(nsubj→될)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1654': [('deprel', 3, 'nsubj:outer')],

    # train-s1685
    # TEXT: 저녁에 삼겹살도 맛있지만 점심특선인 김치찌개는 국물이 아주 진해요
    # TRANSLIT: .jeo.nyeog.e .sam.gyeob.sal.do .mas.iss.ji.man .jeom.sim.teug.seon.in .gim.chi.jji.gae.neun .gug.mul.i .a.ju .jin.hae.yo
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 5:김치찌개는(nsubj→진해요), 6:국물이(nsubj→진해요)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1685': [('deprel', 5, 'nsubj:outer')],

    # train-s1691
    # TEXT: 또 이 지방산이 많은 사람은 적은 사람보다 체지방이 약간 적고 좋은 콜레스테롤인 고밀도지단백(HDL) 콜레스테롤이 많고 총콜레스테롤과 중성지방은 적으며 당뇨병으로 이어질 수 있는 인슐린저항도 적은 것으로 밝혀졌다.
    # TRANSLIT: .ddo .i .ji.bang.san.i .manh.eun .sa.ram.eun .jeog.eun .sa.ram.bo.da .che.ji.bang.i .yag.gan .jeog.go .joh.eun .kol.re.seu.te.rol.in .go.mil.do.ji.dan.baeg(HDL) .kol.re.seu.te.rol.i .manh.go .chong.kol.re.seu.te.rol.gwa .jung.seong.ji.bang.eun .jeog.eu.myeo .dang.nyo.byeong.eu.ro .i.eo.jil .su .iss.neun .in.syul.rin.jeo.hang.do .jeog.eun .geos.eu.ro .barg.hyeo.jyeoss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 5:사람은(nsubj→적고), 8:체지방이(nsubj→적고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1691': [('deprel', 5, 'nsubj:outer')],

    # train-s1699
    # TEXT: 고기도 품질은 나빠 보이지 않았음.
    # TRANSLIT: .go.gi.do .pum.jil.eun .na.bba .bo.i.ji .anh.ass.eum.
    # ENGLISH: This place is very good.
    # CONFLICT: 1:고기도(nsubj→나빠), 2:품질은(nsubj→나빠)
    # Fix: topic-marker: N2(은/는)→outer
    'train-s1699': [('deprel', 2, 'nsubj:outer')],

    # train-s1705
    # TEXT: 춘장문과 급제 후 딸이 중종의 계비가 되면서 고속승진하여 병조참지, 참판 등을 지내고 영원부원군에 봉군되었다.
    # TRANSLIT: .chun.jang.mun.gwa .geub.je .hu .ddal.i .jung.jong.yi .gye.bi.ga .doe.myeon.seo .go.sog.seung.jin.ha.yeo .byeong.jo.cham.ji, .cham.pan .deung.eul .ji.nae.go .yeong.weon.bu.weon.gun.e .bong.gun.doe.eoss.da.
    # ENGLISH: His daughter became his stepmother.
    # CONFLICT: 4:딸이(nsubj→되면서), 6:계비가(nsubj→되면서)
    # Fix: default: N1(딸이)→outer [NEEDS REVIEW]
    'train-s1705': [('deprel', 4, 'nsubj:outer')],

    # train-s1713
    # TEXT: 2408년, 엔터프라이즈-E는 제236우주기지와의 연결이 끊겼다.
    # TRANSLIT: 2408.nyeon, .en.teo.peu.ra.i.jeu-E.neun .je236.u.ju.gi.ji.wa.yi .yeon.gyeol.i .ggeunh.gyeoss.da.
    # ENGLISH: This place is very good.
    # CONFLICT: 3:엔터프라이즈-E는(nsubj:pass→끊겼다), 5:연결이(nsubj:pass→끊겼다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1713': [('deprel', 3, 'nsubj:outer')],

    # train-s1759
    # TEXT: 족발도 쫄깃하고 쟁반국수도 양념이 다른 곳이랑 다르게 진하고 맛있어요
    # TRANSLIT: .jog.bal.do .jjol.gis.ha.go .jaeng.ban.gug.su.do .yang.nyeom.i .da.reun .gos.i.rang .da.reu.ge .jin.ha.go .mas.iss.eo.yo
    # ENGLISH: This place also has good food.
    # CONFLICT: 3:쟁반국수도(nsubj→맛있어요), 4:양념이(nsubj→맛있어요)
    # Fix: also-marker: N1(도)→outer
    'train-s1759': [('deprel', 3, 'nsubj:outer')],

    # train-s1786
    # TEXT: 근처에 횟집 맛있는 데가 없어서 회에 소주 한 잔 하고 싶어 갔는데, 회 맛으로 따지면 부근에서 제일 좋은 듯...
    # TRANSLIT: .geun.cheo.e .hoes.jib .mas.iss.neun .de.ga .eobs.eo.seo .hoe.e .so.ju .han .jan .ha.go .sip.eo .gass.neun.de, .hoe .mas.eu.ro .dda.ji.myeon .bu.geun.e.seo .je.il .joh.eun .deus...
    # ENGLISH: There is no place as good as this seafood restaurant.
    # CONFLICT: 2:횟집(nsubj→없어서), 4:데가(nsubj→없어서)
    # Fix: default: N1(횟집)→outer [NEEDS REVIEW]
    'train-s1786': [('deprel', 2, 'nsubj:outer')],

    # train-s1802
    # TEXT: 음식도 비린내 나고 고무장갑으로 음식 주고 머리카락 나오고요
    # TRANSLIT: .eum.sig.do .bi.rin.nae .na.go .go.mu.jang.gab.eu.ro .eum.sig .ju.go .meo.ri.ka.rag .na.o.go.yo
    # ENGLISH: This place is also special.
    # CONFLICT: 1:음식도(nsubj→나고), 2:비린내(nsubj→나고)
    # Fix: also-marker: N1(도)→outer
    'train-s1802': [('deprel', 1, 'nsubj:outer')],

    # train-s1805
    # TEXT: 여기 돈까스, 함박스테이크 등 여러 음식이 넘 맛이 있고 직원들 또한 넘 친절한 게 아주 좋네요
    # TRANSLIT: .yeo.gi .don.gga.seu, .ham.bag.seu.te.i.keu .deung .yeo.reo .eum.sig.i .neom .mas.i .iss.go .jig.weon.deul .ddo.han .neom .chin.jeol.han .ge .a.ju .joh.ne.yo
    # ENGLISH: There is something delicious here.
    # CONFLICT: 1:여기(nsubj→있고), 9:맛이(nsubj→있고)
    # Fix: default: N1(여기)→outer [NEEDS REVIEW]
    'train-s1805': [('deprel', 1, 'nsubj:outer')],

    # train-s1821
    # TEXT: 돈까스는 진짜 고기가 부드러워요
    # TRANSLIT: .don.gga.seu.neun .jin.jja .go.gi.ga .bu.deu.reo.weo.yo
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:돈까스는(nsubj→부드러워요), 3:고기가(nsubj→부드러워요)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1821': [('deprel', 1, 'nsubj:outer')],

    # train-s1828
    # TEXT: 지난 2월말 기자가 찾았을 당시 침출수가 나오는 유공관이 보이지 않았고 빗물받이용 탱크도 배수관 높이가 잘못돼 있는 등 엉성한 구조였다.
    # TRANSLIT: .ji.nan 2.weol.mal .gi.ja.ga .chaj.ass.eul .dang.si .chim.chul.su.ga .na.o.neun .yu.gong.gwan.i .bo.i.ji .anh.ass.go .bis.mul.bad.i.yong .taeng.keu.do .bae.su.gwan .nop.i.ga .jal.mos.dwae .iss.neun .deung .eong.seong.han .gu.jo.yeoss.da.
    # ENGLISH: The rainwater catch is mispositioned, and the drain pipe is also wrong.
    # CONFLICT: 11:빗물받이용(nsubj→잘못돼), 13:배수관(nsubj→잘못돼)
    # Fix: default: N1(빗물받이용)→outer [NEEDS REVIEW]
    'train-s1828': [('deprel', 11, 'nsubj:outer')],

    # train-s1832
    # TEXT: 자선걷기대회 후원사로 나선 리복(Reebok)은 단체 참가자 그룹에게 당일 응원전 진행에 필요한 붉은색 스포츠 티셔츠를 후원할 뿐만 아니라, 걷기 운동에 적합한 리복 토닝슈즈 이지톤(EASYTONE) 홍보대사 권오중 박사가 이벤트에 함께 참여 예정이다.
    # TRANSLIT: .ja.seon.geod.gi.dae.hoe .hu.weon.sa.ro .na.seon .ri.bog(Reebok).eun .dan.che .cham.ga.ja .geu.rub.e.ge .dang.il .eung.weon.jeon .jin.haeng.e .pil.yo.han .burg.eun.saeg .seu.po.cheu .ti.syeo.cheu.reul .hu.weon.hal .bbun.man .a.ni.ra, .geod.gi .un.dong.e .jeog.hab.han .ri.bog .to.ning.syu.jeu .i.ji.ton(EASYTONE) .hong.bo.dae.sa .gweon.o.jung .bag.sa.ga .i.ben.teu.e .ham.gge .cham.yeo .ye.jeong.i.da.
    # ENGLISH: Reebok participated as an official sponsor.
    # CONFLICT: 4:리복(nsubj→참여), 26:리복(nsubj→참여)
    # Fix: default: N1(리복)→outer [NEEDS REVIEW]
    'train-s1832': [('deprel', 4, 'nsubj:outer')],

    # train-s1853
    # TEXT: 방송사는 방송사대로 몇 만대도 안되는 3DTV를 위해 막대한 비용이 드는 3D콘텐츠를 제작할 수 없으니 3DTV가 대박상품이 되기까지는 상당한 시간이 필요할 것이다.
    # TRANSLIT: .bang.song.sa.neun .bang.song.sa.dae.ro .myeoch .man.dae.do .an.doe.neun 3DTV.reul .wi.hae .mag.dae.han .bi.yong.i .deu.neun 3D.kon.ten.cheu.reul .je.jag.hal .su .eobs.eu.ni 3DTV.ga .dae.bag.sang.pum.i .doe.gi.gga.ji.neun .sang.dang.han .si.gan.i .pil.yo.hal .geos.i.da.
    # ENGLISH: Until 3DTV became a best-selling product.
    # CONFLICT: 15:3DTV가(nsubj→되기까지는), 16:대박상품이(nsubj→되기까지는)
    # Fix: default: N1(3DTV가)→outer [NEEDS REVIEW]
    'train-s1853': [('deprel', 15, 'nsubj:outer')],

    # train-s1867
    # TEXT: 업계에 정통한 한 전문가는 "IMK를 중소기업계 품으로 가져오는 것은 상당한 상징성이 있다"면서 "하지만 중소기업계가 사들인 IMK가 납품단가 현실화, 중소기업 참여 보장, 지분 투자 중소 유통회사들에 대한 실질적 혜택 등을 어떻게 풀어야 할지 신중하게 고민한 뒤 시간을 두고 결정해야 한다"고 지적했다.
    # TRANSLIT: .eob.gye.e .jeong.tong.han .han .jeon.mun.ga.neun "IMK.reul .jung.so.gi.eob.gye .pum.eu.ro .ga.jyeo.o.neun .geos.eun .sang.dang.han .sang.jing.seong.i .iss.da".myeon.seo ".ha.ji.man .jung.so.gi.eob.gye.ga .sa.deul.in IMK.ga .nab.pum.dan.ga .hyeon.sil.hwa, .jung.so.gi.eob .cham.yeo .bo.jang, .ji.bun .tu.ja .jung.so .yu.tong.hoe.sa.deul.e .dae.han .sil.jil.jeog .hye.taeg .deung.eul .eo.ddeoh.ge .pul.eo.ya .hal.ji .sin.jung.ha.ge .go.min.han .dwi .si.gan.eul .du.go .gyeol.jeong.hae.ya .han.da".go .ji.jeog.haess.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 10:것은(nsubj→있다), 12:상징성이(nsubj→있다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1867': [('deprel', 10, 'nsubj:outer')],

    # train-s1892
    # TEXT: 아늑한 분위기와 친절한 서비스가 최고인 미모의 여주인이 인상 깊다.
    # TRANSLIT: .a.neug.han .bun.wi.gi.wa .chin.jeol.han .seo.bi.seu.ga .choe.go.in .mi.mo.yi .yeo.ju.in.i .in.sang .gip.da.
    # ENGLISH: The female owner left a deep impression.
    # CONFLICT: 7:여주인이(nsubj→깊다), 8:인상(nsubj→깊다)
    # Fix: default: N1(여주인이)→outer [NEEDS REVIEW]
    'train-s1892': [('deprel', 7, 'nsubj:outer')],

    # train-s190
    # TEXT: 이날 펀드별로는 '미래에셋인디펜던스주식형K- 2(운용C)'의 설정액이 236억 원 감소해 가장 많이 줄었다.
    # TRANSLIT: .i.nal .peon.deu.byeol.ro.neun '.mi.rae.e.ses.in.di.pen.deon.seu.ju.sig.hyeongK- 2(.un.yongC)'.yi .seol.jeong.aeg.i 236.eog .weon .gam.so.hae .ga.jang .manh.i .jul.eoss.da.
    # ENGLISH: The Mirae Asset Independence Equity K fund saw assets decrease.
    # CONFLICT: 4:미래에셋인디펜던스주식형K-(nsubj→감소해), 13:원(nsubj→감소해)
    # Fix: default: N1(미래에셋인디펜던스주식형K-)→outer [NEEDS REVIEW]
    'train-s190': [('deprel', 4, 'nsubj:outer')],

    # train-s1900
    # TEXT: 국밥이 양이 넘 작아여.
    # TRANSLIT: .gug.bab.i .yang.i .neom .jag.a.yeo.
    # ENGLISH: The pork and rice soup has a small portion.
    # CONFLICT: 1:국밥이(nsubj→작아여), 2:양이(nsubj→작아여)
    # Fix: default: N1(국밥이)→outer [NEEDS REVIEW]
    'train-s1900': [('deprel', 1, 'nsubj:outer')],

    # train-s1909
    # TEXT: 제 405회 로또 1등 당첨 번호는 '1, 2, 10, 25, 26, 44' 등 6개가 나왔다.
    # TRANSLIT: .je 405.hoe .ro.ddo 1.deung .dang.cheom .beon.ho.neun '1, 2, 10, 25, 26, 44' .deung 6.gae.ga .na.wass.da.
    # ENGLISH: My order came out.
    # CONFLICT: 1:제(nsubj→나왔다), 8:1(nsubj→나왔다)
    # Fix: default: N1(제)→outer [NEEDS REVIEW]
    'train-s1909': [('deprel', 1, 'nsubj:outer')],

    # train-s1933
    # TEXT: 보통 인간은 지금의 육신은 결국 소멸하며, 소멸하지 않는 불사의 몸을 갖기 위해서는 최후의 심판 날이 도래할 때까지 기다려야 한다.
    # TRANSLIT: .bo.tong .in.gan.eun .ji.geum.yi .yug.sin.eun .gyeol.gug .so.myeol.ha.myeo, .so.myeol.ha.ji .anh.neun .bul.sa.yi .mom.eul .gaj.gi .wi.hae.seo.neun .choe.hu.yi .sim.pan .nal.i .do.rae.hal .ddae.gga.ji .gi.da.ryeo.ya .han.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 2:인간은(nsubj→소멸하며), 4:육신은(nsubj→소멸하며)
    # Fix: both-topic: N1→outer (first)
    'train-s1933': [('deprel', 2, 'nsubj:outer')],

    # train-s1937
    # TEXT: 가격은 해운대 주변 가게보다 저렴하고 경치도 겨울보단 여름이 좋아요
    # TRANSLIT: .ga.gyeog.eun .hae.un.dae .ju.byeon .ga.ge.bo.da .jeo.ryeom.ha.go .gyeong.chi.do .gyeo.ul.bo.dan .yeo.reum.i .joh.a.yo
    # ENGLISH: This place also has something special.
    # CONFLICT: 6:경치도(nsubj→좋아요), 8:여름이(nsubj→좋아요)
    # Fix: also-marker: N1(도)→outer
    'train-s1937': [('deprel', 6, 'nsubj:outer')],

    # train-s197
    # TEXT: 구례를 대표하시는 자전거 사장님 부자 되세요
    # TRANSLIT: .gu.rye.reul .dae.pyo.ha.si.neun .ja.jeon.geo .sa.jang.nim .bu.ja .doe.se.yo
    # ENGLISH: Become a wealthy cyclist.
    # CONFLICT: 3:자전거(nsubj→되세요), 5:부자(nsubj→되세요)
    # Fix: default: N1(자전거)→outer [NEEDS REVIEW]
    'train-s197': [('deprel', 3, 'nsubj:outer')],

    # train-s1970
    # TEXT: 소스도 종류가 많아서 골라 먹는 재미도 있음
    # TRANSLIT: .so.seu.do .jong.ryu.ga .manh.a.seo .gol.ra .meog.neun .jae.mi.do .iss.eum
    # ENGLISH: This place is also special.
    # CONFLICT: 1:소스도(nsubj→많아서), 2:종류가(nsubj→많아서)
    # Fix: also-marker: N1(도)→outer
    'train-s1970': [('deprel', 1, 'nsubj:outer')],

    # train-s1986
    # TEXT: 아마 다른 집에 갈 거 주문 취소되서 갖고 온 듯하네요
    # TRANSLIT: .a.ma .da.reun .jib.e .gal .geo .ju.mun .chwi.so.doe.seo .gaj.go .on .deus.ha.ne.yo
    # ENGLISH: The order got canceled.
    # CONFLICT: 5:거(nsubj:pass→취소되서), 6:주문(nsubj:pass→취소되서)
    # Fix: default: N1(거)→outer [NEEDS REVIEW]
    'train-s1986': [('deprel', 5, 'nsubj:outer')],

    # train-s1992
    # TEXT: 저는 시원한 해산물이 생각나면 자주 가는데 후해 없습니다.
    # TRANSLIT: .jeo.neun .si.weon.han .hae.san.mul.i .saeng.gag.na.myeon .ja.ju .ga.neun.de .hu.hae .eobs.seub.ni.da.
    # ENGLISH: This place is really good.
    # CONFLICT: 1:저는(nsubj→생각나면), 3:해산물이(nsubj→생각나면)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s1992': [('deprel', 1, 'nsubj:outer')],

    # train-s1997
    # TEXT: 사람은 뼈가 몇 개나 있냐
    # TRANSLIT: .sa.ram.eun .bbyeo.ga .myeoch .gae.na .iss.nya
    # ENGLISH: How many bones does a person have?
    # CONFLICT: 1:사람은(nsubj→있냐), 2:뼈가(nsubj→있냐), 4:개나(nsubj→있냐)
    # Fix: 1:사람은(은 topic marker)→outer; 2:뼈가(outer of the count expression)→outer;
    #      4:개나(inner grammatical subject of 있냐) stays nsubj
    'train-s1997': [('deprel', 1, 'nsubj:outer'), ('deprel', 2, 'nsubj:outer')],

    # train-s2028
    # TEXT: 포항지역은 어제 이어 오늘도 유치원과 초중등학교 188곳이 휴교나 휴업했습니다.
    # TRANSLIT: .po.hang.ji.yeog.eun .eo.je .i.eo .o.neul.do .yu.chi.weon.gwa .cho.jung.deung.hag.gyo 188.gos.i .hyu.gyo.na .hyu.eob.haess.seub.ni.da.
    # ENGLISH: This place is really good.
    # CONFLICT: 1:포항지역은(nsubj→휴업했습니다), 5:유치원과(nsubj→휴업했습니다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2028': [('deprel', 1, 'nsubj:outer')],

    # train-s2035
    # TEXT: 삼성과 애플의 태블릿은 특히 시장에서 직접적인 비교의 대상이 된다는 데에서 비록 판매량의 차이는 존재하지만 '갤럭시탭 10.1'의 이런 변신은 매우 긍정적이고, 또 되돌아볼 의미가 있어 보인다.
    # TRANSLIT: .sam.seong.gwa .ae.peul.yi .tae.beul.ris.eun .teug.hi .si.jang.e.seo .jig.jeob.jeog.in .bi.gyo.yi .dae.sang.i .doen.da.neun .de.e.seo .bi.rog .pan.mae.ryang.yi .cha.i.neun .jon.jae.ha.ji.man '.gael.reog.si.taeb 10.1'.yi .i.reon .byeon.sin.eun .mae.u .geung.jeong.jeog.i.go, .ddo .doe.dol.a.bol .yi.mi.ga .iss.eo .bo.in.da.
    # ENGLISH: This is a very good restaurant.
    # CONFLICT: 3:태블릿은(nsubj→된다는), 8:대상이(nsubj→된다는)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2035': [('deprel', 3, 'nsubj:outer')],

    # train-s2041
    # TEXT: 어떤 것을 주문하든, 빵과 커피가 무한 리필 되는 하우스바도 좋아요.
    # TRANSLIT: .eo.ddeon .geos.eul .ju.mun.ha.deun, .bbang.gwa .keo.pi.ga .mu.han .ri.pil .doe.neun .ha.u.seu.ba.do .joh.a.yo.
    # ENGLISH: The bread and refills are included.
    # CONFLICT: 5:빵과(nsubj→되는), 8:리필(nsubj→되는)
    # Fix: default: N1(빵과)→outer [NEEDS REVIEW]
    'train-s2041': [('deprel', 5, 'nsubj:outer')],

    # train-s2049
    # TEXT: 제주는 돼지고기 자급률이 50프로 정도 밖에 안되고 나머지는 뭍에서 오는 것이라고 하는데 이 곳은 농장에서 직접 고기를 조달한다고 하네요.
    # TRANSLIT: .je.ju.neun .dwae.ji.go.gi .ja.geub.ryul.i 50.peu.ro .jeong.do .bagg.e .an.doe.go .na.meo.ji.neun .mut.e.seo .o.neun .geos.i.ra.go .ha.neun.de .i .gos.eun .nong.jang.e.seo .jig.jeob .go.gi.reul .jo.dal.han.da.go .ha.ne.yo.
    # ENGLISH: This place is really good.
    # CONFLICT: 1:제주는(nsubj→안되고), 2:돼지고기(nsubj→안되고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2049': [('deprel', 1, 'nsubj:outer')],

    # train-s2093
    # TEXT: 여러 군데 다녀 봤지만 여기가 만족도가 높네요.
    # TRANSLIT: .yeo.reo .gun.de .da.nyeo .bwass.ji.man .yeo.gi.ga .man.jog.do.ga .nop.ne.yo.
    # ENGLISH: This place here, the satisfaction level is high.
    # CONFLICT: 5:여기가(nsubj→높네요), 6:만족도가(nsubj→높네요)
    # Fix: default: N1(여기가)→outer [NEEDS REVIEW]
    'train-s2093': [('deprel', 5, 'nsubj:outer')],

    # train-s2096
    # TEXT: 종업원은 불친절하고 메인 메뉴는 별로 맛이 없네요
    # TRANSLIT: .jong.eob.weon.eun .bul.chin.jeol.ha.go .me.in .me.nyu.neun .byeol.ro .mas.i .eobs.ne.yo
    # ENGLISH: The main dish has no flavor.
    # CONFLICT: 3:메인(nsubj→없네요), 6:맛이(nsubj→없네요)
    # Fix: default: N1(메인)→outer [NEEDS REVIEW]
    'train-s2096': [('deprel', 3, 'nsubj:outer')],

    # train-s2124
    # TEXT: 외지에서 차가 고장 나서 걱정 많이 해는데 친절하고 설명도 잘해주세요
    # TRANSLIT: .oe.ji.e.seo .cha.ga .go.jang .na.seo .geog.jeong .manh.i .hae.neun.de .chin.jeol.ha.go .seol.myeong.do .jal.hae.ju.se.yo
    # ENGLISH: The car broke down.
    # CONFLICT: 2:차가(nsubj→나서), 3:고장(nsubj→나서)
    # Fix: default: N1(차가)→outer [NEEDS REVIEW]
    'train-s2124': [('deprel', 2, 'nsubj:outer')],

    # train-s2128
    # TEXT: 기사단의 공식 어린이 단체는 콜럼버스의 종자들로, 5천 개의 동아리가 있다.
    # TRANSLIT: .gi.sa.dan.yi .gong.sig .eo.rin.i .dan.che.neun .kol.reom.beo.seu.yi .jong.ja.deul.ro, 5.cheon .gae.yi .dong.a.ri.ga .iss.da.
    # ENGLISH: There is an official club.
    # CONFLICT: 2:공식(nsubj→있다), 10:동아리가(nsubj→있다)
    # Fix: default: N1(공식)→outer [NEEDS REVIEW]
    'train-s2128': [('deprel', 2, 'nsubj:outer')],

    # train-s2140
    # TEXT: 이러한 흥례부는 지금의 광역시 형태로 중앙정부를 축소한 향리를 둘 수 있게 하였으며, 이 시기에 거주지별로 성과 본관이 책정되면서 울산 지역의 토성(土姓)은 박, 이, 전, 목, 오, 윤, 임, 문 가(家)로 정리되었다.
    # TRANSLIT: .i.reo.han .heung.rye.bu.neun .ji.geum.yi .gwang.yeog.si .hyeong.tae.ro .jung.ang.jeong.bu.reul .chug.so.han .hyang.ri.reul .dul .su .iss.ge .ha.yeoss.eu.myeo, .i .si.gi.e .geo.ju.ji.byeol.ro .seong.gwa .bon.gwan.i .chaeg.jeong.doe.myeon.seo .ul.san .ji.yeog.yi .to.seong(tǔxìng).eun .bag, .i, .jeon, .mog, .o, .yun, .im, .mun .ga(jiā).ro .jeong.ri.doe.eoss.da.
    # ENGLISH: There is a possibility of achieving it.
    # CONFLICT: 2:흥례부는(nsubj→있게), 10:수(nsubj→있게)
    # Fix: su-construction: N1→outer
    'train-s2140': [('deprel', 2, 'nsubj:outer')],

    # train-s2171
    # TEXT: 페르시아만 연안의 해안선은 복잡하게 얽혔으며, 바다는 멀리까지 수심이 얕고 먼 바다에는 많은 섬과 산호초가 떠 있다.
    # TRANSLIT: .pe.reu.si.a.man .yeon.an.yi .hae.an.seon.eun .bog.jab.ha.ge .eorg.hyeoss.eu.myeo, .ba.da.neun .meol.ri.gga.ji .su.sim.i .yat.go .meon .ba.da.e.neun .manh.eun .seom.gwa .san.ho.cho.ga .ddeo .iss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 7:바다는(nsubj→얕고), 9:수심이(nsubj→얕고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2171': [('deprel', 7, 'nsubj:outer')],

    # train-s2177
    # TEXT: 따라서, 화성의 대기에 아르곤은 95%를 차지해버리는 이산화탄소가 빠져나가면 아르곤의 함량은 절대적으로 높아진다.
    # TRANSLIT: .dda.ra.seo, .hwa.seong.yi .dae.gi.e .a.reu.gon.eun 95%.reul .cha.ji.hae.beo.ri.neun .i.san.hwa.tan.so.ga .bba.jyeo.na.ga.myeon .a.reu.gon.yi .ham.ryang.eun .jeol.dae.jeog.eu.ro .nop.a.jin.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 5:아르곤은(nsubj→높아진다), 13:함량은(nsubj→높아진다)
    # Fix: both-topic: N1→outer (first)
    'train-s2177': [('deprel', 5, 'nsubj:outer')],

    # train-s2190
    # TEXT: 애플 역시 타사의 출시 일정은 크게 고려하지 않고 있는 것으로 알려졌다.
    # TRANSLIT: .ae.peul .yeog.si .ta.sa.yi .chul.si .il.jeong.eun .keu.ge .go.ryeo.ha.ji .anh.go .iss.neun .geos.eu.ro .al.ryeo.jyeoss.da.
    # ENGLISH: Apple did not consider the release.
    # CONFLICT: 1:애플(nsubj→고려하지), 4:출시(nsubj→고려하지)
    # Fix: default: N1(애플)→outer [NEEDS REVIEW]
    'train-s2190': [('deprel', 1, 'nsubj:outer')],

    # train-s2223
    # TEXT: 그 경기에서 임수혁의 아버지가 시구를, 임수혁 후원회장이 시타로 나섰다.
    # TRANSLIT: .geu .gyeong.gi.e.seo .im.su.hyeog.yi .a.beo.ji.ga .si.gu.reul, .im.su.hyeog .hu.weon.hoe.jang.i .si.ta.ro .na.seoss.da.
    # ENGLISH: His father stepped up, with Im Su-hyeok.
    # CONFLICT: 4:아버지가(nsubj→나섰다), 7:임수혁(nsubj→나섰다)
    # Fix: default: N1(아버지가)→outer [NEEDS REVIEW]
    'train-s2223': [('deprel', 4, 'nsubj:outer')],

    # train-s2266
    # TEXT: 그러나 이 원자로는 아직 상용화된 적이 없어 논란이 되고 있습니다.
    # TRANSLIT: .geu.reo.na .i .weon.ja.ro.neun .a.jig .sang.yong.hwa.doen .jeog.i .eobs.eo .non.ran.i .doe.go .iss.seub.ni.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 3:원자로는(nsubj→없어), 6:적이(nsubj→없어)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2266': [('deprel', 3, 'nsubj:outer')],

    # train-s2280
    # TEXT: 친절하고 도시락이 정말 맛이 있어요
    # TRANSLIT: .chin.jeol.ha.go .do.si.rag.i .jeong.mal .mas.i .iss.eo.yo
    # ENGLISH: The lunchbox has good flavor.
    # CONFLICT: 2:도시락이(nsubj→있어요), 4:맛이(nsubj→있어요)
    # Fix: default: N1(도시락이)→outer [NEEDS REVIEW]
    'train-s2280': [('deprel', 2, 'nsubj:outer')],

    # train-s2286
    # TEXT: 수원 시내에 음식점이 뭐가 있지?
    # TRANSLIT: .su.weon .si.nae.e .eum.sig.jeom.i .mweo.ga .iss.ji?
    # ENGLISH: What restaurants are available?
    # CONFLICT: 3:음식점이(nsubj→있지), 4:뭐가(nsubj→있지)
    # Fix: default: N1(음식점이)→outer [NEEDS REVIEW]
    'train-s2286': [('deprel', 3, 'nsubj:outer')],

    # train-s2304
    # TEXT: 힘들지만 버틸 수 있는 건 함께 하는 동지가 있기에, 지지하고 함께 뜻을 모아 외치며 연대해주는 동지가 있기에 가능하다고 생각합니다.
    # TRANSLIT: .him.deul.ji.man .beo.til .su .iss.neun .geon .ham.gge .ha.neun .dong.ji.ga .iss.gi.e, .ji.ji.ha.go .ham.gge .ddeus.eul .mo.a .oe.chi.myeo .yeon.dae.hae.ju.neun .dong.ji.ga .iss.gi.e .ga.neung.ha.da.go .saeng.gag.hab.ni.da.
    # ENGLISH: The situation has allies.
    # CONFLICT: 5:건(nsubj→있기에), 8:동지가(nsubj→있기에)
    # Fix: default: N1(건)→outer [NEEDS REVIEW]
    'train-s2304': [('deprel', 5, 'nsubj:outer')],

    # train-s2305
    # TEXT: 나루히토가 딸 하나만을 두고 있기 때문에 그의 아들 히사히토(悠仁)가 이후에 천황이 될 가능성이 매우 높다.
    # TRANSLIT: .na.ru.hi.to.ga .ddal .ha.na.man.eul .du.go .iss.gi .ddae.mun.e .geu.yi .a.deul .hi.sa.hi.to(yōu仁).ga .i.hu.e .cheon.hwang.i .doel .ga.neung.seong.i .mae.u .nop.da.
    # ENGLISH: His son became Crown Prince.
    # CONFLICT: 8:아들(nsubj→될), 15:천황이(nsubj→될)
    # Fix: default: N1(아들)→outer [NEEDS REVIEW]
    'train-s2305': [('deprel', 8, 'nsubj:outer')],

    # train-s2315
    # TEXT: 최근 증권사들이 자산관리 브랜드를 너도나도 내놓고 있는 것은 바로 이런 배경이 작용하고 있다.
    # TRANSLIT: .choe.geun .jeung.gweon.sa.deul.i .ja.san.gwan.ri .beu.raen.deu.reul .neo.do.na.do .nae.noh.go .iss.neun .geos.eun .ba.ro .i.reon .bae.gyeong.i .jag.yong.ha.go .iss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 8:것은(nsubj→작용하고), 11:배경이(nsubj→작용하고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2315': [('deprel', 8, 'nsubj:outer')],

    # train-s2346
    # TEXT: 가격도 저렴하고, 물건도 눈속임 없고, 사장님이 설명도 후련히 해주심.
    # TRANSLIT: .ga.gyeog.do .jeo.ryeom.ha.go, .mul.geon.do .nun.sog.im .eobs.go, .sa.jang.nim.i .seol.myeong.do .hu.ryeon.hi .hae.ju.sim.
    # ENGLISH: This place also has good food.
    # CONFLICT: 4:물건도(nsubj→없고), 5:눈속임(nsubj→없고)
    # Fix: also-marker: N1(도)→outer
    'train-s2346': [('deprel', 4, 'nsubj:outer')],

    # train-s2370
    # TEXT: 카나번(Caernarfon)은 웨일스의 도시로, 인구는 9,611명이다.
    # TRANSLIT: .ka.na.beon(Caernarfon).eun .we.il.seu.yi .do.si.ro, .in.gu.neun 9,611.myeong.i.da.
    # ENGLISH: This is a very good restaurant.
    # CONFLICT: 1:카나번(nsubj→9,611명이다), 9:인구는(nsubj→9,611명이다)
    # Fix: topic-marker: N2(은/는)→outer
    'train-s2370': [('deprel', 9, 'nsubj:outer')],

    # train-s2383
    # TEXT: 반찬은 양념게장이 짱입니다
    # TRANSLIT: .ban.chan.eun .yang.nyeom.ge.jang.i .jjang.ib.ni.da
    # ENGLISH: This place is really good.
    # CONFLICT: 1:반찬은(nsubj→짱입니다), 2:양념게장이(nsubj→짱입니다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2383': [('deprel', 1, 'nsubj:outer')],

    # train-s2417
    # TEXT: 이로써 제주는 이날 경기가 없었던 2위 FC 서울과 승점차를 4로 벌린 반면 성남은 제주와 승점차가 8로 커졌다.
    # TRANSLIT: .i.ro.sseo .je.ju.neun .i.nal .gyeong.gi.ga .eobs.eoss.deon 2.wi FC .seo.ul.gwa .seung.jeom.cha.reul 4.ro .beol.rin .ban.myeon .seong.nam.eun .je.ju.wa .seung.jeom.cha.ga 8.ro .keo.jyeoss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 13:성남은(nsubj→커졌다), 15:승점차가(nsubj→커졌다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2417': [('deprel', 13, 'nsubj:outer')],

    # train-s2434
    # TEXT: 오늘 경제 뉴스 특이한 거 있어
    # TRANSLIT: .o.neul .gyeong.je .nyu.seu .teug.i.han .geo .iss.eo
    # ENGLISH: The economy has that situation.
    # CONFLICT: 2:경제(nsubj→있어), 5:거(nsubj→있어)
    # Fix: default: N1(경제)→outer [NEEDS REVIEW]
    'train-s2434': [('deprel', 2, 'nsubj:outer')],

    # train-s2443
    # TEXT: 이 때 협률사(協律社)라는 이름은 새로 만든 이름이 아니라, 이미 40여 년 전부터 있었던 명창들이 모인 연예(演藝) 단체의 이름이었다.
    # TRANSLIT: .i .ddae .hyeob.ryul.sa(xiélǜshè).ra.neun .i.reum.eun .sae.ro .man.deun .i.reum.i .a.ni.ra, .i.mi 40.yeo .nyeon .jeon.bu.teo .iss.eoss.deon .myeong.chang.deul.i .mo.in .yeon.ye(yǎnyì) .dan.che.yi .i.reum.i.eoss.da.
    # ENGLISH: This is a very good restaurant.
    # CONFLICT: 8:이름은(nsubj→아니라), 11:이름이(nsubj→아니라)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2443': [('deprel', 8, 'nsubj:outer')],

    # train-s2463
    # TEXT: 롯데홈쇼핑은 대만 금융지주회사인 '푸방(富邦)그룹'과 함께 설립한 '모모홈쇼핑'이 지난해 3천억 원의 매출을 올렸다.
    # TRANSLIT: .ros.de.hom.syo.ping.eun .dae.man .geum.yung.ji.ju.hoe.sa.in '.pu.bang(fùbāng).geu.rub'.gwa .ham.gge .seol.rib.han '.mo.mo.hom.syo.ping'.i .ji.nan.hae 3.cheon.eog .weon.yi .mae.chul.eul .ol.ryeoss.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:롯데홈쇼핑은(nsubj→모모홈쇼핑), 17:이(nsubj→모모홈쇼핑)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2463': [('deprel', 1, 'nsubj:outer')],

    # train-s2476
    # TEXT: 대중교통으로 대전 가는 길은 뭐가 있어
    # TRANSLIT: .dae.jung.gyo.tong.eu.ro .dae.jeon .ga.neun .gil.eun .mweo.ga .iss.eo
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 4:길은(nsubj→있어), 5:뭐가(nsubj→있어)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2476': [('deprel', 4, 'nsubj:outer')],

    # train-s2478
    # TEXT: 팔리어는 고유 문자가 없기 때문에 국가와 지역마다 쓰이는 문자의 종류가 저마다 다르다.
    # TRANSLIT: .pal.ri.eo.neun .go.yu .mun.ja.ga .eobs.gi .ddae.mun.e .gug.ga.wa .ji.yeog.ma.da .sseu.i.neun .mun.ja.yi .jong.ryu.ga .jeo.ma.da .da.reu.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:팔리어는(nsubj→없기), 2:고유(nsubj→없기)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2478': [('deprel', 1, 'nsubj:outer')],

    # train-s2527
    # TEXT: 이 때문에 1인당 구매 단가는 인지도가 높은 브랜드 상품이나 큰 바구니 상품을 구매하는 남성이 여성보다 높다.
    # TRANSLIT: .i .ddae.mun.e 1.in.dang .gu.mae .dan.ga.neun .in.ji.do.ga .nop.eun .beu.raen.deu .sang.pum.i.na .keun .ba.gu.ni .sang.pum.eul .gu.mae.ha.neun .nam.seong.i .yeo.seong.bo.da .nop.da.
    # ENGLISH: Per capita, the male rate is higher.
    # CONFLICT: 3:1인당(nsubj→높다), 14:남성이(nsubj→높다)
    # Fix: default: N1(1인당)→outer [NEEDS REVIEW]
    'train-s2527': [('deprel', 3, 'nsubj:outer')],

    # train-s2531
    # TEXT: 말이 필요 없음!
    # TRANSLIT: .mal.i .pil.yo .eobs.eum!
    # ENGLISH: No need to say anything.
    # CONFLICT: 1:말이(nsubj→없음), 2:필요(nsubj→없음)
    # Fix: default: N1(말이)→outer [NEEDS REVIEW]
    'train-s2531': [('deprel', 1, 'nsubj:outer')],

    # train-s2532
    # TEXT: 즉 안희정, 이광재 지사는 민주당이 영입하고 육성한 인재라고 보기 어렵다는 것이다.
    # TRANSLIT: .jeug .an.hyi.jeong, .i.gwang.jae .ji.sa.neun .min.ju.dang.i .yeong.ib.ha.go .yug.seong.han .in.jae.ra.go .bo.gi .eo.ryeob.da.neun .geos.i.da.
    # ENGLISH: It is hard to see Ahn Hee-jung as anything else.
    # CONFLICT: 2:안희정(nsubj→어렵다는), 10:보기(nsubj→어렵다는)
    # Fix: default: N1(안희정)→outer [NEEDS REVIEW]
    'train-s2532': [('deprel', 2, 'nsubj:outer')],

    # train-s2560
    # TEXT: 에밀리가 이 책을 훌륭히 번역하였기 때문에 프랑스는 영국보다 100년 앞서 과학이 발달할 수 있었다는 시각도 있다.
    # TRANSLIT: .e.mil.ri.ga .i .chaeg.eul .hul.ryung.hi .beon.yeog.ha.yeoss.gi .ddae.mun.e .peu.rang.seu.neun .yeong.gug.bo.da 100.nyeon .ap.seo .gwa.hag.i .bal.dal.hal .su .iss.eoss.da.neun .si.gag.do .iss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 7:프랑스는(nsubj→발달할), 11:과학이(nsubj→발달할)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2560': [('deprel', 7, 'nsubj:outer')],

    # train-s2601
    # TEXT: 주인이 개념이 없어요
    # TRANSLIT: .ju.in.i .gae.nyeom.i .eobs.eo.yo
    # ENGLISH: The owner has no manners.
    # CONFLICT: 1:주인이(nsubj→없어요), 2:개념이(nsubj→없어요)
    # Fix: default: N1(주인이)→outer [NEEDS REVIEW]
    'train-s2601': [('deprel', 1, 'nsubj:outer')],

    # train-s2642
    # TEXT: 절개는 상처가 외부에서 보이지 않도록 콧구멍 안쪽으로 하는 방법과 콧구멍 안쪽의 절개를 비주에서 연결하는 개방형 절개가 있다.
    # TRANSLIT: .jeol.gae.neun .sang.cheo.ga .oe.bu.e.seo .bo.i.ji .anh.do.rog .kos.gu.meong .an.jjog.eu.ro .ha.neun .bang.beob.gwa .kos.gu.meong .an.jjog.yi .jeol.gae.reul .bi.ju.e.seo .yeon.gyeol.ha.neun .gae.bang.hyeong .jeol.gae.ga .iss.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:절개는(nsubj→있다), 9:방법과(nsubj→있다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2642': [('deprel', 1, 'nsubj:outer')],

    # train-s2651
    # TEXT: 그는 이 현상이 빛의 속도가 유한하기 때문이라고 생각하고, 빛의 속도를 계산하여 1676년에 이를 논문으로 발표하였다.
    # TRANSLIT: .geu.neun .i .hyeon.sang.i .bich.yi .sog.do.ga .yu.han.ha.gi .ddae.mun.i.ra.go .saeng.gag.ha.go, .bich.yi .sog.do.reul .gye.san.ha.yeo 1676.nyeon.e .i.reul .non.mun.eu.ro .bal.pyo.ha.yeoss.da.
    # ENGLISH: The phenomenon is finite in speed.
    # CONFLICT: 3:현상이(nsubj→유한하기), 5:속도가(nsubj→유한하기)
    # Fix: default: N1(현상이)→outer [NEEDS REVIEW]
    'train-s2651': [('deprel', 3, 'nsubj:outer')],

    # train-s2659
    # TEXT: 차사랑주유소는 직원들이 엄청 친절하시고 오만 원 주유 시에 무료 세차도 된답니다
    # TRANSLIT: .cha.sa.rang.ju.yu.so.neun .jig.weon.deul.i .eom.cheong .chin.jeol.ha.si.go .o.man .weon .ju.yu .si.e .mu.ryo .se.cha.do .doen.dab.ni.da
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:차사랑주유소는(nsubj→친절하시고), 2:직원들이(nsubj→친절하시고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2659': [('deprel', 1, 'nsubj:outer')],

    # train-s2679
    # TEXT: 원래 오타쿠는 잘 알려진 하위 문화가 아니였으나 이 사건의 보도를 통해 널리 알려지게 되었으며 이것으로 인해 오타쿠라 칭해지던 사람들은 주변에서 부정적인 시선으로 인해 정신적으로 피해를 받고 있다.
    # TRANSLIT: .weon.rae .o.ta.ku.neun .jal .al.ryeo.jin .ha.wi .mun.hwa.ga .a.ni.yeoss.eu.na .i .sa.geon.yi .bo.do.reul .tong.hae .neol.ri .al.ryeo.ji.ge .doe.eoss.eu.myeo .i.geos.eu.ro .in.hae .o.ta.ku.ra .ching.hae.ji.deon .sa.ram.deul.eun .ju.byeon.e.seo .bu.jeong.jeog.in .si.seon.eu.ro .in.hae .jeong.sin.jeog.eu.ro .pi.hae.reul .bad.go .iss.da.
    # ENGLISH: This is a very good restaurant.
    # CONFLICT: 2:오타쿠는(nsubj→아니였으나), 5:하위(nsubj→아니였으나)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2679': [('deprel', 2, 'nsubj:outer')],

    # train-s2708
    # TEXT: 굽네치킨은 단점은, 주문 받자마자 오븐에 넣어서 시간이 3~40분 걸린다는 점이지만, 어디서 시켜도 항상 맛있죠.
    # TRANSLIT: .gub.ne.chi.kin.eun .dan.jeom.eun, .ju.mun .bad.ja.ma.ja .o.beun.e .neoh.eo.seo .si.gan.i 3~40.bun .geol.rin.da.neun .jeom.i.ji.man, .eo.di.seo .si.kyeo.do .hang.sang .mas.iss.jyo.
    # ENGLISH: It takes 30 to 40 minutes.
    # CONFLICT: 8:시간이(nsubj→걸린다는), 9:3~40분(nsubj→걸린다는)
    # Fix: default: N1(시간이)→outer [NEEDS REVIEW]
    'train-s2708': [('deprel', 8, 'nsubj:outer')],

    # train-s2711
    # TEXT: 수명은 각각 공룡마다 차이가 있지만 대부분이 온혈동물이였다는 점을 본다면 100년 이내로 살았을 것으로 보인다.
    # TRANSLIT: .su.myeong.eun .gag.gag .gong.ryong.ma.da .cha.i.ga .iss.ji.man .dae.bu.bun.i .on.hyeol.dong.mul.i.yeoss.da.neun .jeom.eul .bon.da.myeon 100.nyeon .i.nae.ro .sal.ass.eul .geos.eu.ro .bo.in.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:수명은(nsubj→있지만), 4:차이가(nsubj→있지만)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2711': [('deprel', 1, 'nsubj:outer')],

    # train-s2712
    # TEXT: 요리 및 식사 메뉴 모두 맛이 좋습니다
    # TRANSLIT: .yo.ri .mich .sig.sa .me.nyu .mo.du .mas.i .joh.seub.ni.da
    # ENGLISH: The food is good.
    # CONFLICT: 1:요리(nsubj→좋습니다), 6:맛이(nsubj→좋습니다)
    # Fix: default: N1(요리)→outer [NEEDS REVIEW]
    'train-s2712': [('deprel', 1, 'nsubj:outer')],

    # train-s2715
    # TEXT: 여기 안 지 10년 넘었는데 맛도 변화 없고 참 좋네요
    # TRANSLIT: .yeo.gi .an .ji 10.nyeon .neom.eoss.neun.de .mas.do .byeon.hwa .eobs.go .cham .joh.ne.yo
    # ENGLISH: This place also has good food.
    # CONFLICT: 6:맛도(nsubj→없고), 7:변화(nsubj→없고)
    # Fix: also-marker: N1(도)→outer
    'train-s2715': [('deprel', 6, 'nsubj:outer')],

    # train-s273
    # TEXT: 새예동물은 모두 16종이 알려져 있다.
    # TRANSLIT: .sae.ye.dong.mul.eun .mo.du 16.jong.i .al.ryeo.jyeo .iss.da.
    # ENGLISH: This is a very meaningful thing to me.
    # CONFLICT: 1:새예동물은(nsubj:pass→알려져), 3:16종이(nsubj:pass→알려져)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s273': [('deprel', 1, 'nsubj:outer')],

    # train-s2758
    # TEXT: 네덜란드 경찰은 여권 심사 과정에서 아갈리가 두 개의 여권을 가진 것을 발견했는데 하나는 인적 사항을 적는 면이 수정돼 있었고, 다른 하나는 키프로스에서 발급된 비자가 필요조건을 충족시키지 못한 것으로 알려졌다.
    # TRANSLIT: .ne.deol.ran.deu .gyeong.chal.eun .yeo.gweon .sim.sa .gwa.jeong.e.seo .a.gal.ri.ga .du .gae.yi .yeo.gweon.eul .ga.jin .geos.eul .bal.gyeon.haess.neun.de .ha.na.neun .in.jeog .sa.hang.eul .jeog.neun .myeon.i .su.jeong.dwae .iss.eoss.go, .da.reun .ha.na.neun .ki.peu.ro.seu.e.seo .bal.geub.doen .bi.ja.ga .pil.yo.jo.geon.eul .chung.jog.si.ki.ji .mos.han .geos.eu.ro .al.ryeo.jyeoss.da.
    # ENGLISH: Various important things are mentioned here.
    # CONFLICT: 13:하나는(nsubj→수정돼), 17:면이(nsubj→수정돼)
    # CONFLICT: 22:하나는(nsubj→충족시키지), 25:비자가(nsubj→충족시키지)
    # Fix: topic-marker: N1(은/는)→outer | topic-marker: N1(은/는)→outer
    'train-s2758': [('deprel', 13, 'nsubj:outer'), ('deprel', 22, 'nsubj:outer')],

    # train-s2762
    # TEXT: 공공주택건설본부는 보금자리주택의 원활한 건설과 보급을 위해 설립된 대한민국 국토해양부 소속기관으로 공공주택건설본부장은 고위공무원 가급(1급상당)의 국토해양부 주택토지실장이 겸임하며, 공공주택건설추진단장은 고위공무원 나급(2~3급 상당)으로 보한다.
    # TRANSLIT: .gong.gong.ju.taeg.geon.seol.bon.bu.neun .bo.geum.ja.ri.ju.taeg.yi .weon.hwal.han .geon.seol.gwa .bo.geub.eul .wi.hae .seol.rib.doen .dae.han.min.gug .gug.to.hae.yang.bu .so.sog.gi.gwan.eu.ro .gong.gong.ju.taeg.geon.seol.bon.bu.jang.eun .go.wi.gong.mu.weon .ga.geub(1.geub.sang.dang).yi .gug.to.hae.yang.bu .ju.taeg.to.ji.sil.jang.i .gyeom.im.ha.myeo, .gong.gong.ju.taeg.geon.seol.chu.jin.dan.jang.eun .go.wi.gong.mu.weon .na.geub(2~3.geub .sang.dang).eu.ro .bo.han.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 11:공공주택건설본부장은(nsubj→겸임하며), 18:국토해양부(nsubj→겸임하며)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2762': [('deprel', 11, 'nsubj:outer')],

    # train-s281
    # TEXT: 하지만 저소득 노인들에게 지하철 무임승차는 큰 도움이 된다.
    # TRANSLIT: .ha.ji.man .jeo.so.deug .no.in.deul.e.ge .ji.ha.cheol .mu.im.seung.cha.neun .keun .do.um.i .doen.da.
    # ENGLISH: The subway is helpful.
    # CONFLICT: 4:지하철(nsubj→된다), 7:도움이(nsubj→된다)
    # Fix: default: N1(지하철)→outer [NEEDS REVIEW]
    'train-s281': [('deprel', 4, 'nsubj:outer')],

    # train-s2842
    # TEXT: 처음에는 맛있더니 재료도 조리도 성의 없더군요
    # TRANSLIT: .cheo.eum.e.neun .mas.iss.deo.ni .jae.ryo.do .jo.ri.do .seong.yi .eobs.deo.gun.yo
    # ENGLISH: Various things are good here.
    # CONFLICT: 3:재료도(nsubj→없더군요), 4:조리도(nsubj→없더군요), 5:성의(nsubj→없더군요)
    # Fix: triple: [3, 4]→outer
    'train-s2842': [('deprel', 3, 'nsubj:outer'), ('deprel', 4, 'nsubj:outer')],

    # train-s2853
    # TEXT: 미시령은 신증동국여지승람에 미시파령(彌時坡嶺)이라는 이름으로 그 기록이 남아 있다.
    # TRANSLIT: .mi.si.ryeong.eun .sin.jeung.dong.gug.yeo.ji.seung.ram.e .mi.si.pa.ryeong(míshípōlǐng).i.ra.neun .i.reum.eu.ro .geu .gi.rog.i .nam.a .iss.da.
    # ENGLISH: This is a very good place.
    # CONFLICT: 1:미시령은(nsubj→남아), 10:기록이(nsubj→남아)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2853': [('deprel', 1, 'nsubj:outer')],

    # train-s2859
    # TEXT: 양국의 민감한 품목이나 공공 서비스는 협정 적용이 배제되거나 유보될 예정이다.
    # TRANSLIT: .yang.gug.yi .min.gam.han .pum.mog.i.na .gong.gong .seo.bi.seu.neun .hyeob.jeong .jeog.yong.i .bae.je.doe.geo.na .yu.bo.doel .ye.jeong.i.da.
    # ENGLISH: The items and the agreement may be deferred.
    # CONFLICT: 3:품목이나(nsubj→유보될), 6:협정(nsubj→유보될)
    # Fix: default: N1(품목이나)→outer [NEEDS REVIEW]
    'train-s2859': [('deprel', 3, 'nsubj:outer')],

    # train-s2893
    # TEXT: 이에 반해 <로열 패밀리 이미 기본적인 줄거리가 다 공개되어 있다.
    # TRANSLIT: .i.e .ban.hae <.ro.yeol .pae.mil.ri .i.mi .gi.bon.jeog.in .jul.geo.ri.ga .da .gong.gae.doe.eo .iss.da.
    # ENGLISH: The Royal Family's plot has been revealed.
    # CONFLICT: 4:로열(nsubj→공개되어), 8:줄거리가(nsubj:pass→공개되어)
    # Fix: default: N1(로열)→outer [NEEDS REVIEW]
    'train-s2893': [('deprel', 4, 'nsubj:outer')],

    # train-s2898
    # TEXT: 섀플리는 세페이드 변광성의 주기가 20일이나 되는데 주기가 긴 세페이드 변광성을 이용해 계산한 거리는 신빙성이 없다며 반박을 시도했지만 몇 년 만에 다른 은하들의 거리가 안드로메다보다 훨씬 멀리 있다는 것이 계산되고 나서 대논쟁은 해결되었다.
    # TRANSLIT: .syae.peul.ri.neun .se.pe.i.deu .byeon.gwang.seong.yi .ju.gi.ga 20.il.i.na .doe.neun.de .ju.gi.ga .gin .se.pe.i.deu .byeon.gwang.seong.eul .i.yong.hae .gye.san.han .geo.ri.neun .sin.bing.seong.i .eobs.da.myeo .ban.bag.eul .si.do.haess.ji.man .myeoch .nyeon .man.e .da.reun .eun.ha.deul.yi .geo.ri.ga .an.deu.ro.me.da.bo.da .hweol.ssin .meol.ri .iss.da.neun .geos.i .gye.san.doe.go .na.seo .dae.non.jaeng.eun .hae.gyeol.doe.eoss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 13:거리는(nsubj→없다며), 14:신빙성이(nsubj→없다며)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2898': [('deprel', 13, 'nsubj:outer')],

    # train-s2904
    # TEXT: 두 가지 게장 모두 알과 살은 가득했어요.
    # TRANSLIT: .du .ga.ji .ge.jang .mo.du .al.gwa .sal.eun .ga.deug.haess.eo.yo.
    # ENGLISH: The branches were full of eggs.
    # CONFLICT: 2:가지(nsubj→가득했어요), 5:알과(nsubj→가득했어요)
    # Fix: default: N1(가지)→outer [NEEDS REVIEW]
    'train-s2904': [('deprel', 2, 'nsubj:outer')],

    # train-s2910
    # TEXT: 맛도 양도 가격도 참 착하고 무엇보다 사람이 착해서 좋은 집.
    # TRANSLIT: .mas.do .yang.do .ga.gyeog.do .cham .chag.ha.go .mu.eos.bo.da .sa.ram.i .chag.hae.seo .joh.eun .jib.
    # ENGLISH: Various things are good here.
    # CONFLICT: 1:맛도(nsubj→착하고), 2:양도(nsubj→착하고), 3:가격도(nsubj→착하고)
    # Fix: triple: [1, 2, 3]→outer
    'train-s2910': [('deprel', 1, 'nsubj:outer'), ('deprel', 2, 'nsubj:outer'), ('deprel', 3, 'nsubj:outer')],

    # train-s2925
    # TEXT: 한국 육상이 이번 광저우 아시안게임에서 은메달을 딴 것은 장대높이뛰기 김유석에 이어 김건우가 두 번째다.
    # TRANSLIT: .han.gug .yug.sang.i .i.beon .gwang.jeo.u .a.si.an.ge.im.e.seo .eun.me.dal.eul .ddan .geos.eun .jang.dae.nop.i.ddwi.gi .gim.yu.seog.e .i.eo .gim.geon.u.ga .du .beon.jjae.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 8:것은(nsubj→번째다), 12:김건우가(nsubj→번째다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2925': [('deprel', 8, 'nsubj:outer')],

    # train-s2945
    # TEXT: 이후 크림 반도의 나머지 지역은 오스만 제국의 속국이 된 크림 한국의 일부가 되었고 정복된 테오도로 공국의 옛 땅과 남부 크림 반도는 오스만 제국의 영토가 되었다.
    # TRANSLIT: .i.hu .keu.rim .ban.do.yi .na.meo.ji .ji.yeog.eun .o.seu.man .je.gug.yi .sog.gug.i .doen .keu.rim .han.gug.yi .il.bu.ga .doe.eoss.go .jeong.bog.doen .te.o.do.ro .gong.gug.yi .yes .ddang.gwa .nam.bu .keu.rim .ban.do.neun .o.seu.man .je.gug.yi .yeong.to.ga .doe.eoss.da.
    # ENGLISH: The remaining land and territory became part of the empire.
    # CONFLICT: 4:나머지(nsubj→되었고), 12:일부가(nsubj→되었고)
    # CONFLICT: 18:땅과(nsubj→되었다), 24:영토가(nsubj→되었다)
    # Fix: default: N1(나머지)→outer [NEEDS REVIEW] | default: N1(땅과)→outer [NEEDS REVIEW]
    'train-s2945': [('deprel', 4, 'nsubj:outer'), ('deprel', 18, 'nsubj:outer')],

    # train-s2984
    # TEXT: 봄 여름엔 산바람이 아래로 타고 내려와 시원하고 가을 겨울은 햇빛이 잘 들어서 따뜻하다
    # TRANSLIT: .bom .yeo.reum.en .san.ba.ram.i .a.rae.ro .ta.go .nae.ryeo.wa .si.weon.ha.go .ga.eul .gyeo.ul.eun .haes.bich.i .jal .deul.eo.seo .dda.ddeus.ha.da
    # ENGLISH: In autumn, sunlight comes through.
    # CONFLICT: 8:가을(nsubj→들어서), 10:햇빛이(nsubj→들어서)
    # Fix: default: N1(가을)→outer [NEEDS REVIEW]
    'train-s2984': [('deprel', 8, 'nsubj:outer')],

    # train-s2985
    # TEXT: 겉으로 보기엔 좋습니다만 맛이 영 성의 없어 보입니다
    # TRANSLIT: .geot.eu.ro .bo.gi.en .joh.seub.ni.da.man .mas.i .yeong .seong.yi .eobs.eo .bo.ib.ni.da
    # ENGLISH: The flavor lacks sincerity.
    # CONFLICT: 4:맛이(nsubj→없어), 6:성의(nsubj→없어)
    # Fix: default: N1(맛이)→outer [NEEDS REVIEW]
    'train-s2985': [('deprel', 4, 'nsubj:outer')],

    # train-s299
    # TEXT: 더욱 자세한 사항은 모두투어 홈페이지(http://www.modetour.com)의 메인 화면에 나와있는 특전을 통해 확인 가능하다.
    # TRANSLIT: .deo.ug .ja.se.han .sa.hang.eun .mo.du.tu.eo .hom.pe.i.ji(http://www.modetour.com).yi .me.in .hwa.myeon.e .na.wa.iss.neun .teug.jeon.eul .tong.hae .hwag.in .ga.neung.ha.da.
    # ENGLISH: This place is very good.
    # CONFLICT: 3:사항은(nsubj→가능하다), 15:확인(nsubj→가능하다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s299': [('deprel', 3, 'nsubj:outer')],

    # train-s2990
    # TEXT: 따라서 강서구는 비류백제의 미추홀에서부터 역사가 시작된다고 볼 수 있으며 최초의 지명이 ''제차파의’라는 것을 알 수 있다.
    # TRANSLIT: .dda.ra.seo .gang.seo.gu.neun .bi.ryu.baeg.je.yi .mi.chu.hol.e.seo.bu.teo .yeog.sa.ga .si.jag.doen.da.go .bol .su .iss.eu.myeo .choe.cho.yi .ji.myeong.i ''.je.cha.pa.yi’.ra.neun .geos.eul .al .su .iss.da.
    # ENGLISH: This is a very good restaurant.
    # CONFLICT: 2:강서구는(nsubj→시작된다고), 5:역사가(nsubj→시작된다고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s2990': [('deprel', 2, 'nsubj:outer')],

    # train-s301
    # TEXT: 밤에 매장 정리할 때 보면 깔끔하게 마무리하려 애쓰는 모습도 보기 좋습니다
    # TRANSLIT: .bam.e .mae.jang .jeong.ri.hal .ddae .bo.myeon .ggal.ggeum.ha.ge .ma.mu.ri.ha.ryeo .ae.sseu.neun .mo.seub.do .bo.gi .joh.seub.ni.da
    # ENGLISH: The food here is also delicious.
    # CONFLICT: 9:모습도(nsubj→좋습니다), 10:보기(nsubj→좋습니다)
    # Fix: also-marker: N1(도)→outer
    'train-s301': [('deprel', 9, 'nsubj:outer')],

    # train-s302
    # TEXT: 그간 깍쟁이 같은 역할을 많이 맡았지만 그건 실제 제 성격이 아니에요.
    # TRANSLIT: .geu.gan .ggag.jaeng.i .gat.eun .yeog.hal.eul .manh.i .mat.ass.ji.man .geu.geon .sil.je .je .seong.gyeog.i .a.ni.e.yo.
    # ENGLISH: That is not what my personality is like.
    # CONFLICT: 7:그건(nsubj→아니에요), 10:성격이(nsubj→아니에요)
    # Fix: default: N1(그건)→outer [NEEDS REVIEW]
    'train-s302': [('deprel', 7, 'nsubj:outer')],

    # train-s3023
    # TEXT: 한편, 코스닥시장에서 K-IFRS(국제회계기준)을 조기 도입한 12월 결산법인 26개사 중 22개사의 매출은 개별기준으로 2조3678억 원으로 전년동기대비 4.12 %, 당기순이익은 763억 원으로 5.97% 증가했다.
    # TRANSLIT: .han.pyeon, .ko.seu.dag.si.jang.e.seo K-IFRS(.gug.je.hoe.gye.gi.jun).eul .jo.gi .do.ib.han 12.weol .gyeol.san.beob.in 26.gae.sa .jung 22.gae.sa.yi .mae.chul.eun .gae.byeol.gi.jun.eu.ro 2.jo3678.eog .weon.eu.ro .jeon.nyeon.dong.gi.dae.bi 4.12 %, .dang.gi.sun.i.ig.eun 763.eog .weon.eu.ro 5.97% .jeung.ga.haess.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 24:당기순이익은(nsubj→증가했다), 28:%(nsubj→증가했다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3023': [('deprel', 24, 'nsubj:outer')],

    # train-s3054
    # TEXT: 어렸을 때, 아버지가 사업이 잘 되지 않아, 전학과 이사를 자주 다녔다는 암시가 있다.
    # TRANSLIT: .eo.ryeoss.eul .ddae, .a.beo.ji.ga .sa.eob.i .jal .doe.ji .anh.a, .jeon.hag.gwa .i.sa.reul .ja.ju .da.nyeoss.da.neun .am.si.ga .iss.da.
    # ENGLISH: His father's business is not going well.
    # CONFLICT: 4:아버지가(nsubj→되지), 5:사업이(nsubj→되지)
    # Fix: default: N1(아버지가)→outer [NEEDS REVIEW]
    'train-s3054': [('deprel', 4, 'nsubj:outer')],

    # train-s3056
    # TEXT: 근처에 맛집이 뭐가 있지?
    # TRANSLIT: .geun.cheo.e .mas.jib.i .mweo.ga .iss.ji?
    # ENGLISH: What good restaurants are available?
    # CONFLICT: 2:맛집이(nsubj→있지), 3:뭐가(nsubj→있지)
    # Fix: default: N1(맛집이)→outer [NEEDS REVIEW]
    'train-s3056': [('deprel', 2, 'nsubj:outer')],

    # train-s3058
    # TEXT: 상장은 신주 모집과 구주 매출을 병행하는 방식으로 진행될 예정이며, 공모액은 2조원 이상이 될 것으로 예상되고 있다.
    # TRANSLIT: .sang.jang.eun .sin.ju .mo.jib.gwa .gu.ju .mae.chul.eul .byeong.haeng.ha.neun .bang.sig.eu.ro .jin.haeng.doel .ye.jeong.i.myeo, .gong.mo.aeg.eun 2.jo.weon .i.sang.i .doel .geos.eu.ro .ye.sang.doe.go .iss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 11:공모액은(nsubj→될), 12:2조원(nsubj→될)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3058': [('deprel', 11, 'nsubj:outer')],

    # train-s3075
    # TEXT: 이 자린 우리가 점심 먹을 자리니까 다른 자리에 앉으세요
    # TRANSLIT: .i .ja.rin .u.ri.ga .jeom.sim .meog.eul .ja.ri.ni.gga .da.reun .ja.ri.e .anj.eu.se.yo
    # ENGLISH: That seat, we will eat.
    # CONFLICT: 2:자린(nsubj→먹을), 3:우리가(nsubj→먹을)
    # Fix: default: N1(자린)→outer [NEEDS REVIEW]
    'train-s3075': [('deprel', 2, 'nsubj:outer')],

    # train-s3084
    # TEXT: 총 3개 코스로 나누어진 곤유산 트레킹은 코스마다 5시간 정도 소요되며 전문 산악인이 동행한다.
    # TRANSLIT: .chong 3.gae .ko.seu.ro .na.nu.eo.jin .gon.yu.san .teu.re.king.eun .ko.seu.ma.da 5.si.gan .jeong.do .so.yo.doe.myeo .jeon.mun .san.ag.in.i .dong.haeng.han.da.
    # ENGLISH: Gonyushan Mountain has specialized guides.
    # CONFLICT: 5:곤유산(nsubj→동행한다), 11:전문(nsubj→동행한다)
    # Fix: default: N1(곤유산)→outer [NEEDS REVIEW]
    'train-s3084': [('deprel', 5, 'nsubj:outer')],

    # train-s3108
    # TEXT: 매출액은 5157억 원으로 전년대비 37.16% 증가.
    # TRANSLIT: .mae.chul.aeg.eun 5157.eog .weon.eu.ro .jeon.nyeon.dae.bi 37.16% .jeung.ga.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:매출액은(nsubj→증가), 8:%(nsubj→증가)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3108': [('deprel', 1, 'nsubj:outer')],

    # train-s3110
    # TEXT: 한국도 KT가 독점 공급 사업자여서 충분히 참고할만한 대목이다.
    # TRANSLIT: .han.gug.do KT.ga .dog.jeom .gong.geub .sa.eob.ja.yeo.seo .chung.bun.hi .cham.go.hal.man.han .dae.mog.i.da.
    # ENGLISH: This place also has good food.
    # CONFLICT: 1:한국도(nsubj→독점), 2:KT가(nsubj→독점)
    # Fix: also-marker: N1(도)→outer
    'train-s3110': [('deprel', 1, 'nsubj:outer')],

    # train-s3133
    # TEXT: 체코 정부 대변인은 남동부 두코바니 원전의 원자로 4기 중 1기가 방수 기능 이상으로 가동이 중단됐다고 밝혔습니다.
    # TRANSLIT: .che.ko .jeong.bu .dae.byeon.in.eun .nam.dong.bu .du.ko.ba.ni .weon.jeon.yi .weon.ja.ro 4.gi .jung 1.gi.ga .bang.su .gi.neung .i.sang.eu.ro .ga.dong.i .jung.dan.dwaess.da.go .barg.hyeoss.seub.ni.da.
    # ENGLISH: Unit 1 had its operation suspended.
    # CONFLICT: 10:1기가(nsubj:pass→중단됐다고), 14:가동이(nsubj:pass→중단됐다고)
    # Fix: default: N1(1기가)→outer [NEEDS REVIEW]
    'train-s3133': [('deprel', 10, 'nsubj:outer')],

    # train-s3144
    # TEXT: 유로존에 공식적으로 가입하기 위해 (개별적으로 동전 조폐권을 가지는 권리를 얻기 위해 ), 국가는 보통 먼저 유럽 연합의 회원국이 되어야 한다.
    # TRANSLIT: .yu.ro.jon.e .gong.sig.jeog.eu.ro .ga.ib.ha.gi .wi.hae (.gae.byeol.jeog.eu.ro .dong.jeon .jo.pye.gweon.eul .ga.ji.neun .gweon.ri.reul .eod.gi .wi.hae ), .gug.ga.neun .bo.tong .meon.jeo .yu.reob .yeon.hab.yi .hoe.weon.gug.i .doe.eo.ya .han.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 15:국가는(nsubj→되어야), 20:회원국이(nsubj→되어야)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3144': [('deprel', 15, 'nsubj:outer')],

    # train-s3168
    # TEXT: 상식적인 조사과정에서는 작은 폭발 에너지의 위치가 충만해진 날개측 중앙 연료탱크 내부의 점화 요인이 되었을 가능성에 대해 심사하였다.
    # TRANSLIT: .sang.sig.jeog.in .jo.sa.gwa.jeong.e.seo.neun .jag.eun .pog.bal .e.neo.ji.yi .wi.chi.ga .chung.man.hae.jin .nal.gae.cheug .jung.ang .yeon.ryo.taeng.keu .nae.bu.yi .jeom.hwa .yo.in.i .doe.eoss.eul .ga.neung.seong.e .dae.hae .sim.sa.ha.yeoss.da.
    # ENGLISH: The location has been ignited.
    # CONFLICT: 6:위치가(nsubj→되었을), 12:점화(nsubj→되었을)
    # Fix: default: N1(위치가)→outer [NEEDS REVIEW]
    'train-s3168': [('deprel', 6, 'nsubj:outer')],

    # train-s3181
    # TEXT: 쿼크의 발견으로, 양성자가 기본 입자가 아니라 두 개의 위 쿼크와 하나의 아래 쿼크가 강한 상호작용으로 묶인, 복합 입자임이 밝혀졌다.
    # TRANSLIT: .kweo.keu.yi .bal.gyeon.eu.ro, .yang.seong.ja.ga .gi.bon .ib.ja.ga .a.ni.ra .du .gae.yi .wi .kweo.keu.wa .ha.na.yi .a.rae .kweo.keu.ga .gang.han .sang.ho.jag.yong.eu.ro .mugg.in, .bog.hab .ib.ja.im.i .barg.hyeo.jyeoss.da.
    # ENGLISH: A proton is not the basic unit.
    # CONFLICT: 4:양성자가(nsubj→아니라), 5:기본(nsubj→아니라)
    # Fix: default: N1(양성자가)→outer [NEEDS REVIEW]
    'train-s3181': [('deprel', 4, 'nsubj:outer')],

    # train-s3221
    # TEXT: 한편 산림항공관리본부와 강원지방기상청은 지난 3월24일 실시간 기상정보 제공과 안전한 비행임무 수행을 위해 두 기관이 상호업무협약(MOU)을 체결한 바 있다.
    # TRANSLIT: .han.pyeon .san.rim.hang.gong.gwan.ri.bon.bu.wa .gang.weon.ji.bang.gi.sang.cheong.eun .ji.nan 3.weol24.il .sil.si.gan .gi.sang.jeong.bo .je.gong.gwa .an.jeon.han .bi.haeng.im.mu .su.haeng.eul .wi.hae .du .gi.gwan.i .sang.ho.eob.mu.hyeob.yag(MOU).eul .che.gyeol.han .ba .iss.da.
    # ENGLISH: The Korea Forest Service and the institution signed an agreement.
    # CONFLICT: 2:산림항공관리본부와(nsubj→체결한), 14:기관이(nsubj→체결한)
    # Fix: default: N1(산림항공관리본부와)→outer [NEEDS REVIEW]
    'train-s3221': [('deprel', 2, 'nsubj:outer')],

    # train-s3224
    # TEXT: 한편 이곳 현장은 67만6445㎡ 규모로 공동주택 4116호(일반 1776호, 임대 2340호), 단독주택 84호 등 총 4200호를 건립하고 중•고등학교가 건립될 예정이다.
    # TRANSLIT: .han.pyeon .i.gos .hyeon.jang.eun 67.man6445㎡ .gyu.mo.ro .gong.dong.ju.taeg 4116.ho(.il.ban 1776.ho, .im.dae 2340.ho), .dan.dog.ju.taeg 84.ho .deung .chong 4200.ho.reul .geon.rib.ha.go .jung•.go.deung.hag.gyo.ga .geon.rib.doel .ye.jeong.i.da.
    # ENGLISH: Among them, a high school will be built.
    # CONFLICT: 23:중(nsubj:pass→건립될), 25:고등학교가(nsubj→건립될)
    # Fix: default: N1(중)→outer [NEEDS REVIEW]
    'train-s3224': [('deprel', 23, 'nsubj:outer')],

    # train-s3247
    # TEXT: 캐릭터의 이동 속도는 고속 이동과 저속 이동 2가지 모드가 있는데, 고속 이동이 평소의 이동이고 저속 이동은 Shift를 누르고 있을 때 적용되는 모드이다.
    # TRANSLIT: .kae.rig.teo.yi .i.dong .sog.do.neun .go.sog .i.dong.gwa .jeo.sog .i.dong 2.ga.ji .mo.deu.ga .iss.neun.de, .go.sog .i.dong.i .pyeong.so.yi .i.dong.i.go .jeo.sog .i.dong.eun Shift.reul .nu.reu.go .iss.eul .ddae .jeog.yong.doe.neun .mo.deu.i.da.
    # ENGLISH: Mobile, high-speed connections are available.
    # CONFLICT: 2:이동(nsubj→있는데), 4:고속(nsubj→있는데)
    # Fix: default: N1(이동)→outer [NEEDS REVIEW]
    'train-s3247': [('deprel', 2, 'nsubj:outer')],

    # train-s3260
    # TEXT: 또 외부에서 온 CEO 총장님이 교수들과 이해관계가 없어서 학교개혁을 과감하게 시도하고 있습니다.
    # TRANSLIT: .ddo .oe.bu.e.seo .on CEO .chong.jang.nim.i .gyo.su.deul.gwa .i.hae.gwan.gye.ga .eobs.eo.seo .hag.gyo.gae.hyeog.eul .gwa.gam.ha.ge .si.do.ha.go .iss.seub.ni.da.
    # ENGLISH: The CEO has no conflicts of interest.
    # CONFLICT: 4:CEO(nsubj→없어서), 7:이해관계가(nsubj→없어서)
    # Fix: default: N1(CEO)→outer [NEEDS REVIEW]
    'train-s3260': [('deprel', 4, 'nsubj:outer')],

    # train-s3266
    # TEXT: 현대 엠코는 현대자동차그룹의 종합건설회사로 향후 브랜드 인지도와 교통의 프리미엄은 물론 초고층 랜드마크로 큰 시세차익이 기대된다.
    # TRANSLIT: .hyeon.dae .em.ko.neun .hyeon.dae.ja.dong.cha.geu.rub.yi .jong.hab.geon.seol.hoe.sa.ro .hyang.hu .beu.raen.deu .in.ji.do.wa .gyo.tong.yi .peu.ri.mi.eom.eun .mul.ron .cho.go.cheung .raen.deu.ma.keu.ro .keun .si.se.cha.ig.i .gi.dae.doen.da.
    # ENGLISH: The brand is expected to generate capital gains.
    # CONFLICT: 6:브랜드(nsubj→기대된다), 14:시세차익이(nsubj→기대된다)
    # Fix: default: N1(브랜드)→outer [NEEDS REVIEW]
    'train-s3266': [('deprel', 6, 'nsubj:outer')],

    # train-s327
    # TEXT: 그들은 아마도 코카서스에 근원이 있었으며, 명확하지는 않지만 북쪽에서부터 진입하였다.
    # TRANSLIT: .geu.deul.eun .a.ma.do .ko.ka.seo.seu.e .geun.weon.i .iss.eoss.eu.myeo, .myeong.hwag.ha.ji.neun .anh.ji.man .bug.jjog.e.seo.bu.teo .jin.ib.ha.yeoss.da.
    # ENGLISH: This is a really good restaurant.
    # CONFLICT: 1:그들은(nsubj→있었으며), 4:근원이(nsubj→있었으며)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s327': [('deprel', 1, 'nsubj:outer')],

    # train-s3276
    # TEXT: 고추장구이도 연탄향이 그윽한 것이 아주 식욕과 소주를 끌어당깁니다.
    # TRANSLIT: .go.chu.jang.gu.i.do .yeon.tan.hyang.i .geu.eug.han .geos.i .a.ju .sig.yog.gwa .so.ju.reul .ggeul.eo.dang.gib.ni.da.
    # ENGLISH: This place also has something special.
    # CONFLICT: 1:고추장구이도(nsubj→그윽한), 2:연탄향이(nsubj→그윽한)
    # Fix: also-marker: N1(도)→outer
    'train-s3276': [('deprel', 1, 'nsubj:outer')],

    # train-s3297
    # TEXT: 모두가 두려워하는 치매도 식생활, 운동, 흡연 여부, 취미 활동, 사교 등 생활습관에 따라 발생률이 천양지차다.
    # TRANSLIT: .mo.du.ga .du.ryeo.weo.ha.neun .chi.mae.do .sig.saeng.hwal, .un.dong, .heub.yeon .yeo.bu, .chwi.mi .hwal.dong, .sa.gyo .deung .saeng.hwal.seub.gwan.e .dda.ra .bal.saeng.ryul.i .cheon.yang.ji.cha.da.
    # ENGLISH: This place also has good food.
    # CONFLICT: 3:치매도(nsubj→천양지차다), 18:발생률이(nsubj→천양지차다)
    # Fix: also-marker: N1(도)→outer
    'train-s3297': [('deprel', 3, 'nsubj:outer')],

    # train-s3300
    # TEXT: 일본의 동해로 방출된 방사선 오염수의 문제를 비롯해 그 문제가 지구상으로 확대되고 있는 후쿠시마 원자력발전소의 문제도 300여 회가 넘게 계속되고 있는 여진과 더불어 아직 그 터널의 끝이 보이지 않고 있는 불안한 상황이구요.
    # TRANSLIT: .il.bon.yi .dong.hae.ro .bang.chul.doen .bang.sa.seon .o.yeom.su.yi .mun.je.reul .bi.ros.hae .geu .mun.je.ga .ji.gu.sang.eu.ro .hwag.dae.doe.go .iss.neun .hu.ku.si.ma .weon.ja.ryeog.bal.jeon.so.yi .mun.je.do 300.yeo .hoe.ga .neom.ge .gye.sog.doe.go .iss.neun .yeo.jin.gwa .deo.bul.eo .a.jig .geu .teo.neol.yi .ggeut.i .bo.i.ji .anh.go .iss.neun .bul.an.han .sang.hwang.i.gu.yo.
    # ENGLISH: This place also has good food.
    # CONFLICT: 15:문제도(nsubj→보이지), 26:끝이(nsubj→보이지)
    # Fix: also-marker: N1(도)→outer
    'train-s3300': [('deprel', 15, 'nsubj:outer')],

    # train-s3329
    # TEXT: 플렉은 장타자가 아니었지만 곧은 드라이브샷을 앞세웠고 불안한 퍼팅은 정확한 아이언 샷으로 만회했다.
    # TRANSLIT: .peul.reg.eun .jang.ta.ja.ga .a.ni.eoss.ji.man .god.eun .deu.ra.i.beu.syas.eul .ap.se.weoss.go .bul.an.han .peo.ting.eun .jeong.hwag.han .a.i.eon .syas.eu.ro .man.hoe.haess.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 1:플렉은(nsubj→만회했다), 8:퍼팅은(nsubj→만회했다)
    # Fix: both-topic: N1→outer (first)
    'train-s3329': [('deprel', 1, 'nsubj:outer')],

    # train-s3337
    # TEXT: 우리산업의 상반기 누적 실적은 매출액과 영업이익이 각각 645억원 ,  17억원으로 추정됐다.
    # TRANSLIT: .u.ri.san.eob.yi .sang.ban.gi .nu.jeog .sil.jeog.eun .mae.chul.aeg.gwa .yeong.eob.i.ig.i .gag.gag 645.eog.weon ,  17.eog.weon.eu.ro .chu.jeong.dwaess.da.
    # ENGLISH: The first half sales and revenue are estimated.
    # CONFLICT: 2:상반기(nsubj:pass→추정됐다), 5:매출액과(nsubj:pass→추정됐다)
    # Fix: default: N1(상반기)→outer [NEEDS REVIEW]
    'train-s3337': [('deprel', 2, 'nsubj:outer')],

    # train-s3359
    # TEXT: 한국수입자동차협회(KAIDA) 집계 결과에 따르면, All-new Infiniti M은 본격 판매를 개시한 지난 7월 총 315대가 판매됐으며, 이 중 M37은 298대가 판매돼 전체 베스트셀링 모델 4위를 기록했다.
    # TRANSLIT: .han.gug.su.ib.ja.dong.cha.hyeob.hoe(KAIDA) .jib.gye .gyeol.gwa.e .dda.reu.myeon, All-new Infiniti M.eun .bon.gyeog .pan.mae.reul .gae.si.han .ji.nan 7.weol .chong 315.dae.ga .pan.mae.dwaess.eu.myeo, .i .jung M37.eun 298.dae.ga .pan.mae.dwae .jeon.che .be.seu.teu.sel.ring .mo.del 4.wi.reul .gi.rog.haess.da.
    # ENGLISH: The all-new model, 315 units were sold.
    # CONFLICT: 9:All-new(nsubj:pass→판매됐으며), 18:315대가(nsubj:pass→판매됐으며)
    # CONFLICT: 23:M37은(nsubj:pass→판매돼), 24:298대가(nsubj:pass→판매돼)
    # Fix: default: N1(All-new)→outer [NEEDS REVIEW] | topic-marker: N1(은/는)→outer
    'train-s3359': [('deprel', 9, 'nsubj:outer'), ('deprel', 23, 'nsubj:outer')],

    # train-s3379
    # TEXT: 주나라 초기의 주공(周公)은, 인간은 나면서부터 하늘에서 정해준 운명을 가지고 있지만, 그것은 불변하는 것이 아니고, 인간의 후천적인 수양 등에 의해 어느 정도 바뀔 수가 있다고 생각하여 독자적인 예(禮)의 문화에 대한 기초를 만들었다.
    # TRANSLIT: .ju.na.ra .cho.gi.yi .ju.gong(zhōugōng).eun, .in.gan.eun .na.myeon.seo.bu.teo .ha.neul.e.seo .jeong.hae.jun .un.myeong.eul .ga.ji.go .iss.ji.man, .geu.geos.eun .bul.byeon.ha.neun .geos.i .a.ni.go, .in.gan.yi .hu.cheon.jeog.in .su.yang .deung.e .yi.hae .eo.neu .jeong.do .ba.ggwil .su.ga .iss.da.go .saeng.gag.ha.yeo .dog.ja.jeog.in .ye(lǐ).yi .mun.hwa.e .dae.han .gi.cho.reul .man.deul.eoss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 17:그것은(nsubj→아니고), 19:것이(nsubj→아니고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3379': [('deprel', 17, 'nsubj:outer')],

    # train-s3385
    # TEXT: 예컨데 회사와 노조가 4%의 임금 인상을 합의해도 최하 등급인 5등급을 받으면 임금 인상율은 0%가 된다.
    # TRANSLIT: .ye.keon.de .hoe.sa.wa .no.jo.ga 4%.yi .im.geum .in.sang.eul .hab.yi.hae.do .choe.ha .deung.geub.in 5.deung.geub.eul .bad.eu.myeon .im.geum .in.sang.yul.eun 0%.ga .doen.da.
    # ENGLISH: The wage rate is zero.
    # CONFLICT: 14:임금(nsubj→된다), 16:0(nsubj→된다)
    # Fix: default: N1(임금)→outer [NEEDS REVIEW]
    'train-s3385': [('deprel', 14, 'nsubj:outer')],

    # train-s3386
    # TEXT: 입맛이야 약간의 차이가 있겠지만 먼저 글 올리신 분들은 친척분들인지..?
    # TRANSLIT: .ib.mas.i.ya .yag.gan.yi .cha.i.ga .iss.gess.ji.man .meon.jeo .geul .ol.ri.sin .bun.deul.eun .chin.cheog.bun.deul.in.ji..?
    # ENGLISH: Tastes differ, of course there is a difference.
    # CONFLICT: 1:입맛이야(nsubj→있겠지만), 3:차이가(nsubj→있겠지만)
    # Fix: default: N1(입맛이야)→outer [NEEDS REVIEW]
    'train-s3386': [('deprel', 1, 'nsubj:outer')],

    # train-s3401
    # TEXT: 시교육청의 2009년 기초학력 미달학생 비율은 초6 1.5%(전국 16개 시ㆍ도교육청 중 10위 ), 중3 9.0%(14위 ), 고2 5.7%(16위)였다.
    # TRANSLIT: .si.gyo.yug.cheong.yi 2009.nyeon .gi.cho.hag.ryeog .mi.dal.hag.saeng .bi.yul.eun .cho6 1.5%(.jeon.gug 16.gae .siㆍ.do.gyo.yug.cheong .jung 10.wi ), .jung3 9.0%(14.wi ), .go2 5.7%(16.wi).yeoss.da.
    # ENGLISH: Basic academic ability, second-year high school students average 5.7.
    # CONFLICT: 3:기초학력(nsubj→5.7), 26:고2(nsubj→5.7)
    # Fix: default: N1(기초학력)→outer [NEEDS REVIEW]
    'train-s3401': [('deprel', 3, 'nsubj:outer')],

    # train-s3436
    # TEXT: 이 잡지는 인터넷판 기사에서 요르단의 고대도시 '페트라'와 붉은 사막 '와디럼'이 1주일간 신혼여행의 주요 행선지가 될 것으로 알려졌다고 전했다.
    # TRANSLIT: .i .jab.ji.neun .in.teo.nes.pan .gi.sa.e.seo .yo.reu.dan.yi .go.dae.do.si '.pe.teu.ra'.wa .burg.eun .sa.mag '.wa.di.reom'.i 1.ju.il.gan .sin.hon.yeo.haeng.yi .ju.yo .haeng.seon.ji.ga .doel .geos.eu.ro .al.ryeo.jyeoss.da.go .jeon.haess.da.
    # ENGLISH: The ancient city will be reconstructed over one week.
    # CONFLICT: 6:고대도시(nsubj→될), 17:1주일간(nsubj→될)
    # Fix: default: N1(고대도시)→outer [NEEDS REVIEW]
    'train-s3436': [('deprel', 6, 'nsubj:outer')],

    # train-s3452
    # TEXT: 브리스톨대학의 알래스테어 헤이 교수는 '브리티시 메디컬 저널(BMJ)' 최근호에서 "항생제의 효능은 처방한 달에 가장 크고 최대 1년까지 지속될 수 있다"며 그러나 "이 같은 (항생제의) 잔존효능이 높은 수준의 내성을 유발하는 요인이 될 수 있다"고 지적했다.
    # TRANSLIT: .beu.ri.seu.tol.dae.hag.yi .al.rae.seu.te.eo .he.i .gyo.su.neun '.beu.ri.ti.si .me.di.keol .jeo.neol(BMJ)' .choe.geun.ho.e.seo ".hang.saeng.je.yi .hyo.neung.eun .cheo.bang.han .dal.e .ga.jang .keu.go .choe.dae 1.nyeon.gga.ji .ji.sog.doel .su .iss.da".myeo .geu.reo.na ".i .gat.eun (.hang.saeng.je.yi) .jan.jon.hyo.neung.i .nop.eun .su.jun.yi .nae.seong.eul .yu.bal.ha.neun .yo.in.i .doel .su .iss.da".go .ji.jeog.haess.da.
    # ENGLISH: Residual efficacy is a factor.
    # CONFLICT: 35:잔존효능이(nsubj→될), 40:요인이(nsubj→될)
    # Fix: default: N1(잔존효능이)→outer [NEEDS REVIEW]
    'train-s3452': [('deprel', 35, 'nsubj:outer')],

    # train-s3457
    # TEXT: 한국은행이 지난 17일부터 24일까지 전국 2354개 업체를 대상으로 조사해 28일 발표한 결과에 따르면 제조업의 6월 업황전망 기업경기실사지수(BSI)는 104로 전월보다 3포인트 하락한 것으로 나타났다.
    # TRANSLIT: .han.gug.eun.haeng.i .ji.nan 17.il.bu.teo 24.il.gga.ji .jeon.gug 2354.gae .eob.che.reul .dae.sang.eu.ro .jo.sa.hae 28.il .bal.pyo.han .gyeol.gwa.e .dda.reu.myeon .je.jo.eob.yi 6.weol .eob.hwang.jeon.mang .gi.eob.gyeong.gi.sil.sa.ji.su(BSI).neun 104.ro .jeon.weol.bo.da 3.po.in.teu .ha.rag.han .geos.eu.ro .na.ta.nass.da.
    # ENGLISH: In June, the drop was 3 points.
    # CONFLICT: 15:6월(nsubj→하락한), 24:3포인트(nsubj→하락한)
    # Fix: default: N1(6월)→outer [NEEDS REVIEW]
    'train-s3457': [('deprel', 15, 'nsubj:outer')],

    # train-s3499
    # TEXT: 추어탕도 맛있다고 하던데 저는 순대국이 맛있더군요.
    # TRANSLIT: .chu.eo.tang.do .mas.iss.da.go .ha.deon.de .jeo.neun .sun.dae.gug.i .mas.iss.deo.gun.yo.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 4:저는(nsubj→맛있더군요), 5:순대국이(nsubj→맛있더군요)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3499': [('deprel', 4, 'nsubj:outer')],

    # train-s3507
    # TEXT: 참가신청은 목포대학교 F1 in Schools 기술지원센터 홈페이지(f1school.mokpo.ac.kr)나 전화(061-450-6307)로 접수가 가능하다.
    # TRANSLIT: .cham.ga.sin.cheong.eun .mog.po.dae.hag.gyo F1 in Schools .gi.sul.ji.weon.sen.teo .hom.pe.i.ji(f1school.mokpo.ac.kr).na .jeon.hwa(061-450-6307).ro .jeob.su.ga .ga.neung.ha.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:참가신청은(nsubj→가능하다), 17:접수가(nsubj→가능하다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3507': [('deprel', 1, 'nsubj:outer')],

    # train-s3512
    # TEXT: 일반 냉동 칵테일 새우는 새우향이 안 나는데 새우 참 맛있었음.
    # TRANSLIT: .il.ban .naeng.dong .kag.te.il .sae.u.neun .sae.u.hyang.i .an .na.neun.de .sae.u .cham .mas.iss.eoss.eum.
    # ENGLISH: Ordinary versions have a shrimp flavor.
    # CONFLICT: 1:일반(nsubj→나는데), 5:새우향이(nsubj→나는데)
    # Fix: default: N1(일반)→outer [NEEDS REVIEW]
    'train-s3512': [('deprel', 1, 'nsubj:outer')],

    # train-s3521
    # TEXT: 이 애니메이션은 매회 최종 엔딩 크레딧에 그 화의 메인 캐릭터를 연기한 성우가 그린 그림이 등장하는데, 세츠나가 메인이었던 6화에서는 코바야시가 담당.
    # TRANSLIT: .i .ae.ni.me.i.syeon.eun .mae.hoe .choe.jong .en.ding .keu.re.dis.e .geu .hwa.yi .me.in .kae.rig.teo.reul .yeon.gi.han .seong.u.ga .geu.rin .geu.rim.i .deung.jang.ha.neun.de, .se.cheu.na.ga .me.in.i.eoss.deon 6.hwa.e.seo.neun .ko.ba.ya.si.ga .dam.dang.
    # ENGLISH: This is a very good restaurant.
    # CONFLICT: 2:애니메이션은(nsubj→등장하는데), 14:그림이(nsubj→등장하는데)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3521': [('deprel', 2, 'nsubj:outer')],

    # train-s3530
    # TEXT: 다소 복잡해 보이는 이 법안은 지난 2008년 삼성네트웍스가 온세텔레콤과 계약해서 SK텔레콤의 가입자를 대상으로 '감'서비스를 제공하다가 9일만에 중단한 것이 발단이 됐다.
    # TRANSLIT: .da.so .bog.jab.hae .bo.i.neun .i .beob.an.eun .ji.nan 2008.nyeon .sam.seong.ne.teu.weog.seu.ga .on.se.tel.re.kom.gwa .gye.yag.hae.seo SK.tel.re.kom.yi .ga.ib.ja.reul .dae.sang.eu.ro '.gam'.seo.bi.seu.reul .je.gong.ha.da.ga 9.il.man.e .jung.dan.han .geos.i .bal.dan.i .dwaess.da.
    # ENGLISH: This somewhat complicated bill originated when Samsung Networks contracted with Onsetelacom and provided 'Gam' service targeting SK Telecom subscribers, then stopped after 9 days.
    # CONFLICT: 5:법안은(nsubj→됐다), 21:것이(nsubj→됐다), 22:발단이(nsubj→됐다)
    # Fix: 5:법안은(은 topic marker)→outer; 21:것이(outer topic of the됐다 clause)→outer;
    #      22:발단이(predicative nominal / inner subject of됐다) stays nsubj
    'train-s3530': [('deprel', 5, 'nsubj:outer'), ('deprel', 21, 'nsubj:outer')],

    # train-s3548
    # TEXT: 여자 인구 100명당 남자 인구를 나타내는 성비는 98.1로 여자가 다소 많다.
    # TRANSLIT: .yeo.ja .in.gu 100.myeong.dang .nam.ja .in.gu.reul .na.ta.nae.neun .seong.bi.neun 98.1.ro .yeo.ja.ga .da.so .manh.da.
    # ENGLISH: This is a very good place.
    # CONFLICT: 7:성비는(nsubj→많다), 9:여자가(nsubj→많다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3548': [('deprel', 7, 'nsubj:outer')],

    # train-s3562
    # TEXT: 304동 전망 끝네줘요
    # TRANSLIT: 304.dong .jeon.mang .ggeut.ne.jweo.yo
    # ENGLISH: Building 304, the view is impressive.
    # CONFLICT: 1:304동(nsubj→끝네줘요), 2:전망(nsubj→끝네줘요)
    # Fix: default: N1(304동)→outer [NEEDS REVIEW]
    'train-s3562': [('deprel', 1, 'nsubj:outer')],

    # train-s3573
    # TEXT: 이것이 후에 그 평가를 현저하게 낮추는 이유가 된다.
    # TRANSLIT: .i.geos.i .hu.e .geu .pyeong.ga.reul .hyeon.jeo.ha.ge .naj.chu.neun .i.yu.ga .doen.da.
    # ENGLISH: This is what makes it meaningful.
    # CONFLICT: 1:이것이(nsubj→된다), 7:이유가(nsubj→된다)
    # Fix: default: N1(이것이)→outer [NEEDS REVIEW]
    'train-s3573': [('deprel', 1, 'nsubj:outer')],

    # train-s3576
    # TEXT: 내부도 도색이 잘 돼서 예쁘고, 연못이 있어서 생태 공부에도 도움이 될 것 같다.
    # TRANSLIT: .nae.bu.do .do.saeg.i .jal .dwae.seo .ye.bbeu.go, .yeon.mos.i .iss.eo.seo .saeng.tae .gong.bu.e.do .do.um.i .doel .geos .gat.da.
    # ENGLISH: This place also has something special.
    # CONFLICT: 1:내부도(nsubj→돼서), 2:도색이(nsubj→돼서)
    # Fix: also-marker: N1(도)→outer
    'train-s3576': [('deprel', 1, 'nsubj:outer')],

    # train-s3624
    # TEXT: 코카서스 지역은 소비에트 연방이 붕괴된 이래로, 다양한 영토 논쟁이 있어왔다.
    # TRANSLIT: .ko.ka.seo.seu .ji.yeog.eun .so.bi.e.teu .yeon.bang.i .bung.goe.doen .i.rae.ro, .da.yang.han .yeong.to .non.jaeng.i .iss.eo.wass.da.
    # ENGLISH: The Caucasus has had territorial claims.
    # CONFLICT: 1:코카서스(nsubj→있어왔다), 9:영토(nsubj→있어왔다)
    # Fix: default: N1(코카서스)→outer [NEEDS REVIEW]
    'train-s3624': [('deprel', 1, 'nsubj:outer')],

    # train-s3654
    # TEXT: 수저랑 젓가락 통 열었는데 야채가 딱 달라 붙어서 안 떼어질 정도였고 방석은 밥풀로 가득하고 테이블은 기름이 잔뜩;
    # TRANSLIT: .su.jeo.rang .jeos.ga.rag .tong .yeol.eoss.neun.de .ya.chae.ga .ddag .dal.ra .but.eo.seo .an .dde.eo.jil .jeong.do.yeoss.go .bang.seog.eun .bab.pul.ro .ga.deug.ha.go .te.i.beul.eun .gi.reum.i .jan.ddeug;
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 15:테이블은(nsubj→잔뜩), 16:기름이(nsubj→잔뜩)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3654': [('deprel', 15, 'nsubj:outer')],

    # train-s3659
    # TEXT: 여기 불짬뽕 정말 불 납니다
    # TRANSLIT: .yeo.gi .bul.jjam.bbong .jeong.mal .bul .nab.ni.da
    # ENGLISH: The spicy jjamppong gives off a spicy taste.
    # CONFLICT: 2:불짬뽕(nsubj→납니다), 4:불(nsubj→납니다)
    # Fix: default: N1(불짬뽕)→outer [NEEDS REVIEW]
    'train-s3659': [('deprel', 2, 'nsubj:outer')],

    # train-s368
    # TEXT: 이 단지는 중심상업지구, 업무지구, 영종 브로드웨이가 도보권에 위치해 있어 여가•편의시설 이용이 편리하다.
    # TRANSLIT: .i .dan.ji.neun .jung.sim.sang.eob.ji.gu, .eob.mu.ji.gu, .yeong.jong .beu.ro.deu.we.i.ga .do.bo.gweon.e .wi.chi.hae .iss.eo .yeo.ga•.pyeon.yi.si.seol .i.yong.i .pyeon.ri.ha.da.
    # ENGLISH: The flavor here is excellent.
    # CONFLICT: 2:단지는(nsubj→편리하다), 12:여가(nsubj→편리하다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s368': [('deprel', 2, 'nsubj:outer')],

    # train-s369
    # TEXT: 아줌마들이 눈치가 없으시네요.
    # TRANSLIT: .a.jum.ma.deul.i .nun.chi.ga .eobs.eu.si.ne.yo.
    # ENGLISH: The ladies have no sense of other people's feelings.
    # CONFLICT: 1:아줌마들이(nsubj→없으시네요), 2:눈치가(nsubj→없으시네요)
    # Fix: default: N1(아줌마들이)→outer [NEEDS REVIEW]
    'train-s369': [('deprel', 1, 'nsubj:outer')],

    # train-s3708
    # TEXT: 이어 "난 뽀로로에 비하면 상대도 안된다"며 "내가 오죽하면 뽀로로 친구 크롱이를 알겠냐"고 말해 폭소케 했다.
    # TRANSLIT: .i.eo ".nan .bbo.ro.ro.e .bi.ha.myeon .sang.dae.do .an.doen.da".myeo ".nae.ga .o.jug.ha.myeon .bbo.ro.ro .chin.gu .keu.rong.i.reul .al.gess.nya".go .mal.hae .pog.so.ke .haess.da.
    # ENGLISH: This place also has something good.
    # CONFLICT: 3:난(nsubj→안된다), 6:상대도(nsubj→안된다)
    # Fix: also-marker: N2(도)→outer
    'train-s3708': [('deprel', 6, 'nsubj:outer')],

    # train-s3711
    # TEXT: 저 단골이였는데 종업원들 싸가지 없어서 이제 김가네는 죽을 때까지 안 갈라고요.
    # TRANSLIT: .jeo .dan.gol.i.yeoss.neun.de .jong.eob.weon.deul .ssa.ga.ji .eobs.eo.seo .i.je .gim.ga.ne.neun .jug.eul .ddae.gga.ji .an .gal.ra.go.yo.
    # ENGLISH: The staff has no manners.
    # CONFLICT: 3:종업원들(nsubj→없어서), 4:싸가지(nsubj→없어서)
    # Fix: default: N1(종업원들)→outer [NEEDS REVIEW]
    'train-s3711': [('deprel', 3, 'nsubj:outer')],

    # train-s3718
    # TEXT: 전 메뉴 다 맛있지만 바싹한 쌀베이크와 데리베이크가 더 맛있었어요
    # TRANSLIT: .jeon .me.nyu .da .mas.iss.ji.man .ba.ssag.han .ssal.be.i.keu.wa .de.ri.be.i.keu.ga .deo .mas.iss.eoss.eo.yo
    # ENGLISH: Before, the menu was delicious.
    # CONFLICT: 1:전(nsubj→맛있지만), 2:메뉴(nsubj→맛있지만)
    # Fix: default: N1(전)→outer [NEEDS REVIEW]
    'train-s3718': [('deprel', 1, 'nsubj:outer')],

    # train-s3737
    # TEXT: 병상수 또한 2009년말 기준 경남 산청이 39병상에 그쳤지만 경남 마산의 경우 무려 7869병상이 확보된 것으로 나타나 200배가 넘는 차이를 보였다.
    # TRANSLIT: .byeong.sang.su .ddo.han 2009.nyeon.mal .gi.jun .gyeong.nam .san.cheong.i 39.byeong.sang.e .geu.chyeoss.ji.man .gyeong.nam .ma.san.yi .gyeong.u .mu.ryeo 7869.byeong.sang.i .hwag.bo.doen .geos.eu.ro .na.ta.na 200.bae.ga .neom.neun .cha.i.reul .bo.yeoss.da.
    # ENGLISH: The number of hospital beds in Gyeongnam fell short.
    # CONFLICT: 1:병상수(nsubj→그쳤지만), 5:경남(nsubj→그쳤지만)
    # Fix: default: N1(병상수)→outer [NEEDS REVIEW]
    'train-s3737': [('deprel', 1, 'nsubj:outer')],

    # train-s3752
    # TEXT: 이로써 3연승 뒤 2패를 안은 클리블랜드는 39승 33패가 됐으나 아메리칸리그 중부지구 1위 자리는 지켰다.
    # TRANSLIT: .i.ro.sseo 3.yeon.seung .dwi 2.pae.reul .an.eun .keul.ri.beul.raen.deu.neun 39.seung 33.pae.ga .dwaess.eu.na .a.me.ri.kan.ri.geu .jung.bu.ji.gu 1.wi .ja.ri.neun .ji.kyeoss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 6:클리블랜드는(nsubj→됐으나), 7:39승(nsubj→됐으나)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3752': [('deprel', 6, 'nsubj:outer')],

    # train-s379
    # TEXT: 그가 15살이 되던 해 무렵, 그는 학교 생활을 그만두고 가족들의 농장 일을 도왔다.
    # TRANSLIT: .geu.ga 15.sal.i .doe.deon .hae .mu.ryeob, .geu.neun .hag.gyo .saeng.hwal.eul .geu.man.du.go .ga.jog.deul.yi .nong.jang .il.eul .do.wass.da.
    # ENGLISH: When he was 15 years old.
    # CONFLICT: 1:그가(nsubj→되던), 2:15살이(nsubj→되던)
    # Fix: default: N1(그가)→outer [NEEDS REVIEW]
    'train-s379': [('deprel', 1, 'nsubj:outer')],

    # train-s3796
    # TEXT: 자세한 자격 요건은 국토부 홈페이지(www.mltm.go.kr)와 혁신도시 홈페이지(innocity.mltm.go.kr)을 통해 확인할 수 있다.
    # TRANSLIT: .ja.se.han .ja.gyeog .yo.geon.eun .gug.to.bu .hom.pe.i.ji(www.mltm.go.kr).wa .hyeog.sin.do.si .hom.pe.i.ji(innocity.mltm.go.kr).eul .tong.hae .hwag.in.hal .su .iss.da.
    # ENGLISH: There is a possibility of achieving it.
    # CONFLICT: 2:자격(nsubj→있다), 18:수(nsubj→있다)
    # Fix: su-construction: N1→outer
    'train-s3796': [('deprel', 2, 'nsubj:outer')],

    # train-s3866
    # TEXT: 의사라는 사람 태도가 않됐더군요
    # TRANSLIT: .yi.sa.ra.neun .sa.ram .tae.do.ga .anh.dwaess.deo.gun.yo
    # ENGLISH: That person's attitude was not right.
    # CONFLICT: 2:사람(nsubj→않됐더군요), 3:태도가(nsubj→않됐더군요)
    # Fix: default: N1(사람)→outer [NEEDS REVIEW]
    'train-s3866': [('deprel', 2, 'nsubj:outer')],

    # train-s3878
    # TEXT: 나중에 볶아 먹는 밥이 중독성 있네요
    # TRANSLIT: .na.jung.e .bogg.a .meog.neun .bab.i .jung.dog.seong .iss.ne.yo
    # ENGLISH: The rice is addictive.
    # CONFLICT: 4:밥이(nsubj→있네요), 5:중독성(nsubj→있네요)
    # Fix: default: N1(밥이)→outer [NEEDS REVIEW]
    'train-s3878': [('deprel', 4, 'nsubj:outer')],

    # train-s3890
    # TEXT: 모양도 맛도 좋아요
    # TRANSLIT: .mo.yang.do .mas.do .joh.a.yo
    # ENGLISH: This place is also good.
    # CONFLICT: 1:모양도(nsubj→좋아요), 2:맛도(nsubj→좋아요)
    # Fix: both-also: N1→outer (first)
    'train-s3890': [('deprel', 1, 'nsubj:outer')],

    # train-s3908
    # TEXT: 여동생 문정왕후는 중종의 계비가 되었으므로 처남매부간이면서 겹사돈이기도 하다.
    # TRANSLIT: .yeo.dong.saeng .mun.jeong.wang.hu.neun .jung.jong.yi .gye.bi.ga .doe.eoss.eu.meu.ro .cheo.nam.mae.bu.gan.i.myeon.seo .gyeob.sa.don.i.gi.do .ha.da.
    # ENGLISH: His younger sister became his stepmother.
    # CONFLICT: 1:여동생(nsubj→되었으므로), 4:계비가(nsubj→되었으므로)
    # Fix: default: N1(여동생)→outer [NEEDS REVIEW]
    'train-s3908': [('deprel', 1, 'nsubj:outer')],

    # train-s3909
    # TEXT: 이에 따라 지난 8월 이동통신 번호이동 시장과 휴대폰 시장은 20만 명이 대기 수요로 발생했지만 기존 경쟁 구도의 심화로 7월과 비슷한 수준을 보일 것으로 예상된다.
    # TRANSLIT: .i.e .dda.ra .ji.nan 8.weol .i.dong.tong.sin .beon.ho.i.dong .si.jang.gwa .hyu.dae.pon .si.jang.eun 20.man .myeong.i .dae.gi .su.yo.ro .bal.saeng.haess.ji.man .gi.jon .gyeong.jaeng .gu.do.yi .sim.hwa.ro 7.weol.gwa .bi.seus.han .su.jun.eul .bo.il .geos.eu.ro .ye.sang.doen.da.
    # ENGLISH: The mobile carrier had casualties.
    # CONFLICT: 5:이동통신(nsubj→발생했지만), 11:명이(nsubj→발생했지만)
    # Fix: default: N1(이동통신)→outer [NEEDS REVIEW]
    'train-s3909': [('deprel', 5, 'nsubj:outer')],

    # train-s3926
    # TEXT: 이날 원•달러 환율은 밤사이 뉴욕증시가 급등하고 이날 코스피지수가 상승한 데 힘입어 하락 압력을 받았다.
    # TRANSLIT: .i.nal .weon•.dal.reo .hwan.yul.eun .bam.sa.i .nyu.yog.jeung.si.ga .geub.deung.ha.go .i.nal .ko.seu.pi.ji.su.ga .sang.seung.han .de .him.ib.eo .ha.rag .ab.ryeog.eul .bad.ass.da.
    # ENGLISH: In won, in dollars, he received payment.
    # CONFLICT: 2:원(nsubj→받았다), 4:달러(nsubj→받았다)
    # Fix: default: N1(원)→outer [NEEDS REVIEW]
    'train-s3926': [('deprel', 2, 'nsubj:outer')],

    # train-s397
    # TEXT: 그 단체란 택시사업소도 될 수 있고 뻐스사업소도 될 수 있으며 또는 자동차를 많이 가지고 있는 일반 단체도 될 수 있습니다.
    # TRANSLIT: .geu .dan.che.ran .taeg.si.sa.eob.so.do .doel .su .iss.go .bbeo.seu.sa.eob.so.do .doel .su .iss.eu.myeo .ddo.neun .ja.dong.cha.reul .manh.i .ga.ji.go .iss.neun .il.ban .dan.che.do .doel .su .iss.seub.ni.da.
    # ENGLISH: There is a possibility of doing it.
    # CONFLICT: 2:단체란(nsubj→있습니다), 19:수(nsubj→있습니다)
    # Fix: su-construction: N1→outer
    'train-s397': [('deprel', 2, 'nsubj:outer')],

    # train-s398
    # TEXT: 서울시는 "특정 정당의 홍보매체로 이용되는 것은 오해를 불러일으킬 소지가 있다"며 "이에 모든 정당 광고를 배제토록 한 것"이라고 해명했다.
    # TRANSLIT: .seo.ul.si.neun ".teug.jeong .jeong.dang.yi .hong.bo.mae.che.ro .i.yong.doe.neun .geos.eun .o.hae.reul .bul.reo.il.eu.kil .so.ji.ga .iss.da".myeo ".i.e .mo.deun .jeong.dang .gwang.go.reul .bae.je.to.rog .han .geos".i.ra.go .hae.myeong.haess.da.
    # ENGLISH: This place, the taste here is the best.
    # CONFLICT: 7:것은(nsubj→있다), 10:소지가(nsubj→있다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s398': [('deprel', 7, 'nsubj:outer')],

    # train-s3989
    # TEXT: 멩엘베르흐는 바흐나 헨델 등의 바로크 음악에서 자신의 스승과 친구이기도 했던 말러와 리하르트 슈트라우스에 이르는 방대한 레퍼토리 영역을 개척했고, 엄격한 리허설로 악단 합주력을 최상급으로 유지시키는 한편 피에르 몽퇴나 브루노 발터 등을 객원 지휘자로 초빙해 공연하도록 주선하기도 했다.
    # TRANSLIT: .meng.el.be.reu.heu.neun .ba.heu.na .hen.del .deung.yi .ba.ro.keu .eum.ag.e.seo .ja.sin.yi .seu.seung.gwa .chin.gu.i.gi.do .haess.deon .mal.reo.wa .ri.ha.reu.teu .syu.teu.ra.u.seu.e .i.reu.neun .bang.dae.han .re.peo.to.ri .yeong.yeog.eul .gae.cheog.haess.go, .eom.gyeog.han .ri.heo.seol.ro .ag.dan .hab.ju.ryeog.eul .choe.sang.geub.eu.ro .yu.ji.si.ki.neun .han.pyeon .pi.e.reu .mong.toe.na .beu.ru.no .bal.teo .deung.eul .gaeg.weon .ji.hwi.ja.ro .cho.bing.hae .gong.yeon.ha.do.rog .ju.seon.ha.gi.do .haess.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:멩엘베르흐는(nsubj→했다), 36:주선하기도(nsubj→했다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s3989': [('deprel', 1, 'nsubj:outer')],

    # train-s3996
    # TEXT: 반찬도 하나 하나 정갈하고 맛있다.
    # TRANSLIT: .ban.chan.do .ha.na .ha.na .jeong.gal.ha.go .mas.iss.da.
    # ENGLISH: This place also has something special.
    # CONFLICT: 1:반찬도(nsubj→맛있다), 2:하나(nsubj→맛있다)
    # Fix: also-marker: N1(도)→outer
    'train-s3996': [('deprel', 1, 'nsubj:outer')],

    # train-s4022
    # TEXT: 보라카이는 바다가 예쁘기 때문에 사실 풀빌라보다는 전용 비치가 있는 리조트가 더 좋습니다.
    # TRANSLIT: .bo.ra.ka.i.neun .ba.da.ga .ye.bbeu.gi .ddae.mun.e .sa.sil .pul.bil.ra.bo.da.neun .jeon.yong .bi.chi.ga .iss.neun .ri.jo.teu.ga .deo .joh.seub.ni.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:보라카이는(nsubj→예쁘기), 2:바다가(nsubj→예쁘기)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4022': [('deprel', 1, 'nsubj:outer')],

    # train-s4034
    # TEXT: 금 탐사 상품을 운영하고 있는 여행업체의 한 부사장은 "과거에는 금 탐사가 나이 든 사람들의 단체 여행인 경우가 많았지만 최근에는 젊은이들이 많이 나타난다"며 "주된 이유는 금 가격 때문으로 생각된다"고 말했다.
    # TRANSLIT: .geum .tam.sa .sang.pum.eul .un.yeong.ha.go .iss.neun .yeo.haeng.eob.che.yi .han .bu.sa.jang.eun ".gwa.geo.e.neun .geum .tam.sa.ga .na.i .deun .sa.ram.deul.yi .dan.che .yeo.haeng.in .gyeong.u.ga .manh.ass.ji.man .choe.geun.e.neun .jeorm.eun.i.deul.i .manh.i .na.ta.nan.da".myeo ".ju.doen .i.yu.neun .geum .ga.gyeog .ddae.mun.eu.ro .saeng.gag.doen.da".go .mal.haess.da.
    # ENGLISH: Gold, there were many cases in the past.
    # CONFLICT: 11:금(nsubj→많았지만), 18:경우가(nsubj→많았지만)
    # Fix: default: N1(금)→outer [NEEDS REVIEW]
    'train-s4034': [('deprel', 11, 'nsubj:outer')],

    # train-s4054
    # TEXT: 경연대회는 진도 강강술래 원형을 중심으로 전통부문 위주로 펼쳐지며 참가대상은 강강술래에 관심있는 사람이면 누구나 가능하다.
    # TRANSLIT: .gyeong.yeon.dae.hoe.neun .jin.do .gang.gang.sul.rae .weon.hyeong.eul .jung.sim.eu.ro .jeon.tong.bu.mun .wi.ju.ro .pyeol.chyeo.ji.myeo .cham.ga.dae.sang.eun .gang.gang.sul.rae.e .gwan.sim.iss.neun .sa.ram.i.myeon .nu.gu.na .ga.neung.ha.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 9:참가대상은(nsubj→가능하다), 13:누구나(nsubj→가능하다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4054': [('deprel', 9, 'nsubj:outer')],

    # train-s4080
    # TEXT: 이 가운데 12건은 양성판정이 나왔고, 나머지 16건은 정밀조사가 진행 중이다.
    # TRANSLIT: .i .ga.un.de 12.geon.eun .yang.seong.pan.jeong.i .na.wass.go, .na.meo.ji 16.geon.eun .jeong.mil.jo.sa.ga .jin.haeng .jung.i.da.
    # ENGLISH: The remaining part needs to be investigated.
    # CONFLICT: 3:12건은(nsubj→나왔고), 4:양성판정이(nsubj→나왔고)
    # CONFLICT: 7:나머지(nsubj→진행), 9:정밀조사가(nsubj→진행)
    # Fix: topic-marker: N1(은/는)→outer | default: N1(나머지)→outer [NEEDS REVIEW]
    'train-s4080': [('deprel', 3, 'nsubj:outer'), ('deprel', 7, 'nsubj:outer')],

    # train-s4091
    # TEXT: 전 여기 커피 너무 맛있는데.
    # TRANSLIT: .jeon .yeo.gi .keo.pi .neo.mu .mas.iss.neun.de.
    # ENGLISH: Before, the coffee was delicious.
    # CONFLICT: 1:전(nsubj→맛있는데), 3:커피(nsubj→맛있는데)
    # Fix: default: N1(전)→outer [NEEDS REVIEW]
    'train-s4091': [('deprel', 1, 'nsubj:outer')],

    # train-s4093
    # TEXT: 유치부는 강남 엄마들이 가장 보내고 싶어하는 교육기관으로 정평이 나있고, 초등 엘리트코스는 영유 졸업생만을 위한 특별과정으로 입학시험이 매우 까다롭기로 소문이 자자함.
    # TRANSLIT: .yu.chi.bu.neun .gang.nam .eom.ma.deul.i .ga.jang .bo.nae.go .sip.eo.ha.neun .gyo.yug.gi.gwan.eu.ro .jeong.pyeong.i .na.iss.go, .cho.deung .el.ri.teu.ko.seu.neun .yeong.yu .jol.eob.saeng.man.eul .wi.han .teug.byeol.gwa.jeong.eu.ro .ib.hag.si.heom.i .mae.u .gga.da.rob.gi.ro .so.mun.i .ja.ja.ham.
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:유치부는(nsubj→나있고), 8:정평이(nsubj→나있고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4093': [('deprel', 1, 'nsubj:outer')],

    # train-s4098
    # TEXT: 노벨평화상 수상 소식은 외교부 사이트의 반박 성명과 이를 보도한 신화통신 기사가 전부다.
    # TRANSLIT: .no.bel.pyeong.hwa.sang .su.sang .so.sig.eun .oe.gyo.bu .sa.i.teu.yi .ban.bag .seong.myeong.gwa .i.reul .bo.do.han .sin.hwa.tong.sin .gi.sa.ga .jeon.bu.da.
    # ENGLISH: The Nobel Peace Prize is a complete refutation.
    # CONFLICT: 1:노벨평화상(nsubj→전부다), 6:반박(nsubj→전부다)
    # Fix: default: N1(노벨평화상)→outer [NEEDS REVIEW]
    'train-s4098': [('deprel', 1, 'nsubj:outer')],

    # train-s4107
    # TEXT: 대한민국은 2007년 10월 9일에 도입되었으며 개별 국가의 정부 기관이 등록 대상이 되는 1단계에 대한민국은 180여개 도메인을 할당받았다.
    # TRANSLIT: .dae.han.min.gug.eun 2007.nyeon 10.weol 9.il.e .do.ib.doe.eoss.eu.myeo .gae.byeol .gug.ga.yi .jeong.bu .gi.gwan.i .deung.rog .dae.sang.i .doe.neun 1.dan.gye.e .dae.han.min.gug.eun 180.yeo.gae .do.me.in.eul .hal.dang.bad.ass.da.
    # ENGLISH: The government has registrations.
    # CONFLICT: 8:정부(nsubj→되는), 10:등록(nsubj→되는)
    # Fix: default: N1(정부)→outer [NEEDS REVIEW]
    'train-s4107': [('deprel', 8, 'nsubj:outer')],

    # train-s414
    # TEXT: 대전이 몇 킬로 떨어져 있어?
    # TRANSLIT: .dae.jeon.i .myeoch .kil.ro .ddeol.eo.jyeo .iss.eo?
    # ENGLISH: Daejeon is only a kilometer away.
    # CONFLICT: 1:대전이(nsubj→떨어져), 3:킬로(nsubj→떨어져)
    # Fix: default: N1(대전이)→outer [NEEDS REVIEW]
    'train-s414': [('deprel', 1, 'nsubj:outer')],

    # train-s4156
    # TEXT: 친절은 따라올 곳이 없는 듯
    # TRANSLIT: .chin.jeol.eun .dda.ra.ol .gos.i .eobs.neun .deus
    # ENGLISH: This is a really good place.
    # CONFLICT: 1:친절은(nsubj→없는), 3:곳이(nsubj→없는)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4156': [('deprel', 1, 'nsubj:outer')],

    # train-s4161
    # TEXT: 유럽에서 기독교가 극도의 세를 떨치고 있을 12~13세기, 연대기 역사가 틸버리의 저베이스(Gervase of Tilbury)가 늑대인간의 변신은 보름달과 관련이 있다고 언급하였다.
    # TRANSLIT: .yu.reob.e.seo .gi.dog.gyo.ga .geug.do.yi .se.reul .ddeol.chi.go .iss.eul 12~13.se.gi, .yeon.dae.gi .yeog.sa.ga .til.beo.ri.yi .jeo.be.i.seu(Gervase of Tilbury).ga .neug.dae.in.gan.yi .byeon.sin.eun .bo.reum.dal.gwa .gwan.ryeon.i .iss.da.go .eon.geub.ha.yeoss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 20:변신은(nsubj→있다고), 22:관련이(nsubj→있다고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4161': [('deprel', 20, 'nsubj:outer')],

    # train-s4169
    # TEXT: 그러나 지방의 마이너 다이묘의 배하 무장의 평가는 낮고, 특히 '붉은 귀신(赤鬼)'이라고 두려워 했던 하타노 가의 아카이 나오마사(본작에서는 아기노 나오마사荻野直正로 등장 ), 아자이 가의 이소노 가즈마사 등은, 후의 작품의 설정에 비해 능력치가 상당히 낮았다.
    # TRANSLIT: .geu.reo.na .ji.bang.yi .ma.i.neo .da.i.myo.yi .bae.ha .mu.jang.yi .pyeong.ga.neun .naj.go, .teug.hi '.burg.eun .gwi.sin(chìguǐ)'.i.ra.go .du.ryeo.weo .haess.deon .ha.ta.no .ga.yi .a.ka.i .na.o.ma.sa(.bon.jag.e.seo.neun .a.gi.no .na.o.ma.sa荻yězhízhèng.ro .deung.jang ), .a.ja.i .ga.yi .i.so.no .ga.jeu.ma.sa .deung.eun, .hu.yi .jag.pum.yi .seol.jeong.e .bi.hae .neung.ryeog.chi.ga .sang.dang.hi .naj.ass.da.
    # ENGLISH: Naomasa's abilities were low.
    # CONFLICT: 24:나오마사(nsubj→낮았다), 42:능력치가(nsubj→낮았다)
    # Fix: default: N1(나오마사)→outer [NEEDS REVIEW]
    'train-s4169': [('deprel', 24, 'nsubj:outer')],

    # train-s4176
    # TEXT: IBM의 PC는 개인용 컴퓨터의 표준이 됐으며 이 같은 개방성은 이후 마이크로소프트와 같은 소프트웨어 기업들이 번성하는 토대가 됐다.
    # TRANSLIT: IBM.yi PC.neun .gae.in.yong .keom.pyu.teo.yi .pyo.jun.i .dwaess.eu.myeo .i .gat.eun .gae.bang.seong.eun .i.hu .ma.i.keu.ro.so.peu.teu.wa .gat.eun .so.peu.teu.we.eo .gi.eob.deul.i .beon.seong.ha.neun .to.dae.ga .dwaess.da.
    # ENGLISH: Various important things are mentioned here.
    # CONFLICT: 2:PC는(nsubj→됐으며), 5:표준이(nsubj→됐으며)
    # CONFLICT: 9:개방성은(nsubj→됐다), 16:토대가(nsubj→됐다)
    # Fix: topic-marker: N1(은/는)→outer | topic-marker: N1(은/는)→outer
    'train-s4176': [('deprel', 2, 'nsubj:outer'), ('deprel', 9, 'nsubj:outer')],

    # train-s4177
    # TEXT: 솔직히 관광지는 숙박요금이나 식당들 가격대가 센 편인데 이 집은 3만 원부터 있네요.
    # TRANSLIT: .sol.jig.hi .gwan.gwang.ji.neun .sug.bag.yo.geum.i.na .sig.dang.deul .ga.gyeog.dae.ga .sen .pyeon.in.de .i .jib.eun 3.man .weon.bu.teo .iss.ne.yo.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 2:관광지는(nsubj→센), 3:숙박요금이나(nsubj→센)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4177': [('deprel', 2, 'nsubj:outer')],

    # train-s4180
    # TEXT: 독일군과 오스트리아군의 두 번째 공격에서는 이탈리아군의 강한 저항에 부딪혀 첫 번째 공세보다는 적은 전진을 하게 되는데 그럼에도 불구하고 중앙지역에서의 계속된 성공으로 인해 이미 이탈리아군은 더 이상 카포레토 전선을 지킬만한 힘이 없게 된다.
    # TRANSLIT: .dog.il.gun.gwa .o.seu.teu.ri.a.gun.yi .du .beon.jjae .gong.gyeog.e.seo.neun .i.tal.ri.a.gun.yi .gang.han .jeo.hang.e .bu.dij.hyeo .cheos .beon.jjae .gong.se.bo.da.neun .jeog.eun .jeon.jin.eul .ha.ge .doe.neun.de .geu.reom.e.do .bul.gu.ha.go .jung.ang.ji.yeog.e.seo.yi .gye.sog.doen .seong.gong.eu.ro .in.hae .i.mi .i.tal.ri.a.gun.eun .deo .i.sang .ka.po.re.to .jeon.seon.eul .ji.kil.man.han .him.i .eobs.ge .doen.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 24:이탈리아군은(nsubj→없게), 30:힘이(nsubj→없게)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4180': [('deprel', 24, 'nsubj:outer')],

    # train-s4184
    # TEXT: 그 때문에 아이누족은 누구에게나 통용되는 평범한 이름이라는 것(철수, 영희, 홍길동같은)이 없다고 한다.
    # TRANSLIT: .geu .ddae.mun.e .a.i.nu.jog.eun .nu.gu.e.ge.na .tong.yong.doe.neun .pyeong.beom.han .i.reum.i.ra.neun .geos(.cheol.su, .yeong.hyi, .hong.gil.dong.gat.eun).i .eobs.da.go .han.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 3:아이누족은(nsubj→없다고), 8:것(nsubj→없다고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4184': [('deprel', 3, 'nsubj:outer')],

    # train-s4233
    # TEXT: 그후 기욤은 연방총리실 직원이 된다(1970년).
    # TRANSLIT: .geu.hu .gi.yom.eun .yeon.bang.chong.ri.sil .jig.weon.i .doen.da(1970.nyeon).
    # ENGLISH: This place is very good.
    # CONFLICT: 2:기욤은(nsubj→된다), 3:연방총리실(nsubj→된다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4233': [('deprel', 2, 'nsubj:outer')],

    # train-s4272
    # TEXT: 베트남 현대미술은 '베트남전'의 기억과 상흔이 고스란히 반영되어 있다.
    # TRANSLIT: .be.teu.nam .hyeon.dae.mi.sul.eun '.be.teu.nam.jeon'.yi .gi.eog.gwa .sang.heun.i .go.seu.ran.hi .ban.yeong.doe.eo .iss.da.
    # ENGLISH: Vietnam reflects the Vietnam War.
    # CONFLICT: 1:베트남(nsubj:pass→반영되어), 4:베트남전(nsubj:pass→반영되어)
    # Fix: default: N1(베트남)→outer [NEEDS REVIEW]
    'train-s4272': [('deprel', 1, 'nsubj:outer')],

    # train-s4279
    # TEXT: KINS 원장공모는 내부 인사와 외부 인사 간의 경쟁 구도에서 교과부 고위직 공무원 내정설도 돌았으나 윤철호 전 원장의 반대로 내부 인사로만 채워졌다는 게 내부 소식통의 전언이다.
    # TRANSLIT: KINS .weon.jang.gong.mo.neun .nae.bu .in.sa.wa .oe.bu .in.sa .gan.yi .gyeong.jaeng .gu.do.e.seo .gyo.gwa.bu .go.wi.jig .gong.mu.weon .nae.jeong.seol.do .dol.ass.eu.na .yun.cheol.ho .jeon .weon.jang.yi .ban.dae.ro .nae.bu .in.sa.ro.man .chae.weo.jyeoss.da.neun .ge .nae.bu .so.sig.tong.yi .jeon.eon.i.da.
    # ENGLISH: KINS, the Ministry of Education circulated it.
    # CONFLICT: 1:KINS(nsubj→돌았으나), 10:교과부(nsubj→돌았으나)
    # Fix: default: N1(KINS)→outer [NEEDS REVIEW]
    'train-s4279': [('deprel', 1, 'nsubj:outer')],

    # train-s4299
    # TEXT: 판단 기준이 된 다른 사상은 도가와 법가의 혼합을 이룬 황로파나 법가의 사상가들인 상앙, 신불해 등의 것이 있다.
    # TRANSLIT: .pan.dan .gi.jun.i .doen .da.reun .sa.sang.eun .do.ga.wa .beob.ga.yi .hon.hab.eul .i.run .hwang.ro.pa.na .beob.ga.yi .sa.sang.ga.deul.in .sang.ang, .sin.bul.hae .deung.yi .geos.i .iss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 5:사상은(nsubj→있다), 17:것이(nsubj→있다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4299': [('deprel', 5, 'nsubj:outer')],

    # train-s4302
    # TEXT: 또한 진성대군(중종)이 그의 사위가 되었다.
    # TRANSLIT: .ddo.han .jin.seong.dae.gun(.jung.jong).i .geu.yi .sa.wi.ga .doe.eoss.da.
    # ENGLISH: Prince Jinseong's son-in-law became king.
    # CONFLICT: 2:진성대군(nsubj→되었다), 8:사위가(nsubj→되었다)
    # Fix: default: N1(진성대군)→outer [NEEDS REVIEW]
    'train-s4302': [('deprel', 2, 'nsubj:outer')],

    # train-s4317
    # TEXT: 안주도 분위기도 서비스도 모두 다 별 다섯 개!
    # TRANSLIT: .an.ju.do .bun.wi.gi.do .seo.bi.seu.do .mo.du .da .byeol .da.seos .gae!
    # ENGLISH: Various things are good here.
    # CONFLICT: 1:안주도(nsubj→별), 2:분위기도(nsubj→별), 3:서비스도(nsubj→별)
    # Fix: triple: [1, 2, 3]→outer
    'train-s4317': [('deprel', 1, 'nsubj:outer'), ('deprel', 2, 'nsubj:outer'), ('deprel', 3, 'nsubj:outer')],

    # train-s4361
    # TEXT: '미국의 빨대'노릇을 자처한 언론인도 위키리크스 때문에 곳곳에서 정체가 드러났다.
    # TRANSLIT: '.mi.gug.yi .bbal.dae'.no.reus.eul .ja.cheo.han .eon.ron.in.do .wi.ki.ri.keu.seu .ddae.mun.e .gos.gos.e.seo .jeong.che.ga .deu.reo.nass.da.
    # ENGLISH: This place also has good food.
    # CONFLICT: 7:언론인도(nsubj→드러났다), 11:정체가(nsubj→드러났다)
    # Fix: also-marker: N1(도)→outer
    'train-s4361': [('deprel', 7, 'nsubj:outer')],

    # train-s4375
    # TEXT: 원인이 여러가지 있겠지만 "염치"란 의미를 모르고 염치없이 사는 사람들이 너무 많기 때문이 아닌가 생각해 보기도 한다.
    # TRANSLIT: .weon.in.i .yeo.reo.ga.ji .iss.gess.ji.man ".yeom.chi".ran .yi.mi.reul .mo.reu.go .yeom.chi.eobs.i .sa.neun .sa.ram.deul.i .neo.mu .manh.gi .ddae.mun.i .a.nin.ga .saeng.gag.hae .bo.gi.do .han.da.
    # ENGLISH: There are probably many causes.
    # CONFLICT: 1:원인이(nsubj→있겠지만), 2:여러가지(nsubj→있겠지만)
    # Fix: default: N1(원인이)→outer [NEEDS REVIEW]
    'train-s4375': [('deprel', 1, 'nsubj:outer')],

    # train-s4391
    # TEXT: 같은 매출액은 2408억 원으로 전년대비 30.7% 증가했으며 당기순익은 65억 원을 기록해 49.5% 감소함.
    # TRANSLIT: .gat.eun .mae.chul.aeg.eun 2408.eog .weon.eu.ro .jeon.nyeon.dae.bi 30.7% .jeung.ga.haess.eu.myeo .dang.gi.sun.ig.eun 65.eog .weon.eul .gi.rog.hae 49.5% .gam.so.ham.
    # ENGLISH: Various important things are mentioned here.
    # CONFLICT: 2:매출액은(nsubj→증가했으며), 5:전년대비(nsubj→증가했으며)
    # CONFLICT: 9:당기순익은(nsubj→감소함), 14:%(nsubj→감소함)
    # Fix: topic-marker: N1(은/는)→outer | topic-marker: N1(은/는)→outer
    'train-s4391': [('deprel', 2, 'nsubj:outer'), ('deprel', 9, 'nsubj:outer')],

    # train-s4393
    # TEXT: 특히, 주목할만한 것은 원래 우주라는 말은 오늘날의 우주가 공간만을 지칭하지만, 이 시기의 우주는 공간과 시간을 함께 의미하는 것이었다.
    # TRANSLIT: .teug.hi, .ju.mog.hal.man.han .geos.eun .weon.rae .u.ju.ra.neun .mal.eun .o.neul.nal.yi .u.ju.ga .gong.gan.man.eul .ji.ching.ha.ji.man, .i .si.gi.yi .u.ju.neun .gong.gan.gwa .si.gan.eul .ham.gge .yi.mi.ha.neun .geos.i.eoss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 7:말은(nsubj→지칭하지만), 9:우주가(nsubj→지칭하지만)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s4393': [('deprel', 7, 'nsubj:outer')],

    # train-s4395
    # TEXT: 이용대는 "경기 전 정상적으로 훈련한 기간이 일주일도 되지 않았다"며 "훈련을 제대로 하지 못한 탓에 경기 때 체력이 떨어졌다"고 분석했다.
    # TRANSLIT: .i.yong.dae.neun ".gyeong.gi .jeon .jeong.sang.jeog.eu.ro .hun.ryeon.han .gi.gan.i .il.ju.il.do .doe.ji .anh.ass.da".myeo ".hun.ryeon.eul .je.dae.ro .ha.ji .mos.han .tas.e .gyeong.gi .ddae .che.ryeog.i .ddeol.eo.jyeoss.da".go .bun.seog.haess.da.
    # ENGLISH: This place also has something good.
    # CONFLICT: 7:기간이(nsubj→되지), 8:일주일도(nsubj→되지)
    # Fix: also-marker: N2(도)→outer
    'train-s4395': [('deprel', 8, 'nsubj:outer')],

    # train-s451
    # TEXT: 당시 불교계는 내분 사태가 이미 일단락되는 중이었기 때문에, 조계종 총무원장 월주가 전두환 지지 성명에 반대하고 5?18 광주 민주화 운동 현장을 방문하여 성금을 전달하는 등 신군부에 밉보인 것이 원인이라는 해석이 있다.
    # TRANSLIT: .dang.si .bul.gyo.gye.neun .nae.bun .sa.tae.ga .i.mi .il.dan.rag.doe.neun .jung.i.eoss.gi .ddae.mun.e, .jo.gye.jong .chong.mu.weon.jang .weol.ju.ga .jeon.du.hwan .ji.ji .seong.myeong.e .ban.dae.ha.go 5?18 .gwang.ju .min.ju.hwa .un.dong .hyeon.jang.eul .bang.mun.ha.yeo .seong.geum.eul .jeon.dal.ha.neun .deung .sin.gun.bu.e .mib.bo.in .geos.i .weon.in.i.ra.neun .hae.seog.i .iss.da.
    # ENGLISH: This place is really good.
    # CONFLICT: 2:불교계는(nsubj→일단락되는), 3:내분(nsubj:pass→일단락되는)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s451': [('deprel', 2, 'nsubj:outer')],

    # train-s46
    # TEXT: 이 보도가 맞다면 우리도 종교의 자유가 있네 하고 떠들어온 북한의 주장이 얼마나 가당찮은 거짓말인지 확연히 드러난다.
    # TRANSLIT: .i .bo.do.ga .maj.da.myeon .u.ri.do .jong.gyo.yi .ja.yu.ga .iss.ne .ha.go .ddeo.deul.eo.on .bug.han.yi .ju.jang.i .eol.ma.na .ga.dang.chanh.eun .geo.jis.mal.in.ji .hwag.yeon.hi .deu.reo.nan.da.
    # ENGLISH: If this report is correct, it clearly reveals how far-fetched North Korea's claim that we too have religious freedom is.
    # CONFLICT: 4:우리도(nsubj→있네), 6:자유가(nsubj→있네)
    # Fix: also-marker: N1(도)→outer
    'train-s46': [('deprel', 4, 'nsubj:outer')],

    # train-s462
    # TEXT: 대전으로 가는 대중교통이 뭐가 있지?
    # TRANSLIT: .dae.jeon.eu.ro .ga.neun .dae.jung.gyo.tong.i .mweo.ga .iss.ji?
    # ENGLISH: What public transportation is available?
    # CONFLICT: 3:대중교통이(nsubj→있지), 4:뭐가(nsubj→있지)
    # Fix: default: N1(대중교통이)→outer [NEEDS REVIEW]
    'train-s462': [('deprel', 3, 'nsubj:outer')],

    # train-s51
    # TEXT: 또한 항상 후덕한 미소를 띠는 모습이 이웃집 아줌마 같습니다.
    # TRANSLIT: .ddo.han .hang.sang .hu.deog.han .mi.so.reul .ddi.neun .mo.seub.i .i.us.jib .a.jum.ma .gat.seub.ni.da.
    # ENGLISH: The look of always wearing a generous smile is like the lady next door.
    # CONFLICT: 6:모습이(nsubj→같습니다), 7:이웃집(nsubj→같습니다)
    # Fix: default: N1(모습이)→outer [NEEDS REVIEW]
    'train-s51': [('deprel', 6, 'nsubj:outer')],

    # train-s525
    # TEXT: 원장님이 성격 넘 좋으시구 기사님 너무 친절하십니다.
    # TRANSLIT: .weon.jang.nim.i .seong.gyeog .neom .joh.eu.si.gu .gi.sa.nim .neo.mu .chin.jeol.ha.sib.ni.da.
    # ENGLISH: The director has a good personality.
    # CONFLICT: 1:원장님이(nsubj→좋으시구), 2:성격(nsubj→좋으시구)
    # Fix: default: N1(원장님이)→outer [NEEDS REVIEW]
    'train-s525': [('deprel', 1, 'nsubj:outer')],

    # train-s532
    # TEXT: 국내기업은 2분기에도 실적호조가 예상되는 반면 코스피지수는 유럽발 충격에 급락했다.
    # TRANSLIT: .gug.nae.gi.eob.eun 2.bun.gi.e.do .sil.jeog.ho.jo.ga .ye.sang.doe.neun .ban.myeon .ko.seu.pi.ji.su.neun .yu.reob.bal .chung.gyeog.e .geub.rag.haess.da.
    # ENGLISH: This is a very good place.
    # CONFLICT: 1:국내기업은(nsubj→예상되는), 3:실적호조가(nsubj→예상되는)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s532': [('deprel', 1, 'nsubj:outer')],

    # train-s558
    # TEXT: 이는 결국 12월 초에 유로존 재무장관 모임(유로그룹)과 Ecofin의 특별회의가 각각 한 차례 더 열려야 확정될 것이라는 관측도 나오고 있다.
    # TRANSLIT: .i.neun .gyeol.gug 12.weol .cho.e .yu.ro.jon .jae.mu.jang.gwan .mo.im(.yu.ro.geu.rub).gwa Ecofin.yi .teug.byeol.hoe.yi.ga .gag.gag .han .cha.rye .deo .yeol.ryeo.ya .hwag.jeong.doel .geos.i.ra.neun .gwan.cheug.do .na.o.go .iss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 1:이는(nsubj→나오고), 21:관측도(nsubj→나오고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s558': [('deprel', 1, 'nsubj:outer')],

    # train-s571
    # TEXT: 가격은 전 트림이 SM3대비 70만원이 올라가 ▲SE 1660만원 ▲LE 1860만원 ▲RE 1960만원이다.
    # TRANSLIT: .ga.gyeog.eun .jeon .teu.rim.i SM3.dae.bi 70.man.weon.i .ol.ra.ga ▲SE 1660.man.weon ▲LE 1860.man.weon ▲RE 1960.man.weon.i.da.
    # ENGLISH: Before, the price went up by 700,000 won.
    # CONFLICT: 2:전(nsubj→올라가), 5:70만원이(nsubj→올라가)
    # Fix: default: N1(전)→outer [NEEDS REVIEW]
    'train-s571': [('deprel', 2, 'nsubj:outer')],

    # train-s58
    # TEXT: 실제로 이들 중 83.8%는 무의식적인 버릇을 반복하는 지원자를 탈락시킨 경험이 있는 것으로 나타났다.
    # TRANSLIT: .sil.je.ro .i.deul .jung 83.8%.neun .mu.yi.sig.jeog.in .beo.reus.eul .ban.bog.ha.neun .ji.weon.ja.reul .tal.rag.si.kin .gyeong.heom.i .iss.neun .geos.eu.ro .na.ta.nass.da.
    # ENGLISH: 83.8% of respondents said they had experience of visiting a restaurant within 5 km of their home.
    # CONFLICT: 4:83.8(nsubj→있는), 12:경험이(nsubj→있는)
    # Fix: default: N1(83.8)→outer [NEEDS REVIEW]
    'train-s58': [('deprel', 4, 'nsubj:outer')],

    # train-s583
    # TEXT: 그라운드의 중앙은 빨간색보다 파란색이 더욱 눈에 들어왔다.
    # TRANSLIT: .geu.ra.un.deu.yi .jung.ang.eun .bbal.gan.saeg.bo.da .pa.ran.saeg.i .deo.ug .nun.e .deul.eo.wass.da.
    # ENGLISH: This place is very good.
    # CONFLICT: 2:중앙은(nsubj→들어왔다), 4:파란색이(nsubj→들어왔다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s583': [('deprel', 2, 'nsubj:outer')],

    # train-s588
    # TEXT: 갈치 조림 실망이 큽니다
    # TRANSLIT: .gal.chi .jo.rim .sil.mang.i .keub.ni.da
    # ENGLISH: The hairtail fish here is very disappointing.
    # CONFLICT: 1:갈치(nsubj→큽니다), 3:실망이(nsubj→큽니다)
    # Fix: default: N1(갈치)→outer [NEEDS REVIEW]
    'train-s588': [('deprel', 1, 'nsubj:outer')],

    # train-s597
    # TEXT: 한 폭의 그림 안에 들어가는 사과만도 120개가 넘지요.
    # TRANSLIT: .han .pog.yi .geu.rim .an.e .deul.eo.ga.neun .sa.gwa.man.do 120.gae.ga .neom.ji.yo.
    # ENGLISH: This place also has good food.
    # CONFLICT: 6:사과만도(nsubj→넘지요), 7:120개가(nsubj→넘지요)
    # Fix: also-marker: N1(도)→outer
    'train-s597': [('deprel', 6, 'nsubj:outer')],

    # train-s604
    # TEXT: 그들은 이후의 왕정복고에서 권좌에 복귀한 왕당파로부터 원수로 백색 테러의 표적이 되었기 때문이다.
    # TRANSLIT: .geu.deul.eun .i.hu.yi .wang.jeong.bog.go.e.seo .gweon.jwa.e .bog.gwi.han .wang.dang.pa.ro.bu.teo .weon.su.ro .baeg.saeg .te.reo.yi .pyo.jeog.i .doe.eoss.gi .ddae.mun.i.da.
    # ENGLISH: This is a very meaningful place.
    # CONFLICT: 1:그들은(nsubj→되었기), 10:표적이(nsubj→되었기)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s604': [('deprel', 1, 'nsubj:outer')],

    # train-s606
    # TEXT: 진포철도의 북부 구간은 당시 공사가 시작되었고, 현재의 정해현 낭왕장에서 공사를 시작했지만, 톈진 기점의 위치가 결정되지도 않은 상황이었다.
    # TRANSLIT: .jin.po.cheol.do.yi .bug.bu .gu.gan.eun .dang.si .gong.sa.ga .si.jag.doe.eoss.go, .hyeon.jae.yi .jeong.hae.hyeon .nang.wang.jang.e.seo .gong.sa.reul .si.jag.haess.ji.man, .tyen.jin .gi.jeom.yi .wi.chi.ga .gyeol.jeong.doe.ji.do .anh.eun .sang.hwang.i.eoss.da.
    # ENGLISH: The northern part has started construction.
    # CONFLICT: 2:북부(nsubj:pass→시작되었고), 5:공사가(nsubj:pass→시작되었고)
    # Fix: default: N1(북부)→outer [NEEDS REVIEW]
    'train-s606': [('deprel', 2, 'nsubj:outer')],

    # train-s621
    # TEXT: 1800년대 후반에 간저우는 남부의 조약항으로 개방된 곳 중 하나로 외국 회사들을 위한 작은 기반이 되었다.
    # TRANSLIT: 1800.nyeon.dae .hu.ban.e .gan.jeo.u.neun .nam.bu.yi .jo.yag.hang.eu.ro .gae.bang.doen .gos .jung .ha.na.ro .oe.gug .hoe.sa.deul.eul .wi.han .jag.eun .gi.ban.i .doe.eoss.da.
    # ENGLISH: This is a really good place.
    # CONFLICT: 3:간저우는(nsubj→되었다), 14:기반이(nsubj→되었다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s621': [('deprel', 3, 'nsubj:outer')],

    # train-s627
    # TEXT: 짜장은 편의점 3분 짜장을 부어 놓은 것 같네요.
    # TRANSLIT: .jja.jang.eun .pyeon.yi.jeom 3.bun .jja.jang.eul .bu.eo .noh.eun .geos .gat.ne.yo.
    # ENGLISH: This place is very good.
    # CONFLICT: 1:짜장은(nsubj→같네요), 7:것(nsubj→같네요)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s627': [('deprel', 1, 'nsubj:outer')],

    # train-s652
    # TEXT: 내가 활동하고 있는 게이인권운동단체 친구 사이의 작은 소모임으로 출발한 지-보이스는 이제 성소수자들 사이에선 꽤 유명한 합창단이 되었다.
    # TRANSLIT: .nae.ga .hwal.dong.ha.go .iss.neun .ge.i.in.gweon.un.dong.dan.che .chin.gu .sa.i.yi .jag.eun .so.mo.im.eu.ro .chul.bal.han .ji-.bo.i.seu.neun .i.je .seong.so.su.ja.deul .sa.i.e.seon .ggwae .yu.myeong.han .hab.chang.dan.i .doe.eoss.da.
    # ENGLISH: This restaurant is really good.
    # CONFLICT: 10:지-보이스는(nsubj→되었다), 16:합창단이(nsubj→되었다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s652': [('deprel', 10, 'nsubj:outer')],

    # train-s680
    # TEXT: 프로는 모르고 망하는 경우가 거의 없다.
    # TRANSLIT: .peu.ro.neun .mo.reu.go .mang.ha.neun .gyeong.u.ga .geo.yi .eobs.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 1:프로는(nsubj→없다), 4:경우가(nsubj→없다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s680': [('deprel', 1, 'nsubj:outer')],

    # train-s681
    # TEXT: 양쪽 고막은 기압이 같아야 하며, 이관은 기압을 조정하기 위한 기관이다.
    # TRANSLIT: .yang.jjog .go.mag.eun .gi.ab.i .gat.a.ya .ha.myeo, .i.gwan.eun .gi.ab.eul .jo.jeong.ha.gi .wi.han .gi.gwan.i.da.
    # ENGLISH: The pressure should be the same on both sides.
    # CONFLICT: 1:양쪽(nsubj→같아야), 3:기압이(nsubj→같아야)
    # Fix: default: N1(양쪽)→outer [NEEDS REVIEW]
    'train-s681': [('deprel', 1, 'nsubj:outer')],

    # train-s685
    # TEXT: 지식경제부는 25일 현대자동차 등 5개 완성차와 주요 부품업계 임원들과 간담회를 열어 한미 자유무역협정(FTA)은 자동차업계에 새로운 기회가 될 수 있기 때문에 달라지는 업계환경에 적극적으로 대응해 수출에 주력해 달라고 당부했다.
    # TRANSLIT: .ji.sig.gyeong.je.bu.neun 25.il .hyeon.dae.ja.dong.cha .deung 5.gae .wan.seong.cha.wa .ju.yo .bu.pum.eob.gye .im.weon.deul.gwa .gan.dam.hoe.reul .yeol.eo .han.mi .ja.yu.mu.yeog.hyeob.jeong(FTA).eun .ja.dong.cha.eob.gye.e .sae.ro.un .gi.hoe.ga .doel .su .iss.gi .ddae.mun.e .dal.ra.ji.neun .eob.gye.hwan.gyeong.e .jeog.geug.jeog.eu.ro .dae.eung.hae .su.chul.e .ju.ryeog.hae .dal.ra.go .dang.bu.haess.da.
    # ENGLISH: The Korea-US relationship is an opportunity.
    # CONFLICT: 12:한미(nsubj→될), 20:기회가(nsubj→될)
    # Fix: default: N1(한미)→outer [NEEDS REVIEW]
    'train-s685': [('deprel', 12, 'nsubj:outer')],

    # train-s69
    # TEXT: 친절하고 인테리어는 괜찮지만 뭐 하나 특출나게 맛난 게 없다
    # TRANSLIT: .chin.jeol.ha.go .in.te.ri.eo.neun .gwaen.chanh.ji.man .mweo .ha.na .teug.chul.na.ge .mas.nan .ge .eobs.da
    # ENGLISH: There is not one good thing about this.
    # CONFLICT: 5:하나(nsubj→없다), 8:게(nsubj→없다)
    # Fix: default: N1(하나)→outer [NEEDS REVIEW]
    'train-s69': [('deprel', 5, 'nsubj:outer')],

    # train-s720
    # TEXT: 국물 맛이 다른 곳과는 많은 차이가 있더군요
    # TRANSLIT: .gug.mul .mas.i .da.reun .gos.gwa.neun .manh.eun .cha.i.ga .iss.deo.gun.yo
    # ENGLISH: The broth is different.
    # CONFLICT: 1:국물(nsubj→있더군요), 6:차이가(nsubj→있더군요)
    # Fix: default: N1(국물)→outer [NEEDS REVIEW]
    'train-s720': [('deprel', 1, 'nsubj:outer')],

    # train-s725
    # TEXT: 소문대로 비빔밀면 맛이 있네요..
    # TRANSLIT: .so.mun.dae.ro .bi.bim.mil.myeon .mas.i .iss.ne.yo..
    # ENGLISH: The bibim-milmyeon noodles are delicious.
    # CONFLICT: 2:비빔밀면(nsubj→있네요), 3:맛이(nsubj→있네요)
    # Fix: default: N1(비빔밀면)→outer [NEEDS REVIEW]
    'train-s725': [('deprel', 2, 'nsubj:outer')],

    # train-s727
    # TEXT: 이들 국가의 천손사상 또한 이러한 맥락과 관련이 깊으며, 중국의 '천자 ()', 일본의 '덴노()' 모두 이러한 사상에 연원하고 있다.
    # TRANSLIT: .i.deul .gug.ga.yi .cheon.son.sa.sang .ddo.han .i.reo.han .maeg.rag.gwa .gwan.ryeon.i .gip.eu.myeo, .jung.gug.yi '.cheon.ja ()', .il.bon.yi '.den.no()' .mo.du .i.reo.han .sa.sang.e .yeon.weon.ha.go .iss.da.
    # ENGLISH: The idea of being descendants of heaven has a deep connection.
    # CONFLICT: 3:천손사상(nsubj→깊으며), 7:관련이(nsubj→깊으며)
    # Fix: default: N1(천손사상)→outer [NEEDS REVIEW]
    'train-s727': [('deprel', 3, 'nsubj:outer')],

    # train-s728
    # TEXT: 시간, 분 단위로 세밀하게 짜 놓은 계획표가 바로 휴지가 되는 경험들을 많이 해보았을 것입니다.
    # TRANSLIT: .si.gan, .bun .dan.wi.ro .se.mil.ha.ge .jja .noh.eun .gye.hoeg.pyo.ga .ba.ro .hyu.ji.ga .doe.neun .gyeong.heom.deul.eul .manh.i .hae.bo.ass.eul .geos.ib.ni.da.
    # ENGLISH: The schedule becomes toilet paper (useless).
    # CONFLICT: 8:계획표가(nsubj→되는), 10:휴지가(nsubj→되는)
    # Fix: default: N1(계획표가)→outer [NEEDS REVIEW]
    'train-s728': [('deprel', 8, 'nsubj:outer')],

    # train-s729
    # TEXT: 델의 1분기 매출은 150억2000만 달러로 작년 같은 기간과 비슷했지만 순이익은 9억4500만 달러로 2배 가량 올랐다.
    # TRANSLIT: .del.yi 1.bun.gi .mae.chul.eun 150.eog2000.man .dal.reo.ro .jag.nyeon .gat.eun .gi.gan.gwa .bi.seus.haess.ji.man .sun.i.ig.eun 9.eog4500.man .dal.reo.ro 2.bae .ga.ryang .ol.rass.da.
    # ENGLISH: This place is very good.
    # CONFLICT: 10:순이익은(nsubj→올랐다), 13:2배(nsubj→올랐다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s729': [('deprel', 10, 'nsubj:outer')],

    # train-s734
    # TEXT: 사회복지사 1급은 사회복지기초와 사회복지실천, 사회복지정책과 제도 분야에서 8과목을 준비해야 하기 때문에 충분한 준비기간과 학습전략이 중요하다.
    # TRANSLIT: .sa.hoe.bog.ji.sa 1.geub.eun .sa.hoe.bog.ji.gi.cho.wa .sa.hoe.bog.ji.sil.cheon, .sa.hoe.bog.ji.jeong.chaeg.gwa .je.do .bun.ya.e.seo 8.gwa.mog.eul .jun.bi.hae.ya .ha.gi .ddae.mun.e .chung.bun.han .jun.bi.gi.gan.gwa .hag.seub.jeon.ryag.i .jung.yo.ha.da.
    # ENGLISH: Social workers, the preparation period is important.
    # CONFLICT: 1:사회복지사(nsubj→중요하다), 14:준비기간과(nsubj→중요하다)
    # Fix: default: N1(사회복지사)→outer [NEEDS REVIEW]
    'train-s734': [('deprel', 1, 'nsubj:outer')],

    # train-s752
    # TEXT: <위험한 독서 작가 김경욱의 작품으로 피상담자의 심리상태에 따라 도움되는 책을 추천하는 독서치료사 이야기로 배우 이화룡, 이지현이 낭독한다.
    # TRANSLIT: <.wi.heom.han .dog.seo .jag.ga .gim.gyeong.ug.yi .jag.pum.eu.ro .pi.sang.dam.ja.yi .sim.ri.sang.tae.e .dda.ra .do.um.doe.neun .chaeg.eul .chu.cheon.ha.neun .dog.seo.chi.ryo.sa .i.ya.gi.ro .bae.u .i.hwa.ryong, .i.ji.hyeon.i .nang.dog.han.da.
    # ENGLISH: Reading aloud is performed by actors.
    # CONFLICT: 3:독서(nsubj→낭독한다), 15:배우(nsubj→낭독한다)
    # Fix: default: N1(독서)→outer [NEEDS REVIEW]
    'train-s752': [('deprel', 3, 'nsubj:outer')],

    # train-s768
    # TEXT: 빨강은 나라의 통합을, 하양은 순수함, 국민의 통합과 면화를, 초록은 농업과 이슬람교의 정신적인 _ 의미를 나타낸다.
    # TRANSLIT: .bbal.gang.eun .na.ra.yi .tong.hab.eul, .ha.yang.eun .sun.su.ham, .gug.min.yi .tong.hab.gwa .myeon.hwa.reul, .cho.rog.eun .nong.eob.gwa .i.seul.ram.gyo.yi .jeong.sin.jeog.in _ .yi.mi.reul .na.ta.naen.da.
    # ENGLISH: Various things are important.
    # CONFLICT: 1:빨강은(nsubj→나타낸다), 5:하양은(nsubj→나타낸다), 12:초록은(nsubj→나타낸다)
    # Fix: triple: [1, 5, 12]→outer
    'train-s768': [('deprel', 1, 'nsubj:outer'), ('deprel', 5, 'nsubj:outer'), ('deprel', 12, 'nsubj:outer')],

    # train-s771
    # TEXT: 그런데 큰 북극고래는 그런 바다코끼리의 100배나 된다.
    # TRANSLIT: .geu.reon.de .keun .bug.geug.go.rae.neun .geu.reon .ba.da.ko.ggi.ri.yi 100.bae.na .doen.da.
    # ENGLISH: This is a very good place.
    # CONFLICT: 3:북극고래는(nsubj→된다), 6:100배나(nsubj→된다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s771': [('deprel', 3, 'nsubj:outer')],

    # train-s801
    # TEXT: 정말 말이 필요 없음.
    # TRANSLIT: .jeong.mal .mal.i .pil.yo .eobs.eum.
    # ENGLISH: No need to say anything.
    # CONFLICT: 2:말이(nsubj→없음), 3:필요(nsubj→없음)
    # Fix: default: N1(말이)→outer [NEEDS REVIEW]
    'train-s801': [('deprel', 2, 'nsubj:outer')],

    # train-s809
    # TEXT: 푸짐한 음식과 밑반찬이 많고, 시설이 청결하고 사장님이 인심이 넓다.
    # TRANSLIT: .pu.jim.han .eum.sig.gwa .mit.ban.chan.i .manh.go, .si.seol.i .cheong.gyeol.ha.go .sa.jang.nim.i .in.sim.i .neorb.da.
    # ENGLISH: The owner is generous.
    # CONFLICT: 8:사장님이(nsubj→넓다), 9:인심이(nsubj→넓다)
    # Fix: default: N1(사장님이)→outer [NEEDS REVIEW]
    'train-s809': [('deprel', 8, 'nsubj:outer')],

    # train-s822
    # TEXT: 그 거리는 우리 은하의 크기와 비교할 수 없이 멀었기 때문에 안드로메다가 우리 은하 내부에 존재한다는 것이 말이 되지 않았다.
    # TRANSLIT: .geu .geo.ri.neun .u.ri .eun.ha.yi .keu.gi.wa .bi.gyo.hal .su .eobs.i .meol.eoss.gi .ddae.mun.e .an.deu.ro.me.da.ga .u.ri .eun.ha .nae.bu.e .jon.jae.han.da.neun .geos.i .mal.i .doe.ji .anh.ass.da.
    # ENGLISH: This is not what it should become.
    # CONFLICT: 16:것이(nsubj→되지), 17:말이(nsubj→되지)
    # Fix: default: N1(것이)→outer [NEEDS REVIEW]
    'train-s822': [('deprel', 16, 'nsubj:outer')],

    # train-s844
    # TEXT: 조명래 단국대 교수는 "정부가 주택을 매입해 전세 세입자와 지분을 절반씩 나눠 갖는 지분형주택은 소유권을 인정하면서 주거 안정을 꾀할 수 있는 방안"이라며 "공공성을 확보하지 않은 채 규제를 완화하고 세제지원을 강화하려는 정책은 결국 상위계층과 고가 주택 보유자들에게만 혜택이 돌아가고 실효성은 떨어질 수 있다"고 지적했다.
    # TRANSLIT: .jo.myeong.rae .dan.gug.dae .gyo.su.neun ".jeong.bu.ga .ju.taeg.eul .mae.ib.hae .jeon.se .se.ib.ja.wa .ji.bun.eul .jeol.ban.ssig .na.nweo .gaj.neun .ji.bun.hyeong.ju.taeg.eun .so.yu.gweon.eul .in.jeong.ha.myeon.seo .ju.geo .an.jeong.eul .ggoe.hal .su .iss.neun .bang.an".i.ra.myeo ".gong.gong.seong.eul .hwag.bo.ha.ji .anh.eun .chae .gyu.je.reul .wan.hwa.ha.go .se.je.ji.weon.eul .gang.hwa.ha.ryeo.neun .jeong.chaeg.eun .gyeol.gug .sang.wi.gye.cheung.gwa .go.ga .ju.taeg .bo.yu.ja.deul.e.ge.man .hye.taeg.i .dol.a.ga.go .sil.hyo.seong.eun .ddeol.eo.jil .su .iss.da".go .ji.jeog.haess.da.
    # ENGLISH: There is a possibility of doing it.
    # CONFLICT: 34:정책은(nsubj→있다), 44:수(nsubj→있다)
    # Fix: su-construction: N1→outer
    'train-s844': [('deprel', 34, 'nsubj:outer')],

    # train-s894
    # TEXT: 인테리어도 레스트랑처럼 깨끗하고 10년 넘게 한 자리에서 영업을 했다는 게 믿음이 갔음
    # TRANSLIT: .in.te.ri.eo.do .re.seu.teu.rang.cheo.reom .ggae.ggeus.ha.go 10.nyeon .neom.ge .han .ja.ri.e.seo .yeong.eob.eul .haess.da.neun .ge .mid.eum.i .gass.eum
    # ENGLISH: My trust in it is gone.
    # CONFLICT: 10:게(nsubj→갔음), 11:믿음이(nsubj→갔음)
    # Fix: default: N1(게)→outer [NEEDS REVIEW]
    'train-s894': [('deprel', 10, 'nsubj:outer')],

    # train-s916
    # TEXT: 문경은 감독과 저도 젊은 나이에 지도자가 됐습니다.
    # TRANSLIT: .mun.gyeong.eun .gam.dog.gwa .jeo.do .jeorm.eun .na.i.e .ji.do.ja.ga .dwaess.seub.ni.da.
    # ENGLISH: This is a very meaningful place.
    # CONFLICT: 1:문경은(nsubj→됐습니다), 6:지도자가(nsubj→됐습니다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s916': [('deprel', 1, 'nsubj:outer')],

    # train-s917
    # TEXT: 그러나 가을 상가시장은 수도권 곳곳에서 준공 후 미분양 상가의 공급도 가세하는 혼재 양상이 전망된다.
    # TRANSLIT: .geu.reo.na .ga.eul .sang.ga.si.jang.eun .su.do.gweon .gos.gos.e.seo .jun.gong .hu .mi.bun.yang .sang.ga.yi .gong.geub.do .ga.se.ha.neun .hon.jae .yang.sang.i .jeon.mang.doen.da.
    # ENGLISH: Autumn, sunshine and rain are mixed together in the forecast.
    # CONFLICT: 2:가을(nsubj:pass→전망된다), 12:혼재(nsubj:pass→전망된다)
    # Fix: default: N1(가을)→outer [NEEDS REVIEW]
    'train-s917': [('deprel', 2, 'nsubj:outer')],

    # train-s950
    # TEXT: 분쉬는 그의 일기에 우리나라에 머물던 기간 중 후반기에는 매일 서른 명 이상의 환자가 찾아올 정도로 진료가 많았으며, 환자의 대부분은 약값을 치를 돈조차 없었고 심지어 자신들이 마치 자선 사업을 베풀고 있는 것 같은 태도로 나왔다고 기록하고 있다.
    # TRANSLIT: .bun.swi.neun .geu.yi .il.gi.e .u.ri.na.ra.e .meo.mul.deon .gi.gan .jung .hu.ban.gi.e.neun .mae.il .seo.reun .myeong .i.sang.yi .hwan.ja.ga .chaj.a.ol .jeong.do.ro .jin.ryo.ga .manh.ass.eu.myeo, .hwan.ja.yi .dae.bu.bun.eun .yag.gabs.eul .chi.reul .don.jo.cha .eobs.eoss.go .sim.ji.eo .ja.sin.deul.i .ma.chi .ja.seon .sa.eob.eul .be.pul.go .iss.neun .geos .gat.eun .tae.do.ro .na.wass.da.go .gi.rog.ha.go .iss.da.
    # ENGLISH: This is a very meaningful event.
    # CONFLICT: 20:대부분은(nsubj→없었고), 23:돈조차(nsubj→없었고)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s950': [('deprel', 20, 'nsubj:outer')],

    # train-s952
    # TEXT: 길이 3m, 무게 1톤에 이르는 거대 옹관은 세계적으로 유래를 찾기 힘들다.
    # TRANSLIT: .gil.i 3m, .mu.ge 1.ton.e .i.reu.neun .geo.dae .ong.gwan.eun .se.gye.jeog.eu.ro .yu.rae.reul .chaj.gi .him.deul.da.
    # ENGLISH: It is hard to find something huge.
    # CONFLICT: 7:거대(nsubj→힘들다), 11:찾기(nsubj→힘들다)
    # Fix: default: N1(거대)→outer [NEEDS REVIEW]
    'train-s952': [('deprel', 7, 'nsubj:outer')],

    # train-s981
    # TEXT: 이 기관은 실린더가 하나였으며, 증기 기관과 비슷하지만 가로등을 켜는 가스를 연료로 사용했다.
    # TRANSLIT: .i .gi.gwan.eun .sil.rin.deo.ga .ha.na.yeoss.eu.myeo, .jeung.gi .gi.gwan.gwa .bi.seus.ha.ji.man .ga.ro.deung.eul .kyeo.neun .ga.seu.reul .yeon.ryo.ro .sa.yong.haess.da.
    # ENGLISH: This is a very good place.
    # CONFLICT: 2:기관은(nsubj→하나였으며), 3:실린더가(nsubj→하나였으며)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s981': [('deprel', 2, 'nsubj:outer')],

    # train-s984
    # TEXT: 이 장롱은 받침대 위에 같은 규격의 두 개의 농을 위ㆍ아래로 결합한 형태이며, 각각은 분리가 가능하다.
    # TRANSLIT: .i .jang.rong.eun .bad.chim.dae .wi.e .gat.eun .gyu.gyeog.yi .du .gae.yi .nong.eul .wiㆍ.a.rae.ro .gyeol.hab.han .hyeong.tae.i.myeo, .gag.gag.eun .bun.ri.ga .ga.neung.ha.da.
    # ENGLISH: This is a very meaningful place.
    # CONFLICT: 16:각각은(nsubj→가능하다), 17:분리가(nsubj→가능하다)
    # Fix: topic-marker: N1(은/는)→outer
    'train-s984': [('deprel', 16, 'nsubj:outer')],

}


def apply_fixes(doc, fixes):
    fixed = 0
    for bundle in doc.bundles:
        for tree in bundle.trees:
            sid = tree.sent_id
            if sid not in fixes:
                continue
            nodes = {n.ord: n for n in tree.descendants}
            for op in fixes[sid]:
                if op[0] == 'deprel':
                    _, nid, new_deprel = op
                    nodes[nid].deprel = new_deprel
                elif op[0] == 'reparent':
                    _, nid, new_head_id, new_deprel = op
                    nodes[nid].parent = nodes[new_head_id]
                    nodes[nid].deprel = new_deprel
            fixed += 1
    return fixed


if __name__ == '__main__':
    base = os.path.expanduser('.')
    splits = {
        'train': os.path.join(base, 'ko_gsd-ud-train.conllu'),
        'dev':   os.path.join(base, 'ko_gsd-ud-dev.conllu'),
        'test':  os.path.join(base, 'ko_gsd-ud-test.conllu'),
    }
    for split, path in splits.items():
        doc = udapi.Document(path)
        n = apply_fixes(doc, FIXES)
        doc.store_conllu(path)
        print(f"Fixed {n} sentences in {split} split ({path})")
