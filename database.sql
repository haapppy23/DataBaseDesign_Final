DROP DATABASE IF EXISTS study_group_db;
CREATE DATABASE study_group_db;
USE study_group_db;


CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    age INT,
    gender VARCHAR(10),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL DEFAULT '1234',
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subjects (
    subject VARCHAR(255) PRIMARY KEY
);

CREATE TABLE `groups` (
    group_id INT PRIMARY KEY AUTO_INCREMENT,
    gName VARCHAR(50) NOT NULL,
    subject VARCHAR(255),
    location VARCHAR(255),
    info TEXT,
    group_leader_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject) REFERENCES subjects(subject) ON DELETE SET NULL,
    FOREIGN KEY (group_leader_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE group_members (
    group_id INT,
    user_id INT,
    status ENUM('pending', 'approved') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES `groups`(group_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE posts (
    post_id INT PRIMARY KEY AUTO_INCREMENT,
    content TEXT,
    author_id INT,
    group_id INT,
    image_path VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (group_id) REFERENCES `groups`(group_id) ON DELETE CASCADE
);

CREATE TABLE comments (
    comment_id INT PRIMARY KEY AUTO_INCREMENT,
    post_id INT,
    content TEXT,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE study_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP DEFAULT NULL,
    minutes INT DEFAULT 0,
    subject VARCHAR(255),
    content TEXT,
    user_id INT,
    group_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES `groups`(group_id) ON DELETE SET NULL,
    FOREIGN KEY (subject) REFERENCES subjects(subject) ON DELETE SET NULL
);


INSERT INTO subjects (subject) VALUES 
('Network'), ('Database'), ('Python'), ('Java'), ('C_Lang'), 
('Algorithm'), ('Web'), ('OS'), ('AI'), ('Security'), 
('Toeic'), ('History');

INSERT INTO users (name, age, gender, email, password, location) VALUES 
('관리자', 99, 'M', 'admin@test.com', '1234', '본부'),
('유재석', 25, 'M', 'yjs@example.com', '1234', '신부동'),
('아이유', 23, 'F', 'iu@example.com', '1234', '두정동'),
('박명수', 26, 'M', 'pms@example.com', '1234', '불당동'),
('노홍철', 24, 'M', 'nhc@example.com', '1234', '쌍용동'),
('정형돈', 25, 'M', 'jhd@example.com', '1234', '성정동'),
('하동훈', 22, 'M', 'haha@example.com', '1234', '안서동'),
('김태호', 30, 'M', 'pd@example.com', '1234', '청당동'),
('길성준', 27, 'M', 'gil@example.com', '1234', '백석동'),
('전진', 24, 'M', 'jj@example.com', '1234', '신방동');

INSERT INTO `groups` (gName, subject, location, info, group_leader_id) VALUES 
('두정동 파이썬 기초반', 'Python', '두정동', '먹자골목 근처 스터디룸. 초보 환영.', 2),
('신부동 토익 900 목표', 'Toeic', '신부동', '터미널 앞 카페. 매일 단어시험.', 3),
('불당동 AI 논문 리뷰', 'AI', '불당동', '최신 논문 읽고 구현해보기.', 4),
('쌍용동 정보처리기사', 'Database', '쌍용동', '나사렛대 도서관. 필기/실기 같이 준비.', 2),
('안서동 알고리즘 PS', 'Algorithm', '안서동', '단대호수 보면서 백준 풀이.', 7),
('성정동 웹 풀스택', 'Web', '성정동', '리액트/노드 프로젝트 진행.', 6);

INSERT INTO group_members (group_id, user_id, status) VALUES 
(1, 2, 'approved'), (1, 3, 'approved'), (1, 5, 'pending'),
(2, 3, 'approved'), (2, 6, 'approved'), (2, 7, 'pending'),
(3, 4, 'approved'), (3, 9, 'approved'),
(4, 2, 'approved'), (4, 10, 'approved'),
(5, 7, 'approved'),
(6, 6, 'approved');

INSERT INTO posts (content, author_id, group_id, image_path) VALUES 
('다음주 모임 시간 변경합니다. 7시 -> 8시', 2, 1, NULL),
('파이썬 설치 다 하셨나요?', 3, 1, NULL),
('오늘 단어 시험 범위 어디까지인가요?', 6, 2, NULL),
('인공지능 모델 학습이 안 끝나요 ㅠㅠ', 9, 3, NULL);

INSERT INTO comments (post_id, content, user_id) VALUES 
(1, '넵 확인했습니다.', 3),
(2, '설치 완료했습니다!', 3),
(2, '저는 에러나요 ㅠㅠ', 5);

INSERT INTO study_logs (user_id, subject, minutes, content) VALUES 
(2, 'Python', 60, '리스트와 딕셔너리 기초'),
(2, 'Database', 120, '정규화 1,2,3단계 정리'),
(3, 'Toeic', 90, 'RC 파트 5 문제풀이'),
(4, 'AI', 180, 'CNN 모델 구조 파악'),
(2, 'Python', 45, '백준 브론즈 문제 풀이');