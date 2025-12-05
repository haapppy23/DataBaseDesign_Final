(천안 지역 기반 스터디 플랫폼)

> **"우리 동네에서 진짜 스터디원을 만나다."** > 관계형 데이터베이스(RDBMS)의 무결성 제약조건과 직관적인 SNS UI를 결합한 스터디 매칭 및 관리 시스템

---

## 프로젝트 개요
기존 대학생 커뮤니티(에브리타임)나 오픈채팅방의 **익명성(No-Show 문제)**과 **광범위한 지역 필터** 한계를 극복하기 위해 개발되었습니다.
**천안시 행정구역(30개 읍/면/동) 데이터**를 표준화하여 하이퍼 로컬 매칭을 지원하며, **스터디 그룹의 전 생애주기(모집-관리-기록)**를 체계적으로 관리합니다.

## 기술 스택 (Tech Stack)
* **Backend:** Python 3.13, Flask (Micro Framework)
* **Database:** MySQL 8.0 (PyMySQL Interface)
    * *ORM을 사용하지 않고 **Raw SQL**을 직접 작성하여 DB 제어*
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3
* **Tools:** Visual Studio Code, Git/GitHub

## 주요 기능 (Key Features)

### 1. 사용자 인증 및 지역 특화
* **Session 기반 로그인:** 보안성을 강화한 세션 관리.
* **지역 데이터 표준화:** 회원가입/그룹 생성 시 천안시 행정구역 드롭다운 제공.

### 2. 대시보드 & 동적 검색
* **Dynamic Query:** 검색어, 분야, 지역 조건에 따라 SQL `WHERE` 절 자동 생성.
* **UI/UX:** 인스타그램 피드 형태의 카드 레이아웃 및 3열 그리드 시스템.
* **Pagination & Sort:** 대용량 데이터 처리를 위한 페이징 및 다중 정렬 구현.

### 3. 그룹장 권한 관리 (Management)
* **승인 시스템:** 가입 신청(Pending) → 승인(Approved) 프로세스 구현.
* **트랜잭션 처리:** 멤버 강퇴(Delete), 방장 권한 위임(Update), 그룹 삭제(Cascade) 기능.

### 4. 마이페이지 & 학습 기록
* **Personalization:** 내가 만든 그룹과 참여 중인 그룹 분리 조회.
* **Study Logs:** 학습 내용(과목, 시간, 상세내용) 기록 및 스크롤 뷰 조회.

### 5. 슈퍼 관리자 모드 (Admin)
* **Monitoring:** 전체 회원 및 그룹 현황 테이블 뷰 조회.
* **Control:** 문제 발생 시 회원/그룹 강제 삭제 권한 (`admin@test.com` 전용).

---

## 설치 및 실행 방법 (How to Run)

**1. 레포지토리 클론**
```bash
git clone [https://github.com/본인아이디/Studygram.git](https://github.com/본인아이디/Studygram.git)
cd Studygram

-----------------------------------

## 라이브러리 설치 

pip install flask pymysql

-----------------------------------

## 데이터 베이스 세팅 

MySQL에서 study_group_db 생성 및 테이블/데이터 초기화.

database.sql 파일의 내용을 실행하면 스키마와 더미 데이터가 자동 생성됩니다.

-----------------------------------

## 테스트 계정 

원활한 시연을 위해 아래 계정을 사용할 수 있습니다. (모든 비밀번호: 1234)

역할,이메일,비고
슈퍼 관리자,admin@test.com,/admin 접속 가능
일반 방장,yjs@example.com,유재석 (다수 그룹 보유)
일반 멤버,iu@example.com,아이유

-----------------------------------

STUDY_GROUP/
├── app.py              # 메인 애플리케이션 (Controller)
├── static/             # 정적 파일 (CSS, Uploads)
├── templates/          # HTML 템플릿 (View)
└── database.sql        # DB 초기화 스크립트

-----------------------------------

Developer
김성현 (Team Leader): DB 설계 및 쿼리문 작성,쿼리 테스트용 테이블 데이터 생성 , Backend 구현, Frontend 통합 ,보고서 작성,  쿼리 테스트용 테이블 데이터 생성

강지수: DB설계, 요구사항 분석, UI 기획, 쿼리 생성 일반 사용자 , 발표자료제작 , 발표

김문일: DB설계 , 자료 조사 및 QA , 쿼리 생성 관리자 , 발표자료 제작 , 발표 

----------------------------------------------------------


